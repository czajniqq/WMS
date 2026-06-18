from datetime import datetime, timezone

LOG_BATCH = {
    "entries": [
        {"event_time": datetime.now(timezone.utc).isoformat(), "level": "WARNING", "source": "System", "event_id": 1001, "message": "Test warning"},
        {"event_time": datetime.now(timezone.utc).isoformat(), "level": "ERROR", "source": "Application", "event_id": 2001, "message": "Test error"},
    ]
}

def test_submit_logs(client, sample_agent):
    resp = client.post(f"/api/v1/agents/{sample_agent.id}/logs", json=LOG_BATCH)
    assert resp.status_code == 201
    assert resp.json()["saved"] == 2

def test_get_logs(client, sample_agent):
    client.post(f"/api/v1/agents/{sample_agent.id}/logs", json=LOG_BATCH)
    resp = client.get(f"/api/v1/agents/{sample_agent.id}/logs")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1

def test_logs_filter_level(client, sample_agent):
    client.post(f"/api/v1/agents/{sample_agent.id}/logs", json=LOG_BATCH)
    resp = client.get(f"/api/v1/agents/{sample_agent.id}/logs?level=ERROR")
    assert resp.status_code == 200
    data = resp.json()
    assert all(l["level"] == "ERROR" for l in data)
