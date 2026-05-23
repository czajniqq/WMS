from ..models import Alert
from ..config import settings

def evaluate(db, agent_id: int, cpu_percent: float, ram_percent: float):
    if cpu_percent >= settings.CPU_ALERT_THRESHOLD:
        existing = db.query(Alert).filter(
            Alert.agent_id == agent_id,
            Alert.rule == "CPU_HIGH",
            Alert.status == "ACTIVE",
        ).first()
        if not existing:
            alert = Alert(
                agent_id=agent_id,
                rule="CPU_HIGH",
                threshold=settings.CPU_ALERT_THRESHOLD,
                actual_value=cpu_percent,
            )
            db.add(alert)

    if ram_percent >= settings.RAM_ALERT_THRESHOLD:
        existing = db.query(Alert).filter(
            Alert.agent_id == agent_id,
            Alert.rule == "RAM_HIGH",
            Alert.status == "ACTIVE",
        ).first()
        if not existing:
            alert = Alert(
                agent_id=agent_id,
                rule="RAM_HIGH",
                threshold=settings.RAM_ALERT_THRESHOLD,
                actual_value=ram_percent,
            )
            db.add(alert)

    db.commit()
