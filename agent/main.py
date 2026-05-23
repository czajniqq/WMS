import configparser
import logging
import os
import socket
import time
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

AGENT_ID = None
_last_log_collection = datetime.utcnow() - timedelta(seconds=LOGS_INTERVAL)


def _get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def collect_and_send_metrics():
    global AGENT_ID
    try:
        data = collect_metrics()
        reporter.submit_metrics(SERVER_URL, AGENT_ID, data)
    except Exception as exc:
        logging.error("metrics error: %s", exc)


def collect_and_send_logs():
    global _last_log_collection
    try:
        since = _last_log_collection
        entries = read_event_log(since, MIN_LOG_LEVEL)
        if entries:
            reporter.submit_logs(SERVER_URL, AGENT_ID, entries)
        _last_log_collection = datetime.utcnow()
    except Exception as exc:
        logging.error("logs error: %s", exc)


def send_heartbeat():
    try:
        reporter.heartbeat(SERVER_URL, AGENT_ID)
    except Exception as exc:
        logging.error("heartbeat error: %s", exc)


def main():
    global AGENT_ID
    hostname = socket.gethostname()
    ip = _get_local_ip()

    for attempt in range(10):
        try:
            AGENT_ID = reporter.register(SERVER_URL, hostname, ip, AGENT_VERSION)
            break
        except Exception as exc:
            logging.error("registration attempt %d failed: %s", attempt + 1, exc)
            time.sleep(10)
    else:
        raise SystemExit("Could not register with backend after 10 attempts")

    schedule.every(HEARTBEAT_INTERVAL).seconds.do(send_heartbeat)
    schedule.every(METRICS_INTERVAL).seconds.do(collect_and_send_metrics)
    schedule.every(LOGS_INTERVAL).seconds.do(collect_and_send_logs)

    collect_and_send_metrics()

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
