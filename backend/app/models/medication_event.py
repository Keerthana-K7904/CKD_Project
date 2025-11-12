"""
Medication Event Model for tracking pill dispenser events
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class MedicationEvent(Base):
    """Records when medications are dispensed or taken"""
    __tablename__ = "medication_events"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    medication_id = Column(Integer, ForeignKey("medications.id"), nullable=True)
    medication_name = Column(String, nullable=False)
    
    event_type = Column(String, nullable=False)  # 'dispensed', 'taken', 'missed', 'refilled'
    event_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    device_id = Column(String, nullable=True)  # IoT device that reported this
    dosage = Column(String, nullable=True)
    
    confirmed = Column(Boolean, default=False)  # Patient confirmed they took it
    notes = Column(String, nullable=True)
    
    metadata = Column(JSON, nullable=True)  # Additional event metadata
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="medication_events")
    medication = relationship("Medication", back_populates="events")

