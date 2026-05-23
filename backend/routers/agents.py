from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Agent
from ..schemas import AgentRegisterRequest, AgentRegisterResponse, AgentListItem
from typing import List

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])

@router.post("/register", response_model=AgentRegisterResponse, status_code=status.HTTP_201_CREATED)
def register_agent(payload: AgentRegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(Agent).filter(Agent.hostname == payload.hostname).first()
    if existing:
        raise HTTPException(status_code=409, detail="Hostname already registered")
    agent = Agent(
        hostname=payload.hostname,
        ip_address=payload.ip_address,
        agent_version=payload.agent_version,
        registered_at=datetime.utcnow(),
        last_seen=datetime.utcnow(),
        status="ONLINE",
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent

@router.post("/{agent_id}/heartbeat", status_code=status.HTTP_200_OK)
def heartbeat(agent_id: int, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    agent.last_seen = datetime.utcnow()
    agent.status = "ONLINE"
    db.commit()
    return {"status": "ok"}

@router.get("/", response_model=List[AgentListItem])
def list_agents(db: Session = Depends(get_db)):
    return db.query(Agent).all()
