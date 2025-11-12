import streamlit as st

st.set_page_config(page_title="CKD Care Portal", page_icon="🩺", layout="wide")

from typing import Optional
from auth import verify_credentials, get_user_by_email
from styles import inject_global_styles
from api_client import get_api_client
from components.html_components import medical_header, alert_banner, render_html_component

# Initialize session state
if "auth" not in st.session_state:
    st.session_state.auth = {
        "is_authenticated": False,
        "role": None,            # 'doctor' or 'patient'
        "email": None,
        "patient_id": None       # only for patient role
    }

inject_global_styles()

# Sidebar navigation
with st.sidebar:
    st.title("🩺 CKD Care Portal")
    
    if st.session_state.auth["is_authenticated"]:
        st.success(f"Welcome, {st.session_state.auth['email']}")
        st.write(f"Role: {st.session_state.auth['role'].title()}")
        
        if st.button("Logout", type="secondary"):
            st.session_state.auth = {
                "is_authenticated": False,
                "role": None,
                "email": None,
                "patient_id": None
            }
            st.rerun()
    else:
        st.info("Please login to access the portal")

# Main content
try:
    render_html_component(medical_header("CKD Care Portal", "AI-Powered Chronic Kidney Disease Management System"))
except Exception as e:
    st.title("CKD Care Portal 🩺")
    st.caption("AI-Powered Chronic Kidney Disease Management System")

# If already authenticated, show dashboard
if st.session_state.auth["is_authenticated"]:
    role = st.session_state.auth["role"]
    if role == "doctor":
        st.success("Logged in as Doctor")
        try:
            st.switch_page("pages/Doctor_Dashboard.py")
        except Exception:
            st.write("Use the sidebar to navigate to the Doctor Dashboard.")
    elif role == "patient":
        st.success("Logged in as Patient")
        try:
            st.switch_page("pages/Patient_Dashboard.py")
        except Exception:
            st.write("Use the sidebar to navigate to the Patient Dashboard.")
else:
    # Login form
    st.subheader("Login to Access Your Dashboard")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        role = st.selectbox("Select role", options=["patient", "doctor"], index=0)
        email = st.text_input("Email", placeholder="you@example.com")
    with col2:
        password = st.text_input("Password", type="password")
        if role == "patient":
            patient_id: Optional[int] = st.number_input("Patient ID", min_value=1, value=1, step=1)
        else:
            patient_id = None

    if st.button("Sign in", type="primary"):
        user = get_user_by_email(email)
        if user and user["role"] == role and verify_credentials(email, password):
            st.session_state.auth = {
                "is_authenticated": True,
                "role": role,
                "email": email,
                "patient_id": int(patient_id) if patient_id is not None else None
            }
            try:
                render_html_component(alert_banner("Login successful! Redirecting...", "success"))
            except:
                st.success("Login successful! Redirecting...")
            st.rerun()
        else:
            try:
                render_html_component(alert_banner("Invalid credentials or role mismatch", "error"))
            except:
                st.error("Invalid credentials or role mismatch")

# Features overview
st.markdown("---")
st.subheader("System Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="color: #1a1a1a; font-weight: 600;">
    <p style="font-size: 18px; margin-bottom: 10px;">🔬 AI-Powered Predictions</p>
    <ul style="color: #2d2d2d; font-size: 15px;">
    <li>CKD progression analysis</li>
    <li>Risk assessment</li>
    <li>Personalized insights</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="color: #1a1a1a; font-weight: 600;">
    <p style="font-size: 18px; margin-bottom: 10px;">💊 Medication Management</p>
    <ul style="color: #2d2d2d; font-size: 15px;">
    <li>Drug interaction checking</li>
    <li>Adherence tracking</li>
    <li>Dosage optimization</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="color: #1a1a1a; font-weight: 600;">
    <p style="font-size: 18px; margin-bottom: 10px;">🥗 Nutritional Guidance</p>
    <ul style="color: #2d2d2d; font-size: 15px;">
    <li>CKD-specific recommendations</li>
    <li>Dietary restrictions</li>
    <li>Meal planning</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.caption("🔒 Secure • HIPAA Compliant • Real-time Data Sync")
