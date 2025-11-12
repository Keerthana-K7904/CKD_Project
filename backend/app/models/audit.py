from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
from .base import BaseModel


class AuditEvent(BaseModel):
    __tablename__ = "audit_events"

    route = Column(String, nullable=False)
    method = Column(String, nullable=False)
    subject_type = Column(String, nullable=True)  # e.g., Patient, Observation
    subject_id = Column(String, nullable=True)
    actor = Column(String, nullable=True)  # token/client id if available
    details = Column(JSON, nullable=True)
    occurred_at = Column(DateTime, default=datetime.utcnow, nullable=False)


