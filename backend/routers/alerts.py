from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Alert
from ..schemas import AlertResponse

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])

@router.get("/", response_model=List[AlertResponse])
def get_all_alerts(db: Session = Depends(get_db)):
    return db.query(Alert).order_by(Alert.triggered_at.desc()).all()

@router.get("/active", response_model=List[AlertResponse])
def get_active_alerts(db: Session = Depends(get_db)):
    return db.query(Alert).filter(Alert.status == "ACTIVE").order_by(Alert.triggered_at.desc()).all()

@router.put("/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    if alert.status == "RESOLVED":
        raise HTTPException(status_code=409, detail="Alert already resolved")
    alert.resolved_at = datetime.utcnow()
    alert.status = "RESOLVED"
    db.commit()
    db.refresh(alert)
    return alert
