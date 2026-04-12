from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Agent, Metric
from ..schemas import MetricPayload, MetricResponse
from ..services.alert_engine import evaluate

router = APIRouter(prefix="/api/v1/agents", tags=["metrics"])

@router.post("/{agent_id}/metrics", response_model=MetricResponse, status_code=status.HTTP_201_CREATED)
def submit_metrics(agent_id: int, payload: MetricPayload, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    metric = Metric(
        agent_id=agent_id,
        collected_at=payload.collected_at,
        cpu_percent=payload.cpu_percent,
        ram_percent=payload.ram_percent,
        ram_used_mb=payload.ram_used_mb,
        ram_total_mb=payload.ram_total_mb,
        net_bytes_sent=payload.net_bytes_sent,
        net_bytes_recv=payload.net_bytes_recv,
        uptime_seconds=payload.uptime_seconds,
    )
    db.add(metric)
    agent.last_seen = datetime.utcnow()
    db.commit()
    db.refresh(metric)
    evaluate(db, agent_id, payload.cpu_percent, payload.ram_percent)
    return metric

@router.get("/{agent_id}/metrics", response_model=List[MetricResponse])
def get_metrics(
    agent_id: int,
    from_time: Optional[datetime] = Query(None),
    to_time: Optional[datetime] = Query(None),
    limit: int = Query(100),
    db: Session = Depends(get_db),
):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    q = db.query(Metric).filter(Metric.agent_id == agent_id)
    if from_time:
        q = q.filter(Metric.collected_at >= from_time)
    if to_time:
        q = q.filter(Metric.collected_at <= to_time)
    return q.order_by(Metric.collected_at.desc()).limit(limit).all()
