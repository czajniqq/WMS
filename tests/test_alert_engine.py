from datetime import datetime
from backend.models import Alert, Agent
from backend.services.alert_engine import evaluate

def test_cpu_alert_generated(db_session):
    agent = Agent(hostname="cpu-test", ip_address="1.2.3.4", agent_version="1.0", registered_at=datetime.utcnow(), last_seen=datetime.utcnow())
    db_session.add(agent)
    db_session.commit()
    evaluate(db_session, agent.id, cpu_percent=95.0, ram_percent=10.0)
    alerts = db_session.query(Alert).filter(Alert.agent_id == agent.id, Alert.rule == "CPU_HIGH").all()
    assert len(alerts) == 1

def test_ram_alert_generated(db_session):
    agent = Agent(hostname="ram-test", ip_address="1.2.3.5", agent_version="1.0", registered_at=datetime.utcnow(), last_seen=datetime.utcnow())
    db_session.add(agent)
    db_session.commit()
    evaluate(db_session, agent.id, cpu_percent=10.0, ram_percent=95.0)
    alerts = db_session.query(Alert).filter(Alert.agent_id == agent.id, Alert.rule == "RAM_HIGH").all()
    assert len(alerts) == 1

def test_no_duplicate_alert(db_session):
    agent = Agent(hostname="dup-test", ip_address="1.2.3.6", agent_version="1.0", registered_at=datetime.utcnow(), last_seen=datetime.utcnow())
    db_session.add(agent)
    db_session.commit()
    evaluate(db_session, agent.id, cpu_percent=95.0, ram_percent=10.0)
    evaluate(db_session, agent.id, cpu_percent=95.0, ram_percent=10.0)
    alerts = db_session.query(Alert).filter(Alert.agent_id == agent.id, Alert.rule == "CPU_HIGH").all()
    assert len(alerts) == 1
