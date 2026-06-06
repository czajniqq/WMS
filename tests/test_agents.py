def test_register_agent(client):
    resp = client.post("/api/v1/agents/register", json={
        "hostname": "host1", "ip_address": "10.0.0.1", "agent_version": "1.0.0"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["hostname"] == "host1"
    assert data["status"] == "ONLINE"

def test_register_duplicate(client):
    payload = {"hostname": "host2", "ip_address": "10.0.0.2", "agent_version": "1.0.0"}
    client.post("/api/v1/agents/register", json=payload)
    resp = client.post("/api/v1/agents/register", json=payload)
    assert resp.status_code == 200

def test_heartbeat(client, sample_agent):
    resp = client.post(f"/api/v1/agents/{sample_agent.id}/heartbeat")
    assert resp.status_code == 200

def test_heartbeat_not_found(client):
    resp = client.post("/api/v1/agents/9999/heartbeat")
    assert resp.status_code == 404

def test_list_agents(client, sample_agent):
    resp = client.get("/api/v1/agents/")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1
