import configparser
import logging
import os
import socket
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta

import schedule

from collector import collect_metrics
from event_log_reader import read_event_log
import reporter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cfg = configparser.ConfigParser()
cfg.read(os.path.join(BASE_DIR, "config.ini"))

SERVER_URL = cfg.get("server", "url", fallback="http://127.0.0.1:8000")
AGENT_VERSION = cfg.get("agent", "version", fallback="1.0.0")
METRICS_INTERVAL = int(cfg.get("intervals", "metrics_seconds", fallback="60"))
LOGS_INTERVAL = int(cfg.get("intervals", "logs_seconds", fallback="300"))
HEARTBEAT_INTERVAL = int(cfg.get("intervals", "heartbeat_seconds", fallback="120"))
MIN_LOG_LEVEL = cfg.get("thresholds", "min_log_level", fallback="WARNING")

logging.basicConfig(
    filename=os.path.join(BASE_DIR, "agent_errors.log"),
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s %(message)s",
)


@dataclass
class AgentState:
    agent_id: int
    last_log_collection: datetime = field(
        default_factory=lambda: datetime.utcnow() - timedelta(seconds=LOGS_INTERVAL)
    )


def _get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def collect_and_send_metrics(state: AgentState):
    try:
        data = collect_metrics()
        reporter.submit_metrics(SERVER_URL, state.agent_id, data)
    except Exception as exc:
        logging.error("metrics error: %s", exc)


def collect_and_send_logs(state: AgentState):
    try:
        since = state.last_log_collection
        entries = read_event_log(since, MIN_LOG_LEVEL)
        if entries:
            reporter.submit_logs(SERVER_URL, state.agent_id, entries)
        state.last_log_collection = datetime.utcnow()
    except Exception as exc:
        logging.error("logs error: %s", exc)


def send_heartbeat(state: AgentState):
    try:
        reporter.heartbeat(SERVER_URL, state.agent_id)
    except Exception as exc:
        logging.error("heartbeat error: %s", exc)


def main():
    hostname = socket.gethostname()
    ip = _get_local_ip()

    agent_id = None
    attempt = 0
    while True:
        attempt += 1
        try:
            agent_id = reporter.register(SERVER_URL, hostname, ip, AGENT_VERSION)
            break
        except Exception as exc:
            logging.error("registration attempt %d failed: %s", attempt, exc)
            wait = min(30 * attempt, 300)
            time.sleep(wait)

    state = AgentState(agent_id=agent_id)

    schedule.every(HEARTBEAT_INTERVAL).seconds.do(send_heartbeat, state)
    schedule.every(METRICS_INTERVAL).seconds.do(collect_and_send_metrics, state)
    schedule.every(LOGS_INTERVAL).seconds.do(collect_and_send_logs, state)

    collect_and_send_metrics(state)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

