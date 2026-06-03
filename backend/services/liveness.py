from datetime import datetime, timedelta, timezone
from ..models import Agent
from ..config import settings

def check_liveness(db):
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=settings.AGENT_OFFLINE_TIMEOUT_SECONDS)
    offline_agents = db.query(Agent).filter(
        Agent.last_seen < cutoff,
        Agent.status == "ONLINE",
    ).all()
    for agent in offline_agents:
        agent.status = "OFFLINE"

    online_agents = db.query(Agent).filter(
        Agent.last_seen >= cutoff,
        Agent.status == "OFFLINE",
    ).all()
    for agent in online_agents:
        agent.status = "ONLINE"

    db.commit()
