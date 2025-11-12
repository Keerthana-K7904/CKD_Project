from fastapi import APIRouter, HTTPException, Depends
from typing import List
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.models.patient import Patient, Medication, LabResult, Appointment
from app.core.database import get_db

router = APIRouter()

from typing import Optional

class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: str
    gender: str
    ehr_id: str
    ckd_stage: Optional[int] = None  # Optional - for unknown CKD status
    gfr: float
    creatinine: float
    blood_pressure: dict
    email: str
    phone: str

class PatientResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    date_of_birth: str
    gender: str
    ehr_id: str
    ckd_stage: Optional[int] = None  # Optional - for unknown CKD status
    gfr: float
    creatinine: float
    blood_pressure: dict
    email: str
    phone: str
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[PatientResponse])
async def get_all_patients(db: Session = Depends(get_db)):
    """
    Get all patients
    """
    patients = db.query(Patient).all()
    return patients

@router.post("/", response_model=PatientResponse)
async def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    """
    Create a new patient record
    """
    try:
        db_patient = Patient(**patient.dict())
        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)
        return db_patient
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Error creating patient: {str(e)}"
        )

@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """
    Get patient details by ID
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.get("/{patient_id}/medications")
async def get_patient_medications(patient_id: int, db: Session = Depends(get_db)):
    """
    Get patient's medications
    """
    medications = db.query(Medication).filter(Medication.patient_id == patient_id).all()
    return medications

@router.get("/{patient_id}/lab-results")
async def get_patient_lab_results(patient_id: int, db: Session = Depends(get_db)):
    """
    Get patient's lab results
    """
    lab_results = db.query(LabResult).filter(LabResult.patient_id == patient_id).all()
    return lab_results

@router.get("/{patient_id}/appointments")
async def get_patient_appointments(patient_id: int, db: Session = Depends(get_db)):
    """
    Get patient's appointments
    """
    appointments = db.query(Appointment).filter(Appointment.patient_id == patient_id).all()
    return appointments

@router.put("/{patient_id}")
async def update_patient(patient_id: int, patient: PatientCreate, db: Session = Depends(get_db)):
    """
    Update patient information
    """
    try:
        db_patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not db_patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        for key, value in patient.dict().items():
            setattr(db_patient, key, value)
        
        db.commit()
        db.refresh(db_patient)
        return db_patient
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Error updating patient: {str(e)}"
        ) 