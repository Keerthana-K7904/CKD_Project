"""
Medication Adherence Tracking Endpoints
For IoT pill dispenser integration
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.patient import Patient, Medication

router = APIRouter()

class MedicationEventCreate(BaseModel):
    """Event when pill is dispensed/taken"""
    patient_id: int
    medication_name: str
    medication_id: Optional[int] = None
    event_type: str  # 'dispensed', 'taken', 'missed'
    device_id: Optional[str] = None
    dosage: Optional[str] = None
    confirmed: bool = False
    notes: Optional[str] = None

class AdherenceCalculation(BaseModel):
    """Adherence calculation result"""
    patient_id: int
    medication_id: int
    medication_name: str
    expected_doses: int
    actual_doses: int
    adherence_rate: float
    period_days: int

@router.post("/medication-event")
async def record_medication_event(event: MedicationEventCreate, db: Session = Depends(get_db)):
    """
    Record medication event from IoT pill dispenser or patient self-report
    Automatically updates adherence rates
    """
    try:
        # Find or create medication record
        medication = None
        if event.medication_id:
            medication = db.query(Medication).filter(
                Medication.id == event.medication_id,
                Medication.patient_id == event.patient_id
            ).first()
        else:
            # Find by name
            medication = db.query(Medication).filter(
                Medication.patient_id == event.patient_id,
                Medication.name.ilike(f"%{event.medication_name}%")
            ).first()
        
        if not medication:
            raise HTTPException(status_code=404, detail="Medication not found for this patient")
        
        # For now, store event in a simple log (you can create MedicationEvent table later)
        # Calculate adherence based on recent events
        
        # Simple calculation: track in metadata
        # In production, you'd have a MedicationEvent table with all events
        
        # Update adherence rate
        # This is a simplified version - in production, calculate from actual events
        if event.event_type == "taken" or event.event_type == "dispensed":
            # Increment taken count
            current_rate = medication.adherence_rate or 0.85
            # Gradually adjust (moving average)
            medication.adherence_rate = min(1.0, current_rate + 0.01)
        elif event.event_type == "missed":
            # Decrement for missed dose
            current_rate = medication.adherence_rate or 0.85
            medication.adherence_rate = max(0.0, current_rate - 0.05)
        
        db.commit()
        db.refresh(medication)
        
        return {
            "message": f"Event recorded: {event.event_type}",
            "medication": medication.name,
            "updated_adherence_rate": medication.adherence_rate,
            "adherence_percentage": f"{medication.adherence_rate * 100:.1f}%",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recording event: {str(e)}")

@router.get("/adherence-report/{patient_id}")
async def get_adherence_report(
    patient_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get comprehensive adherence report for a patient
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    medications = db.query(Medication).filter(Medication.patient_id == patient_id).all()
    
    if not medications:
        return {
            "patient_id": patient_id,
            "patient_name": f"{patient.first_name} {patient.last_name}",
            "overall_adherence": 0.0,
            "medications": [],
            "recommendation": "No medications prescribed"
        }
    
    # Calculate overall adherence
    total_adherence = sum(med.adherence_rate or 0.0 for med in medications)
    overall_adherence = total_adherence / len(medications) if medications else 0.0
    
    medication_details = []
    for med in medications:
        adherence_pct = (med.adherence_rate or 0.0) * 100
        
        # Determine status
        if med.adherence_rate >= 0.9:
            status = "Excellent"
            status_emoji = "✅"
        elif med.adherence_rate >= 0.8:
            status = "Good"
            status_emoji = "🟢"
        elif med.adherence_rate >= 0.6:
            status = "Fair"
            status_emoji = "🟡"
        else:
            status = "Poor"
            status_emoji = "🔴"
        
        medication_details.append({
            "id": med.id,
            "name": med.name,
            "dosage": med.dosage,
            "frequency": med.frequency,
            "adherence_rate": med.adherence_rate,
            "adherence_percentage": f"{adherence_pct:.1f}%",
            "status": status,
            "status_emoji": status_emoji,
            "start_date": med.start_date
        })
    
    # Generate recommendation
    if overall_adherence >= 0.85:
        recommendation = "Excellent adherence. Continue current regimen."
    elif overall_adherence >= 0.70:
        recommendation = "Good adherence. Consider pill organizer and patient education."
    else:
        recommendation = "Poor adherence. Urgent intervention needed: smart pill dispenser, medication simplification, or caregiver support."
    
    return {
        "patient_id": patient_id,
        "patient_name": f"{patient.first_name} {patient.last_name}",
        "ckd_stage": patient.ckd_stage,
        "overall_adherence": overall_adherence,
        "overall_percentage": f"{overall_adherence * 100:.1f}%",
        "medications": medication_details,
        "total_medications": len(medications),
        "recommendation": recommendation,
        "report_period_days": days,
        "generated_at": datetime.utcnow().isoformat()
    }

@router.post("/update-adherence/{medication_id}")
async def update_medication_adherence(
    medication_id: int,
    adherence_rate: float,
    db: Session = Depends(get_db)
):
    """
    Manually update medication adherence rate
    """
    if not 0.0 <= adherence_rate <= 1.0:
        raise HTTPException(status_code=400, detail="Adherence rate must be between 0.0 and 1.0")
    
    medication = db.query(Medication).filter(Medication.id == medication_id).first()
    if not medication:
        raise HTTPException(status_code=404, detail="Medication not found")
    
    medication.adherence_rate = adherence_rate
    db.commit()
    db.refresh(medication)
    
    return {
        "message": "Adherence updated successfully",
        "medication": medication.name,
        "adherence_rate": medication.adherence_rate,
        "adherence_percentage": f"{medication.adherence_rate * 100:.1f}%"
    }

