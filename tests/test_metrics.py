from datetime import datetime, timezone

METRIC_PAYLOAD = {
    "collected_at": datetime.now(timezone.utc).isoformat(),
    "cpu_percent": 50.0,
    "ram_percent": 60.0,
    "ram_used_mb": 4096.0,
    "ram_total_mb": 8192.0,
    "net_bytes_sent": 1000,
    "net_bytes_recv": 2000,
    "uptime_seconds": 3600,
}

def test_submit_metrics(client, sample_agent):
    resp = client.post(f"/api/v1/agents/{sample_agent.id}/metrics", json=METRIC_PAYLOAD)
    assert resp.status_code == 201
    assert resp.json()["cpu_percent"] == 50.0

def test_get_metrics(client, sample_agent):
    client.post(f"/api/v1/agents/{sample_agent.id}/metrics", json=METRIC_PAYLOAD)
    resp = client.get(f"/api/v1/agents/{sample_agent.id}/metrics")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1

def test_metrics_agent_not_found(client):
    resp = client.post("/api/v1/agents/9999/metrics", json=METRIC_PAYLOAD)
    assert resp.status_code == 404
