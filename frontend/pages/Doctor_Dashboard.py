import streamlit as st

st.set_page_config(page_title="Doctor Dashboard", page_icon="🩺", layout="wide")

import pandas as pd
from typing import Optional, Dict, Any
from api_client import get_api_client
from components.charts import (
    create_vitals_chart, create_lab_trends_chart, 
    create_medication_adherence_chart, create_prediction_confidence_chart
)
from components.forms import (
    patient_registration_form, prediction_input_form, 
    medication_form, lab_result_form, appointment_form,
    drug_interaction_form, iot_device_registration_form
)
from components.html_components import (
    medical_header, health_metric_card, patient_status_badge,
    loading_spinner, alert_banner, render_html_component,
    mobile_responsive_grid
)

def require_doctor():
    if "auth" not in st.session_state or not st.session_state.auth.get("is_authenticated") or st.session_state.auth.get("role") != "doctor":
        st.error("Unauthorized. Please login as a doctor in the main app.")
        st.stop()

require_doctor()

# Initialize API client
api_client = get_api_client()

try:
    render_html_component(medical_header("Doctor Dashboard", "Comprehensive patient management and AI-powered insights"))
except Exception as e:
    st.title("Doctor Dashboard 🩺")
    st.caption("Comprehensive patient management and AI-powered insights")

# Sidebar navigation
with st.sidebar:
    st.subheader("Patient Management")
    patient_id = st.number_input("Patient ID", min_value=1, value=1, step=1)
    load_patient = st.button("Load Patient", type="primary")
    
    st.markdown("---")
    st.subheader("Quick Actions")
    if st.button("Register New Patient"):
        st.session_state.show_registration = True
    if st.button("Check Drug Interactions"):
        st.session_state.show_interactions = True

# Main content tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Patient Overview",
    "Predictions",
    "Medications",
    "Lab Results",
    "Appointments",
    "IoT & Alerts"
])

# Patient Registration Modal
if st.session_state.get("show_registration", False):
    with st.expander("Register New Patient", expanded=True):
        patient_data = patient_registration_form()
        if patient_data:
            result = api_client.create_patient(patient_data)
            if "error" not in result:
                st.success("Patient registered successfully!")
                st.session_state.show_registration = False
                st.rerun()
            else:
                st.error(f"Registration failed: {result['error']}")

# Drug Interaction Checker
if st.session_state.get("show_interactions", False):
    with st.expander("Drug Interaction Checker", expanded=True):
        interaction_data = drug_interaction_form()
        if interaction_data:
            result = api_client.check_drug_interactions(st.session_state.get("patient_id", 1) or 1, interaction_data["medications"])
            if "error" not in result:
                st.subheader("Interaction Analysis")
                st.write(f"**Summary:** {result.get('summary', 'No summary available')}")
                
                if result.get('contraindications'):
                    st.error("**Contraindications:**")
                    for item in result['contraindications']:
                        if isinstance(item, dict):
                            st.write(f"- {item.get('medication1')} + {item.get('medication2')}: {item.get('interaction_type')}")
                        else:
                            st.write(f"- {item}")
                
                if result.get('warnings'):
                    st.warning("**Warnings:**")
                    for item in result['warnings']:
                        if isinstance(item, dict):
                            st.write(f"- {item.get('medication1')} + {item.get('medication2')}: {item.get('interaction_type')}")
                        else:
                            st.write(f"- {item}")
                
                if result.get('precautions'):
                    st.info("**Precautions:**")
                    for item in result['precautions']:
                        if isinstance(item, dict):
                            st.write(f"- {item.get('medication1')} + {item.get('medication2')}: {item.get('interaction_type')}")
                        else:
                            st.write(f"- {item}")
            else:
                st.error(f"Interaction check failed: {result['error']}")

# Load patient data
patient_data = None
# Auto-load if patient already in session, or if Load Patient clicked
should_load = load_patient or (st.session_state.get("patient_id") == patient_id and "patient_data" in st.session_state)

if should_load:
    if load_patient or "patient_data" not in st.session_state:  # Fetch fresh data
        with st.spinner("Loading patient profile..."):
            patient_data = api_client.get_patient(patient_id)
            if "error" in patient_data:
                st.error(f"Failed to load patient: {patient_data['error']}")
                patient_data = None
            else:
                st.session_state.patient_data = patient_data
                st.session_state.patient_id = patient_id
    else:  # Use cached patient data
        patient_data = st.session_state.get("patient_data")

if patient_data and "error" not in patient_data:
    # Tab 1: Patient Overview
    with tab1:
        st.subheader(f"Patient: {patient_data.get('first_name', '')} {patient_data.get('last_name', '')}")
        
        # Key metrics with custom HTML cards
        ckd_stage = patient_data.get("ckd_stage", 0)
        gfr = patient_data.get('gfr', 0)
        creatinine = patient_data.get('creatinine', 0)
        bp = patient_data.get('blood_pressure', {})
        
        # Determine status for each metric
        gfr_status = "normal" if gfr >= 60 else "warning" if gfr >= 30 else "critical"
        creatinine_status = "normal" if creatinine <= 1.2 else "warning" if creatinine <= 2.0 else "critical"
        bp_status = "normal" if bp.get('systolic', 0) <= 120 else "warning"
        
        try:
            metric_cards = [
                health_metric_card("CKD Stage", str(ckd_stage), "", f"Stage {ckd_stage}", "info"),
                health_metric_card("GFR", f"{gfr:.1f}", "ml/min/1.73m²", f"Kidney function", gfr_status),
                health_metric_card("Creatinine", f"{creatinine:.2f}", "mg/dL", f"Waste level", creatinine_status),
                health_metric_card("Blood Pressure", f"{bp.get('systolic', 0)}/{bp.get('diastolic', 0)}", "mmHg", f"Cardiovascular", bp_status)
            ]
            render_html_component(mobile_responsive_grid(metric_cards, 4))
        except Exception as e:
            # Fallback to standard Streamlit metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("CKD Stage", ckd_stage)
            with col2:
                st.metric("GFR", f"{gfr:.1f}")
            with col3:
                st.metric("Creatinine", f"{creatinine:.2f}")
            with col4:
                st.metric("Blood Pressure", f"{bp.get('systolic', 0)}/{bp.get('diastolic', 0)}")
        
        # Vitals chart
        st.plotly_chart(create_vitals_chart(patient_data), use_container_width=True)
        
        # Patient details
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Patient Information**")
            st.write(f"**EHR ID:** {patient_data.get('ehr_id', 'N/A')}")
            st.write(f"**Email:** {patient_data.get('email', 'N/A')}")
            st.write(f"**Phone:** {patient_data.get('phone', 'N/A')}")
        
        with col2:
            st.markdown("**Medical Information**")
            st.write(f"**Gender:** {patient_data.get('gender', 'N/A')}")
            st.write(f"**Date of Birth:** {patient_data.get('date_of_birth', 'N/A')}")

        # Edit patient form
        with st.expander("Edit Patient Details", expanded=False):
            with st.form("edit_patient_form", clear_on_submit=False):
                colA, colB, colC = st.columns(3)
                with colA:
                    new_email = st.text_input("Email", value=patient_data.get("email", ""))
                    new_phone = st.text_input("Phone", value=patient_data.get("phone", ""))
                with colB:
                    new_ckd_stage = st.number_input("CKD Stage", min_value=0, max_value=5, value=int(patient_data.get("ckd_stage", 0)))
                    new_gfr = st.number_input("GFR (ml/min/1.73m²)", min_value=0.0, value=float(patient_data.get("gfr", 0.0)))
                with colC:
                    new_creatinine = st.number_input("Creatinine (mg/dL)", min_value=0.0, value=float(patient_data.get("creatinine", 0.0)))
                    bp_dict = patient_data.get("blood_pressure", {}) or {}
                    new_sys = st.number_input("Systolic (mmHg)", min_value=0, value=int(bp_dict.get("systolic", 0)))
                    new_dia = st.number_input("Diastolic (mmHg)", min_value=0, value=int(bp_dict.get("diastolic", 0)))

                submitted = st.form_submit_button("Save Changes")
                if submitted:
                    update_payload = {
                        "first_name": patient_data.get("first_name"),
                        "last_name": patient_data.get("last_name"),
                        "date_of_birth": patient_data.get("date_of_birth"),
                        "gender": patient_data.get("gender"),
                        "ehr_id": patient_data.get("ehr_id"),
                        "email": new_email,
                        "phone": new_phone,
                        "ckd_stage": int(new_ckd_stage),
                        "gfr": float(new_gfr),
                        "creatinine": float(new_creatinine),
                        "blood_pressure": {"systolic": int(new_sys), "diastolic": int(new_dia)},
                    }
                    result = api_client.update_patient(patient_id, update_payload)
                    if "error" not in result:
                        st.success("✅ Patient updated successfully! Refreshing...")
                        st.session_state.patient_id = patient_id
                        st.rerun()
                    else:
                        st.error(f"Update failed: {result['error']}")

    # Tab 2: Predictions
    with tab2:
        st.subheader("CKD Progression Prediction")
        
        # Prediction form
        features = prediction_input_form(patient_data)
        
        if st.button("Run Prediction", type="primary"):
            with st.spinner("Analyzing..."):
                result = api_client.predict_ckd_progression(patient_id, features)
                
                if "error" not in result:
                    st.success("Prediction completed!")
                    
                    # Display results
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Prediction", result.get('prediction'))
                        st.metric("Probability", f"{result.get('probability', 0):.2%}")
                    with col2:
                        st.metric("Confidence", result.get('confidence', 'unknown').title())
                    
                    # Confidence chart
                    st.plotly_chart(create_prediction_confidence_chart(result), use_container_width=True)
                else:
                    st.error(f"Prediction failed: {result['error']}")

    # Tab 3: Medications
    with tab3:
        st.subheader("Medication Management")
        
        # Add medication form
        with st.expander("Add New Medication"):
            med_data = medication_form(patient_id)
            if med_data:
                # Note: This would need a POST endpoint for medications
                st.info("Medication addition would be implemented with proper backend endpoint")
        
        # Load medications
        with st.spinner("Loading medications..."):
            medications = api_client.get_patient_medications(patient_id)
        
        if medications:
            st.dataframe(pd.DataFrame(medications), use_container_width=True)
            
            # Adherence chart
            adherence_data = api_client.get_medication_adherence(patient_id)
            if "error" not in adherence_data:
                st.plotly_chart(create_medication_adherence_chart(adherence_data), use_container_width=True)
        else:
            st.info("No medications found for this patient")

    # Tab 4: Lab Results
    with tab4:
        st.subheader("Lab Results")
        
        # Add lab result form
        with st.expander("Add New Lab Result"):
            lab_data = lab_result_form(patient_id)
            if lab_data:
                # Note: This would need a POST endpoint for lab results
                st.info("Lab result addition would be implemented with proper backend endpoint")
        
        # Load lab results
        with st.spinner("Loading lab results..."):
            lab_results = api_client.get_patient_lab_results(patient_id)
        
        if lab_results:
            st.dataframe(pd.DataFrame(lab_results), use_container_width=True)
            st.plotly_chart(create_lab_trends_chart(lab_results), use_container_width=True)
        else:
            st.info("No lab results found for this patient")

    # Tab 5: Appointments
    with tab5:
        st.subheader("Appointments")
        
        # Add appointment form
        with st.expander("Schedule New Appointment"):
            appt_data = appointment_form(patient_id)
            if appt_data:
                # Note: This would need a POST endpoint for appointments
                st.info("Appointment scheduling would be implemented with proper backend endpoint")
        
        # Load appointments
        with st.spinner("Loading appointments..."):
            appointments = api_client.get_patient_appointments(patient_id)
        
        if appointments:
            st.dataframe(pd.DataFrame(appointments), use_container_width=True)
        else:
            st.info("No appointments found for this patient")

    # Tab 6: IoT & Alerts
    with tab6:
        st.subheader("IoT Devices & Remote Monitoring")
        st.caption("Register off-the-shelf clinic devices and monitor alerts without leaving the patient chart.")

        refresh_iot = st.button("Refresh IoT Data", key=f"refresh_iot_{patient_id}")
        with st.spinner("Loading IoT status..."):
            devices = api_client.get_iot_devices(patient_id)
            alerts = api_client.get_iot_alerts(patient_id, unread_only=False)
            recent_readings = api_client.get_iot_readings(patient_id, hours=24)
        if refresh_iot:
            st.rerun()

        summary_col1, summary_col2 = st.columns(2)
        with summary_col1:
            st.metric("Registered Devices", len(devices) if isinstance(devices, list) else 0)
        with summary_col2:
            st.metric("Active Alerts (24h)", len(alerts) if isinstance(alerts, list) else 0)

        st.markdown("#### Connected Devices")
        if isinstance(devices, dict) and devices.get("error"):
            st.error(devices["error"])
        elif not devices:
            st.info("No devices registered yet. Use the form below to onboard BP cuffs, glucometers, or heart-rate monitors used in the clinic.")
        else:
            device_df = pd.DataFrame(devices)
            show_cols = [
                c for c in ["device_name", "device_type", "device_id", "manufacturer", "model", "is_active", "last_sync"]
                if c in device_df.columns
            ]
            st.dataframe(device_df[show_cols], use_container_width=True)

        with st.expander("➕ Register IoT Device", expanded=not devices):
            st.markdown("Local teams can register a device in under a minute—just capture the serial number from the packaging and plug it in here.")
            device_payload = iot_device_registration_form(patient_id)
            if device_payload:
                result = api_client.register_iot_device(
                    patient_id=device_payload["patient_id"],
                    device_type=device_payload["device_type"],
                    device_name=device_payload["device_name"],
                    manufacturer=device_payload["manufacturer"],
                    model=device_payload["model"],
                    device_id=device_payload["device_id"],
                    mac_address=device_payload.get("mac_address")
                )
                if isinstance(result, dict) and result.get("error"):
                    st.error(f"Device registration failed: {result['error']}")
                else:
                    st.success("✅ Device registered! The monitoring feed will refresh automatically.")
                    st.rerun()

        st.markdown("#### Latest Alerts")
        if isinstance(alerts, dict) and alerts.get("error"):
            st.error(alerts["error"])
        elif not alerts:
            st.success("No active alerts for this patient.")
        else:
            alerts_df = pd.DataFrame(alerts)
            if "alert_timestamp" in alerts_df.columns:
                alerts_df["alert_timestamp"] = pd.to_datetime(alerts_df["alert_timestamp"], errors="coerce")
            show_alert_cols = [
                c for c in ["alert_timestamp", "severity", "alert_type", "alert_message"]
                if c in alerts_df.columns
            ]
            st.dataframe(
                alerts_df[show_alert_cols].sort_values(by="alert_timestamp", ascending=False),
                use_container_width=True,
                height=220
            )

        st.markdown("#### Recent Readings (last 24h)")
        if isinstance(recent_readings, dict) and recent_readings.get("error"):
            st.error(recent_readings["error"])
        elif not recent_readings:
            st.info("No readings received in the last 24 hours.")
        else:
            readings_df = pd.DataFrame(recent_readings)
            if "reading_timestamp" in readings_df.columns:
                readings_df["reading_timestamp"] = pd.to_datetime(readings_df["reading_timestamp"], errors="coerce")
            show_read_cols = [
                c for c in ["reading_timestamp", "device_name", "reading_type", "numeric_value", "unit", "quality", "alert_message"]
                if c in readings_df.columns
            ]
            st.dataframe(readings_df[show_read_cols], use_container_width=True, height=250)

        st.markdown("**Clinic Tip:** Pair each device with a patient once and reuse it—no need for special setup or IT support.")

else:
    st.info("Enter a Patient ID and click 'Load Patient' to view their information")
