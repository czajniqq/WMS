import configparser
import os
import time
import requests

_cfg = configparser.ConfigParser()
_cfg.read(os.path.join(os.path.dirname(__file__), "config.ini"))
MAX_RETRIES = int(_cfg.get("retry", "max_retries", fallback="3"))
BACKOFF = float(_cfg.get("retry", "backoff_seconds", fallback="5"))
_TLS_VERIFY = _cfg.getboolean("server", "tls_verify", fallback=True)
_API_KEY = _cfg.get("server", "api_key", fallback="")
_HEADERS = {"X-API-Key": _API_KEY} if _API_KEY else {}


def _post(url, data):
    last_exc = None
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.post(url, json=data, timeout=10, verify=_TLS_VERIFY, headers=_HEADERS)
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            last_exc = exc
            time.sleep(BACKOFF)
    raise RuntimeError(f"Failed after {MAX_RETRIES} attempts: {last_exc}") from last_exc


def _put(url):
    last_exc = None
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.put(url, timeout=10, verify=_TLS_VERIFY, headers=_HEADERS)
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            last_exc = exc
            time.sleep(BACKOFF)
    raise RuntimeError(f"Failed after {MAX_RETRIES} attempts: {last_exc}") from last_exc


def register(server_url: str, hostname: str, ip: str, version: str) -> int:
    data = {"hostname": hostname, "ip_address": ip, "agent_version": version}
    result = _post(f"{server_url}/api/v1/agents/register", data)
    return result["id"]


def heartbeat(server_url: str, agent_id: int) -> None:
    _post(f"{server_url}/api/v1/agents/{agent_id}/heartbeat", {})


def submit_metrics(server_url: str, agent_id: int, metrics: dict) -> dict:
    return _post(f"{server_url}/api/v1/agents/{agent_id}/metrics", metrics)


def submit_logs(server_url: str, agent_id: int, entries: list) -> dict:
    return _post(f"{server_url}/api/v1/agents/{agent_id}/logs", {"entries": entries})
