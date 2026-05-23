from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, BigInteger, ForeignKey, Index
from .database import Base

class Agent(Base):
    __tablename__ = "agents"
    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String, unique=True, index=True, nullable=False)
    ip_address = Column(String, nullable=False)
    agent_version = Column(String, nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="ONLINE")

class Metric(Base):
    __tablename__ = "metrics"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    collected_at = Column(DateTime, nullable=False)
    cpu_percent = Column(Float)
    ram_percent = Column(Float)
    ram_used_mb = Column(Float)
    ram_total_mb = Column(Float)
    net_bytes_sent = Column(BigInteger)
    net_bytes_recv = Column(BigInteger)
    uptime_seconds = Column(BigInteger)
    __table_args__ = (Index("ix_metrics_agent_collected", "agent_id", "collected_at"),)

class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    event_time = Column(DateTime, nullable=False)
    level = Column(String, index=True)
    source = Column(String)
    event_id = Column(Integer)
    message = Column(Text)
    received_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (Index("ix_logs_agent_event_time", "agent_id", "event_time"),)

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, index=True)
    triggered_at = Column(DateTime, default=datetime.utcnow)
    rule = Column(String, nullable=False)
    threshold = Column(Float)
    actual_value = Column(Float)
    resolved_at = Column(DateTime, nullable=True)
    status = Column(String, default="ACTIVE", index=True)
