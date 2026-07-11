from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Alert
from ..schemas import AlertResponse

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])

@router.get("/", response_model=List[AlertResponse])
def get_all_alerts(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return (
        db.query(Alert)
        .order_by(Alert.triggered_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

@router.get("/active", response_model=List[AlertResponse])
def get_active_alerts(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return (
        db.query(Alert)
        .filter(Alert.status == "ACTIVE")
        .order_by(Alert.triggered_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

@router.put("/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    if alert.status == "RESOLVED":
        raise HTTPException(status_code=409, detail="Alert already resolved")
    alert.resolved_at = datetime.now(timezone.utc)
    alert.status = "RESOLVED"
    db.commit()
    db.refresh(alert)
    return alert
