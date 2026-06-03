from datetime import datetime
from typing import Optional, List
import ipaddress
from pydantic import BaseModel, ConfigDict, Field, field_validator

class AgentRegisterRequest(BaseModel):
    hostname: str
    ip_address: str
    agent_version: str

    @field_validator("ip_address")
    @classmethod
    def validate_ip_address(cls, v: str) -> str:
        try:
            ipaddress.ip_address(v)
        except ValueError:
            raise ValueError(f"Invalid IP address: {v!r}")
        return v

class AgentRegisterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    hostname: str
    ip_address: str
    agent_version: str
    registered_at: datetime
    last_seen: Optional[datetime]
    status: str

class AgentListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    hostname: str
    ip_address: str
    agent_version: str
    registered_at: datetime
    last_seen: Optional[datetime]
    status: str

class MetricPayload(BaseModel):
    collected_at: datetime
    cpu_percent: float
    ram_percent: float
    ram_used_mb: float
    ram_total_mb: float
    net_bytes_sent: int
    net_bytes_recv: int
    uptime_seconds: int

class MetricResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    agent_id: int
    collected_at: datetime
    cpu_percent: float
    ram_percent: float
    ram_used_mb: float
    ram_total_mb: float
    net_bytes_sent: int
    net_bytes_recv: int
    uptime_seconds: int

class LogEntry(BaseModel):
    event_time: datetime
    level: str
    source: str
    event_id: int
    message: str

class LogBatchRequest(BaseModel):
    entries: List[LogEntry] = Field(..., max_length=500)

class LogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    agent_id: int
    event_time: datetime
    level: str
    source: str
    event_id: int
    message: str
    received_at: datetime

class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    agent_id: int
    triggered_at: datetime
    rule: str
    threshold: float
    actual_value: float
    resolved_at: Optional[datetime]
    status: str
