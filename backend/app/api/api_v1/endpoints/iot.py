from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.iot import SensorDevice, SensorReading, AlertLog, PatientMonitoringProfile
from app.models.patient import Patient

router = APIRouter()

# ============================================================
# Request/Response Models
# ============================================================

class SensorReadingCreate(BaseModel):
    device_id: str
    reading_type: str  # 'blood_pressure', 'glucose', 'weight', etc.
    reading_data: dict  # {"value": 120, "unit": "mmHg"}
    reading_timestamp: Optional[datetime] = None

class SensorReadingResponse(BaseModel):
    id: int
    device_name: str
    reading_type: str
    reading_timestamp: datetime
    numeric_value: float
    unit: str
    quality: str
    is_alert: bool
    alert_message: Optional[str] = None
    
    class Config:
        from_attributes = True

class AlertResponse(BaseModel):
    id: int
    patient_id: int
    alert_type: str
    severity: str
    alert_message: str
    alert_timestamp: datetime
    is_read: bool
    
    class Config:
        from_attributes = True

class DeviceRegistration(BaseModel):
    patient_id: int
    device_type: str
    device_name: str
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    device_id: str
    mac_address: Optional[str] = None

class DeviceResponse(BaseModel):
    id: int
    device_type: str
    device_name: str
    manufacturer: str
    model: str
    device_id: str
    is_active: bool
    last_sync: datetime
    
    class Config:
        from_attributes = True

# ============================================================
# Endpoints
# ============================================================

@router.post("/readings", response_model=SensorReadingResponse)
def create_sensor_reading(
    reading: SensorReadingCreate,
    db: Session = Depends(get_db)
):
    """
    **Ingest real-time sensor data from IoT devices**
    
    Accepts sensor readings from various IoT devices:
    - Blood pressure monitors
    - Glucose meters
    - Weight scales
    - Activity trackers
    - Custom devices
    """
    try:
        # Find device by device_id
        device = db.query(SensorDevice).filter(
            SensorDevice.device_id == reading.device_id
        ).first()
        
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        if not device.is_active:
            raise HTTPException(status_code=400, detail="Device is inactive")
        
        # Extract numeric value for querying
        numeric_value = None
        # Prefer a generic 'value' if provided
        if isinstance(reading.reading_data.get('value'), (int, float)):
            numeric_value = reading.reading_data['value']
        # Special handling for blood pressure payloads that may provide systolic/diastolic
        elif reading.reading_type == "blood_pressure":
            systolic = reading.reading_data.get('systolic')
            if isinstance(systolic, (int, float)):
                numeric_value = float(systolic)
        
        # Determine quality and alert status based on thresholds
        quality, is_alert, alert_severity, alert_message = _analyze_reading(
            reading.reading_type,
            numeric_value,
            device.patient_id,
            db
        )
        
        # Create reading record
        db_reading = SensorReading(
            device_id=device.id,
            patient_id=device.patient_id,
            reading_type=reading.reading_type,
            reading_timestamp=reading.reading_timestamp or datetime.utcnow(),
            reading_data=reading.reading_data,
            numeric_value=numeric_value,
            unit=reading.reading_data.get('unit') or ("mmHg" if reading.reading_type == "blood_pressure" else None),
            quality=quality,
            is_alert=is_alert,
            alert_severity=alert_severity,
            alert_message=alert_message
        )
        
        db.add(db_reading)
        
        # Create alert log if alert
        if is_alert:
            alert = AlertLog(
                patient_id=device.patient_id,
                sensor_reading_id=None,  # Will be set after flush
                alert_type=_get_alert_type(reading.reading_type, numeric_value),
                severity=alert_severity,
                alert_message=alert_message,
                alert_timestamp=datetime.utcnow()
            )
            db.add(alert)
        
        # Update device last sync
        device.last_sync = datetime.utcnow()
        
        db.commit()
        db.refresh(db_reading)
        
        return SensorReadingResponse(
            id=db_reading.id,
            device_name=device.device_name,
            reading_type=db_reading.reading_type,
            reading_timestamp=db_reading.reading_timestamp,
            numeric_value=db_reading.numeric_value,
            unit=db_reading.unit,
            quality=db_reading.quality,
            is_alert=db_reading.is_alert,
            alert_message=db_reading.alert_message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating reading: {str(e)}")

@router.get("/patients/{patient_id}/readings", response_model=List[SensorReadingResponse])
def get_patient_readings(
    patient_id: int,
    hours: int = 24,
    reading_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    **Get sensor readings for a patient**
    
    Returns readings from last N hours (default 24 hours)
    """
    since_time = datetime.utcnow() - timedelta(hours=hours)
    
    query = db.query(SensorReading).filter(
        SensorReading.patient_id == patient_id,
        SensorReading.reading_timestamp >= since_time
    )
    
    if reading_type:
        query = query.filter(SensorReading.reading_type == reading_type)
    
    readings = query.order_by(SensorReading.reading_timestamp.desc()).limit(1000).all()
    
    results = []
    for reading in readings:
        device = db.query(SensorDevice).filter(SensorDevice.id == reading.device_id).first()
        results.append(SensorReadingResponse(
            id=reading.id,
            device_name=device.device_name if device else "Unknown",
            reading_type=reading.reading_type,
            reading_timestamp=reading.reading_timestamp,
            numeric_value=reading.numeric_value,
            unit=reading.unit,
            quality=reading.quality,
            is_alert=reading.is_alert,
            alert_message=reading.alert_message
        ))
    
    return results

@router.get("/patients/{patient_id}/alerts", response_model=List[AlertResponse])
def get_patient_alerts(
    patient_id: int,
    unread_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    **Get active alerts for a patient**
    """
    query = db.query(AlertLog).filter(
        AlertLog.patient_id == patient_id
    )
    
    if unread_only:
        query = query.filter(AlertLog.is_read == False)
    
    alerts = query.order_by(AlertLog.alert_timestamp.desc()).limit(100).all()
    
    return alerts

@router.post("/devices", response_model=DeviceResponse)
def register_device(
    device: DeviceRegistration,
    db: Session = Depends(get_db)
):
    """
    **Register a new IoT device for a patient**
    """
    # Check if device already exists
    existing = db.query(SensorDevice).filter(
        SensorDevice.device_id == device.device_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Device already registered")
    
    # Check patient exists
    patient = db.query(Patient).filter(Patient.id == device.patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Create device
    db_device = SensorDevice(
        patient_id=device.patient_id,
        device_type=device.device_type,
        device_name=device.device_name,
        manufacturer=device.manufacturer,
        model=device.model,
        device_id=device.device_id,
        mac_address=device.mac_address,
        is_active=True,
        last_sync=datetime.utcnow()
    )
    
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    
    return DeviceResponse(
        id=db_device.id,
        device_type=db_device.device_type,
        device_name=db_device.device_name,
        manufacturer=db_device.manufacturer or "",
        model=db_device.model or "",
        device_id=db_device.device_id,
        is_active=db_device.is_active,
        last_sync=db_device.last_sync
    )

@router.get("/patients/{patient_id}/devices", response_model=List[DeviceResponse])
def get_patient_devices(
    patient_id: int,
    db: Session = Depends(get_db)
):
    """
    **Get all devices for a patient**
    """
    devices = db.query(SensorDevice).filter(
        SensorDevice.patient_id == patient_id
    ).all()
    
    return [
        DeviceResponse(
            id=d.id,
            device_type=d.device_type,
            device_name=d.device_name,
            manufacturer=d.manufacturer or "",
            model=d.model or "",
            device_id=d.device_id,
            is_active=d.is_active,
            last_sync=d.last_sync
        )
        for d in devices
    ]

# ============================================================
# Helper Functions
# ============================================================

def _analyze_reading(reading_type: str, value: float, patient_id: int, db: Session):
    """Analyze reading against thresholds and return quality/alert info"""
    # Get patient monitoring profile
    profile = db.query(PatientMonitoringProfile).filter(
        PatientMonitoringProfile.patient_id == patient_id
    ).first()
    
    if not profile:
        # Use default thresholds
        thresholds = {
            "blood_pressure": {"systolic_max": 140, "diastolic_max": 90},
            "glucose": {"max": 140, "min": 70},
            "weight": {"change_percent_max": 5},
            "heart_rate": {"max": 100, "min": 60}
        }
    else:
        thresholds = profile.thresholds
    
    quality = "good"
    is_alert = False
    severity = None
    message = None
    
    if reading_type == "blood_pressure" and value:
        # For BP, we might receive systolic value
        if value > thresholds.get("blood_pressure", {}).get("systolic_max", 140):
            quality = "warning"
            is_alert = True
            severity = "warning"
            message = f"High blood pressure detected: {value} mmHg"
    
    elif reading_type == "glucose" and value:
        if value > thresholds.get("glucose", {}).get("max", 140):
            quality = "critical"
            is_alert = True
            severity = "critical"
            message = f"High glucose level: {value} mg/dL"
        elif value < thresholds.get("glucose", {}).get("min", 70):
            quality = "critical"
            is_alert = True
            severity = "critical"
            message = f"Low glucose level: {value} mg/dL"
    
    elif reading_type == "heart_rate" and value:
        if value > thresholds.get("heart_rate", {}).get("max", 100):
            quality = "warning"
            is_alert = True
            severity = "warning"
            message = f"High heart rate: {value} bpm"
        elif value < thresholds.get("heart_rate", {}).get("min", 60):
            quality = "warning"
            is_alert = True
            severity = "warning"
            message = f"Low heart rate: {value} bpm"
    
    return quality, is_alert, severity, message

def _get_alert_type(reading_type: str, value: float) -> str:
    """Generate alert type string"""
    if reading_type == "blood_pressure":
        if value and value > 140:
            return "high_bp"
    elif reading_type == "glucose":
        if value and value > 140:
            return "high_glucose"
        elif value and value < 70:
            return "low_glucose"
    elif reading_type == "heart_rate":
        if value and value > 100:
            return "high_heart_rate"
        elif value and value < 60:
            return "low_heart_rate"
    
    return f"general_{reading_type}"

