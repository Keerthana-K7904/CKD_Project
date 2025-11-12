import streamlit as st
from typing import Dict, Any, Optional, List
import datetime

def patient_registration_form() -> Optional[Dict[str, Any]]:
    """Patient registration form"""
    st.subheader("Register New Patient")
    
    with st.form("patient_registration"):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name *", placeholder="John")
            last_name = st.text_input("Last Name *", placeholder="Doe")
            date_of_birth = st.date_input("Date of Birth *", value=datetime.date(1990, 1, 1))
            gender = st.selectbox("Gender *", options=["Male", "Female", "Other"])
            ehr_id = st.text_input("EHR ID *", placeholder="EHR123456")
        
        with col2:
            ckd_stage_unknown = st.checkbox("CKD Status Unknown (for screening)", value=False)
            if ckd_stage_unknown:
                ckd_stage = None
                st.info("💡 CKD stage will be determined after AI prediction")
            else:
                ckd_stage = st.selectbox("CKD Stage", options=[1, 2, 3, 4, 5])
            gfr = st.number_input("GFR (ml/min/1.73m²) *", min_value=0.0, max_value=200.0, value=90.0)
            creatinine = st.number_input("Creatinine (mg/dL) *", min_value=0.1, max_value=10.0, value=1.0)
            email = st.text_input("Email", placeholder="john.doe@example.com")
            phone = st.text_input("Phone", placeholder="+1-555-0123")
        
        st.subheader("Blood Pressure")
        bp_col1, bp_col2 = st.columns(2)
        with bp_col1:
            systolic = st.number_input("Systolic (mmHg)", min_value=50, max_value=250, value=120)
        with bp_col2:
            diastolic = st.number_input("Diastolic (mmHg)", min_value=30, max_value=150, value=80)
        
        blood_pressure = {"systolic": systolic, "diastolic": diastolic}
        
        submitted = st.form_submit_button("Register Patient", type="primary")
        
        if submitted:
            if not all([first_name, last_name, ehr_id]):
                st.error("Please fill in all required fields (*)")
                return None
            
            return {
                "first_name": first_name,
                "last_name": last_name,
                "date_of_birth": str(date_of_birth),
                "gender": gender,
                "ehr_id": ehr_id,
                "ckd_stage": ckd_stage,
                "gfr": gfr,
                "creatinine": creatinine,
                "blood_pressure": blood_pressure,
                "email": email,
                "phone": phone
            }
    
    return None

def prediction_input_form(patient_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """CKD progression prediction input form"""
    st.subheader("CKD Progression Prediction")
    
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.number_input("Age", min_value=1, max_value=120, value=40)
        blood_pressure = st.number_input("Blood Pressure (mmHg)", min_value=50.0, max_value=200.0, value=120.0)
    
    with col2:
        sugar = st.number_input("Blood Sugar (mg/dL)", min_value=50.0, max_value=400.0, value=100.0)
        creatinine = st.number_input("Creatinine (mg/dL)", min_value=0.1, max_value=10.0, value=1.0)
    
    # Pre-fill with patient data if available
    if patient_data:
        if st.checkbox("Use patient's current values"):
            age = 30  # Default age if not in patient data
            blood_pressure = patient_data.get('blood_pressure', {}).get('systolic', 120)
            creatinine = patient_data.get('creatinine', 1.0)
    
    return {
        "age": age,
        "blood_pressure": blood_pressure,
        "sugar": sugar,
        "creatinine": creatinine
    }

def medication_form(patient_id: int) -> Optional[Dict[str, Any]]:
    """Add medication form"""
    st.subheader("Add Medication")
    
    with st.form("add_medication"):
        name = st.text_input("Medication Name *", placeholder="Lisinopril")
        dosage = st.text_input("Dosage *", placeholder="10mg")
        frequency = st.selectbox("Frequency *", options=["Once daily", "Twice daily", "Three times daily", "As needed"])
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date *", value=datetime.date.today())
        with col2:
            end_date = st.date_input("End Date (optional)", value=None)
        
        adherence_rate = st.slider("Adherence Rate (%)", min_value=0, max_value=100, value=85)
        
        submitted = st.form_submit_button("Add Medication", type="primary")
        
        if submitted:
            if not all([name, dosage, frequency]):
                st.error("Please fill in all required fields (*)")
                return None
            
            return {
                "patient_id": patient_id,
                "name": name,
                "dosage": dosage,
                "frequency": frequency,
                "start_date": str(start_date),
                "end_date": str(end_date) if end_date else None,
                "adherence_rate": adherence_rate / 100.0
            }
    
    return None

def lab_result_form(patient_id: int) -> Optional[Dict[str, Any]]:
    """Add lab result form"""
    st.subheader("Add Lab Result")
    
    with st.form("add_lab_result"):
        test_name = st.selectbox("Test Name *", options=[
            "Creatinine", "GFR", "BUN", "Potassium", "Phosphorus", 
            "Hemoglobin", "Albumin", "Calcium", "Other"
        ])
        
        if test_name == "Other":
            test_name = st.text_input("Custom Test Name", placeholder="Custom test")
        
        col1, col2 = st.columns(2)
        with col1:
            result_value = st.number_input("Result Value *", min_value=0.0, value=1.0)
        with col2:
            unit = st.text_input("Unit *", placeholder="mg/dL")
        
        reference_range = st.text_input("Reference Range", placeholder="0.6-1.2 mg/dL")
        date_taken = st.date_input("Date Taken *", value=datetime.date.today())
        
        submitted = st.form_submit_button("Add Lab Result", type="primary")
        
        if submitted:
            if not all([test_name, unit]):
                st.error("Please fill in all required fields (*)")
                return None
            
            return {
                "patient_id": patient_id,
                "test_name": test_name,
                "result_value": result_value,
                "unit": unit,
                "reference_range": reference_range,
                "date_taken": str(date_taken)
            }
    
    return None

def appointment_form(patient_id: int) -> Optional[Dict[str, Any]]:
    """Add appointment form"""
    st.subheader("Schedule Appointment")
    
    with st.form("add_appointment"):
        appointment_type = st.selectbox("Appointment Type *", options=[
            "Routine Checkup", "Follow-up", "Consultation", "Lab Review", "Other"
        ])
        
        if appointment_type == "Other":
            appointment_type = st.text_input("Custom Type", placeholder="Custom appointment")
        
        col1, col2 = st.columns(2)
        with col1:
            appointment_date = st.date_input("Appointment Date *", value=datetime.date.today())
        with col2:
            status = st.selectbox("Status *", options=["Scheduled", "Confirmed", "Completed", "Cancelled"])
        
        notes = st.text_area("Notes", placeholder="Additional notes...")
        
        submitted = st.form_submit_button("Schedule Appointment", type="primary")
        
        if submitted:
            return {
                "patient_id": patient_id,
                "appointment_date": str(appointment_date),
                "appointment_type": appointment_type,
                "status": status,
                "notes": notes
            }
    
    return None

def drug_interaction_form() -> Optional[Dict[str, Any]]:
    """Drug interaction checker form"""
    st.subheader("Check Drug Interactions")
    
    medications = st.text_area(
        "Enter medications (one per line)",
        placeholder="Lisinopril\nMetformin\nAspirin",
        help="Enter each medication on a new line"
    )
    
    if st.button("Check Interactions", type="primary"):
        if not medications.strip():
            st.error("Please enter at least one medication")
            return None
        
        med_list = [med.strip() for med in medications.split('\n') if med.strip()]
        return {"medications": med_list}
    
    return None

def iot_device_registration_form(patient_id: int) -> Optional[Dict[str, Any]]:
    """Register a new IoT device for a patient"""
    with st.form(f"iot_device_registration_{patient_id}"):
        col1, col2 = st.columns(2)

        with col1:
            device_name = st.text_input(
                "Device Name *",
                placeholder="Clinic BP Monitor"
            )
            device_type = st.selectbox(
                "Device Type *",
                options=[
                    "blood_pressure",
                    "glucose",
                    "heart_rate",
                    "weight",
                    "oxygen",
                    "temperature"
                ]
            )
            device_id = st.text_input(
                "Device Serial / ID *",
                placeholder="CLINIC-BP-001"
            )

        with col2:
            manufacturer = st.text_input(
                "Manufacturer",
                placeholder="Generic Health Corp"
            )
            model = st.text_input(
                "Model",
                placeholder="Model 1000"
            )
            mac_address = st.text_input(
                "MAC Address (optional)",
                placeholder="AA:BB:CC:DD:EE:FF"
            )

        st.caption("Tip: Local clinics can use any off-the-shelf device. Just record the serial number and basic details.")

        submitted = st.form_submit_button("Register Device", type="primary")

        if submitted:
            if not device_name or not device_id:
                st.error("Please provide at least a device name and serial/ID.")
                return None

            return {
                "patient_id": patient_id,
                "device_type": device_type,
                "device_name": device_name,
                "manufacturer": manufacturer or "Unknown",
                "model": model or "Unknown",
                "device_id": device_id,
                "mac_address": mac_address or None
            }

    return None

def nutrition_preferences_form(patient_id: int) -> Optional[Dict[str, Any]]:
    """Nutrition preferences form"""
    st.subheader("Update Food Preferences")
    
    with st.form("nutrition_preferences"):
        food_id = st.number_input("Food ID", min_value=1, value=1)
        rating = st.slider("Rating (1-5 stars)", min_value=1, max_value=5, value=3)
        
        submitted = st.form_submit_button("Update Preference", type="primary")
        
        if submitted:
            return {
                "patient_id": patient_id,
                "food_id": food_id,
                "rating": float(rating)
            }
    
    return None
