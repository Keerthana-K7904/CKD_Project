import streamlit as st
import requests

st.title("CKD Predictive Care System 🩺")

# Input form
age = st.number_input("Age", min_value=1, max_value=120, value=30)
bp = st.number_input("Blood Pressure", min_value=50.0, max_value=200.0, value=120.0)
sugar = st.number_input("Sugar", min_value=50.0, max_value=400.0, value=100.0)
creatinine = st.number_input("Creatinine", min_value=0.1, max_value=10.0, value=1.0)

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

if st.button("Predict"):
    try:
        payload = {
            "patient_id": 0,
            "features": {
                "age": age,
                "blood_pressure": bp,
                "sugar": sugar,
                "creatinine": creatinine
            }
        }
        response = requests.post(
            f"{API_BASE_URL}/predictions/predict-progression",
            json=payload,
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            st.success(f"Prediction: {data.get('prediction')}")
            st.info(f"Probability: {data.get('probability'):.2%}")
            st.write(f"Confidence: **{data.get('confidence', 'unknown').capitalize()}**")
        else:
            try:
                err = response.json()
                st.error(f"API Error {response.status_code}: {err.get('detail', 'Unknown error')}")
            except Exception:
                st.error(f"API Error {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
