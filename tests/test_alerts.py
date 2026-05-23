from datetime import datetime
from backend.models import Alert

def test_get_alerts_empty(client):
    resp = client.get("/api/v1/alerts/")
    assert resp.status_code == 200
    assert resp.json() == []

def test_get_active_alerts(client, db_session, sample_agent):
    alert = Alert(agent_id=sample_agent.id, rule="CPU_HIGH", threshold=90.0, actual_value=95.0, status="ACTIVE", triggered_at=datetime.utcnow())
    db_session.add(alert)
    db_session.commit()
    resp = client.get("/api/v1/alerts/active")
    assert resp.status_code == 200
    assert len(resp.json()) == 1

def test_resolve_alert(client, db_session, sample_agent):
    alert = Alert(agent_id=sample_agent.id, rule="RAM_HIGH", threshold=90.0, actual_value=92.0, status="ACTIVE", triggered_at=datetime.utcnow())
    db_session.add(alert)
    db_session.commit()
    resp = client.put(f"/api/v1/alerts/{alert.id}/resolve")
    assert resp.status_code == 200
    assert resp.json()["status"] == "RESOLVED"

def test_resolve_already_resolved(client, db_session, sample_agent):
    alert = Alert(agent_id=sample_agent.id, rule="CPU_HIGH", threshold=90.0, actual_value=95.0, status="RESOLVED", triggered_at=datetime.utcnow(), resolved_at=datetime.utcnow())
    db_session.add(alert)
    db_session.commit()
    resp = client.put(f"/api/v1/alerts/{alert.id}/resolve")
    assert resp.status_code == 409
