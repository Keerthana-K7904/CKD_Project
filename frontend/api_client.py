import requests
import streamlit as st
from typing import Dict, List, Optional, Any
import json

class APIClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000/api/v1"):
        self.base_url = base_url
        self.timeout = 30
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.request(method, url, timeout=self.timeout, **kwargs)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return {"error": "Resource not found"}
            elif response.status_code == 500:
                return {"error": "Server error"}
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
        except requests.exceptions.ConnectionError:
            return {"error": "Cannot connect to backend server"}
        except requests.exceptions.Timeout:
            return {"error": "Request timed out"}
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}
    
    # Patient Management
    def get_patient(self, patient_id: int) -> Dict[str, Any]:
        return self._make_request("GET", f"/patients/{patient_id}")
    
    def create_patient(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("POST", "/patients", json=patient_data)
    
    def update_patient(self, patient_id: int, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._make_request("PUT", f"/patients/{patient_id}", json=patient_data)
    
    def get_patient_medications(self, patient_id: int) -> List[Dict[str, Any]]:
        result = self._make_request("GET", f"/patients/{patient_id}/medications")
        return result if isinstance(result, list) else []
    
    def get_patient_lab_results(self, patient_id: int) -> List[Dict[str, Any]]:
        result = self._make_request("GET", f"/patients/{patient_id}/lab-results")
        return result if isinstance(result, list) else []
    
    def get_patient_appointments(self, patient_id: int) -> List[Dict[str, Any]]:
        result = self._make_request("GET", f"/patients/{patient_id}/appointments")
        return result if isinstance(result, list) else []
    
    # Predictions
    def predict_ckd_progression(self, patient_id: int, features: Dict[str, Any]) -> Dict[str, Any]:
        payload = {
            "patient_id": patient_id,
            "features": features
        }
        return self._make_request("POST", "/predictions/predict-progression", json=payload)
    
    def get_model_metrics(self) -> Dict[str, Any]:
        return self._make_request("GET", "/predictions/model-metrics")
    
    # Medications
    def check_drug_interactions(self, patient_id: int, medications: List[str]) -> Dict[str, Any]:
        payload = {
            "patient_id": patient_id,
            "medications": medications
        }
        return self._make_request("POST", "/medications/check-interactions", json=payload)
    
    def get_medication_adherence(self, patient_id: int) -> Dict[str, Any]:
        return self._make_request("GET", f"/medications/medication-adherence/{patient_id}")
    
    def add_drug_interaction(self, med1: str, med2: str, interaction_type: str) -> Dict[str, Any]:
        params = {
            "medication1": med1,
            "medication2": med2,
            "interaction_type": interaction_type
        }
        return self._make_request("POST", "/medications/add-interaction", params=params)
    
    # Nutrition
    def get_nutritional_recommendations(self, patient_id: int, ckd_stage: int, restrictions: Optional[List[str]] = None) -> Dict[str, Any]:
        payload = {
            "patient_id": patient_id,
            "ckd_stage": ckd_stage,
            "restrictions": restrictions or []
        }
        return self._make_request("POST", "/nutrition/recommendations", json=payload)
    
    def update_food_preferences(self, patient_id: int, food_id: int, rating: float) -> Dict[str, Any]:
        payload = {
            "patient_id": patient_id,
            "food_id": food_id,
            "rating": rating
        }
        return self._make_request("POST", "/nutrition/update-preferences", json=payload)

    # IoT
    def get_iot_devices(self, patient_id: int) -> List[Dict[str, Any]]:
        result = self._make_request("GET", f"/iot/patients/{patient_id}/devices")
        return result if isinstance(result, list) else []

    def get_iot_readings(self, patient_id: int, hours: int = 6, reading_type: Optional[str] = None) -> List[Dict[str, Any]]:
        params = {"hours": hours}
        if reading_type:
            params["reading_type"] = reading_type
        result = self._make_request("GET", f"/iot/patients/{patient_id}/readings", params=params)
        return result if isinstance(result, list) else []

    def get_iot_alerts(self, patient_id: int, unread_only: bool = False) -> List[Dict[str, Any]]:
        params = {"unread_only": unread_only}
        result = self._make_request("GET", f"/iot/patients/{patient_id}/alerts", params=params)
        return result if isinstance(result, list) else []
    
    def register_iot_device(
        self,
        patient_id: int,
        device_type: str,
        device_name: str,
        manufacturer: str,
        model: str,
        device_id: str,
        mac_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Register a new IoT device for a patient"""
        payload = {
            "patient_id": patient_id,
            "device_type": device_type,
            "device_name": device_name,
            "manufacturer": manufacturer,
            "model": model,
            "device_id": device_id
        }
        if mac_address:
            payload["mac_address"] = mac_address
        return self._make_request("POST", "/iot/devices", json=payload)

# Global API client instance
@st.cache_resource
def get_api_client():
    return APIClient()
