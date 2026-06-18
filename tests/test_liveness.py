from datetime import datetime, timedelta, timezone
from backend.models import Agent
from backend.services.liveness import check_liveness

def test_mark_offline(db_session):
    old_time = datetime.now(timezone.utc) - timedelta(seconds=400)
    agent = Agent(hostname="old-agent", ip_address="1.1.1.1", agent_version="1.0",
                  registered_at=old_time, last_seen=old_time, status="ONLINE")
    db_session.add(agent)
    db_session.commit()
    check_liveness(db_session)
    db_session.refresh(agent)
    assert agent.status == "OFFLINE"

def test_mark_online(db_session):
    recent_time = datetime.now(timezone.utc) - timedelta(seconds=10)
    agent = Agent(hostname="new-agent", ip_address="2.2.2.2", agent_version="1.0",
                  registered_at=recent_time, last_seen=recent_time, status="OFFLINE")
    db_session.add(agent)
    db_session.commit()
    check_liveness(db_session)
    db_session.refresh(agent)
    assert agent.status == "ONLINE"
