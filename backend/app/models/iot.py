from sqlalchemy import Column, String, Float, Integer, JSON, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import BaseModel

class SensorDevice(BaseModel):
    """IoT sensor devices registered in the system"""
    __tablename__ = "sensor_devices"
    
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    device_type = Column(String, nullable=False)  # 'blood_pressure', 'glucose', 'weight', 'activity', 'bp_monitor'
    device_name = Column(String, nullable=False)
    manufacturer = Column(String)
    model = Column(String)
    device_id = Column(String, unique=True, nullable=False)
    mac_address = Column(String)
    is_active = Column(Boolean, default=True)
    last_sync = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    readings = relationship("SensorReading", back_populates="device")

class SensorReading(BaseModel):
    """Real-time sensor readings from IoT devices"""
    __tablename__ = "sensor_readings"
    
    device_id = Column(Integer, ForeignKey("sensor_devices.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    reading_type = Column(String, nullable=False)  # 'blood_pressure', 'glucose', 'weight', 'heart_rate', etc.
    reading_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Reading data stored as flexible JSON
    reading_data = Column(JSON, nullable=False)  # {"value": 120, "unit": "mmHg", "quality": "good"}
    
    # Processed values for common metrics
    numeric_value = Column(Float)  # Extracted for queries
    unit = Column(String)
    quality = Column(String)  # 'good', 'warning', 'critical', 'invalid'
    
    # Alert status
    is_alert = Column(Boolean, default=False)
    alert_severity = Column(String)  # 'info', 'warning', 'critical'
    alert_message = Column(String)
    
    # Relationships
    device = relationship("SensorDevice", back_populates="readings")

class AlertLog(BaseModel):
    """Log of alerts generated from IoT sensor data"""
    __tablename__ = "alert_logs"
    
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    sensor_reading_id = Column(Integer, ForeignKey("sensor_readings.id"))
    alert_type = Column(String, nullable=False)  # 'critical_bp', 'high_glucose', 'low_gfr', etc.
    severity = Column(String, nullable=False)  # 'info', 'warning', 'critical'
    alert_message = Column(String, nullable=False)
    alert_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Status
    is_read = Column(Boolean, default=False)
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String)  # Doctor ID or system
    acknowledged_at = Column(DateTime)

class PatientMonitoringProfile(BaseModel):
    """Patient-specific monitoring settings and thresholds"""
    __tablename__ = "monitoring_profiles"
    
    patient_id = Column(Integer, ForeignKey("patients.id"), unique=True, nullable=False)
    
    # Monitoring settings
    is_monitoring_active = Column(Boolean, default=True)
    monitoring_frequency = Column(String, default='daily')  # 'real_time', 'hourly', 'daily'
    
    # Thresholds for alerts (JSON for flexibility)
    thresholds = Column(JSON, nullable=False, default={
        "blood_pressure": {"systolic_max": 140, "diastolic_max": 90, "systolic_min": 90, "diastolic_min": 60},
        "glucose": {"max": 140, "min": 70},
        "weight": {"change_percent_max": 5},
        "heart_rate": {"max": 100, "min": 60},
        "gfr": {"critical_min": 15}
    })
    
    # Notification preferences
    email_alerts = Column(Boolean, default=True)
    sms_alerts = Column(Boolean, default=False)
    push_notifications = Column(Boolean, default=True)

