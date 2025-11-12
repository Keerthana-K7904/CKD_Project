from sqlalchemy import Column, String, Float, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class Patient(BaseModel):
    __tablename__ = "patients"
    
    # Basic Information
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    date_of_birth = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    
    # Medical Information
    ehr_id = Column(String, unique=True, nullable=False)
    ckd_stage = Column(Integer, nullable=True)  # Optional - None for unknown/screening patients
    gfr = Column(Float, nullable=False)
    creatinine = Column(Float, nullable=False)
    blood_pressure = Column(JSON)  # Store as {"systolic": value, "diastolic": value}
    
    # Contact Information
    email = Column(String, unique=True)
    phone = Column(String)
    
    # Relationships
    medications = relationship("Medication", back_populates="patient")
    lab_results = relationship("LabResult", back_populates="patient")
    appointments = relationship("Appointment", back_populates="patient")

class Medication(BaseModel):
    __tablename__ = "medications"
    
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    name = Column(String, nullable=False)
    dosage = Column(String, nullable=False)
    frequency = Column(String, nullable=False)
    start_date = Column(String, nullable=False)
    end_date = Column(String)
    adherence_rate = Column(Float, default=0.0)
    
    patient = relationship("Patient", back_populates="medications")

class LabResult(BaseModel):
    __tablename__ = "lab_results"
    
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    test_name = Column(String, nullable=False)
    result_value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    reference_range = Column(String)
    date_taken = Column(String, nullable=False)
    
    patient = relationship("Patient", back_populates="lab_results")

class Appointment(BaseModel):
    __tablename__ = "appointments"
    
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    appointment_date = Column(String, nullable=False)
    appointment_type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    notes = Column(String)
    
    patient = relationship("Patient", back_populates="appointments") 