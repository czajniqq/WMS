from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Agent, Log, Alert
from ..schemas import LogBatchRequest, LogResponse

router = APIRouter(prefix="/api/v1/agents", tags=["logs"])

@router.post("/{agent_id}/logs", status_code=status.HTTP_201_CREATED)
def submit_logs(agent_id: int, payload: LogBatchRequest, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    entries = []
    for e in payload.entries:
        entries.append(Log(
            agent_id=agent_id,
            event_time=e.event_time,
            level=e.level,
            source=e.source,
            event_id=e.event_id,
            message=e.message,
            received_at=datetime.utcnow(),
        ))
        
        # Generowanie alertów z logów ERROR i CRITICAL
        if e.level in ["ERROR", "CRITICAL"]:
            alert = Alert(
                agent_id=agent_id,
                rule=f"LOG_{e.level}",
                threshold=0.0,
                actual_value=0.0,
                status="ACTIVE",
                triggered_at=e.event_time
            )
            db.add(alert)
            
    db.bulk_save_objects(entries)
    db.commit()
    return {"saved": len(entries)}

@router.get("/{agent_id}/logs", response_model=List[LogResponse])
def get_logs(
    agent_id: int,
    level: Optional[str] = Query(None),
    from_time: Optional[datetime] = Query(None),
    to_time: Optional[datetime] = Query(None),
    limit: int = Query(100),
    db: Session = Depends(get_db),
):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    q = db.query(Log).filter(Log.agent_id == agent_id)
    if level:
        q = q.filter(Log.level == level)
    if from_time:
        q = q.filter(Log.event_time >= from_time)
    if to_time:
        q = q.filter(Log.event_time <= to_time)
    return q.order_by(Log.event_time.desc()).limit(limit).all()
