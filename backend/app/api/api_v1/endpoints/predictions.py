from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from pydantic import BaseModel
import pandas as pd
import joblib
from pathlib import Path
from app.ml.models.ckd_progression import CKDProgressionModel
from app.ml.data.preprocessing import CKDDataPreprocessor

router = APIRouter()

class PredictionRequest(BaseModel):
    patient_id: int
    features: Dict[str, Any]

class PredictionResponse(BaseModel):
    prediction: int
    probability: float
    confidence: str

# Lazy-loaded artifacts for inference
progression_model = CKDProgressionModel()
preprocessor = CKDDataPreprocessor()
_artifacts_loaded = False

def _ensure_artifacts_loaded():
    global _artifacts_loaded
    if _artifacts_loaded:
        return
    try:
        # Resolve artifacts under backend/ml/models relative to this file
        # backend/app/api/api_v1/endpoints -> parents[3] == backend/app
        app_dir = Path(__file__).resolve().parents[3]
        models_dir = app_dir / 'ml' / 'models'
        preprocessor.load_preprocessor(str(models_dir / 'preprocessor.joblib'))
        progression_model.load_model(str(models_dir / 'progression_model.joblib'))
        _artifacts_loaded = True
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load ML artifacts: {str(e)}")

@router.post("/predict-progression", response_model=PredictionResponse)
async def predict_progression(request: PredictionRequest):
    """
    Predict CKD progression for a patient
    """
    try:
        _ensure_artifacts_loaded()

        # Build dataframe and apply inference transform
        features_df = pd.DataFrame([request.features])
        processed_features = preprocessor.transform_for_inference(features_df)

        # Make prediction
        prediction = int(progression_model.predict(processed_features)[0])
        proba = progression_model.predict_proba(processed_features)
        probability = float(proba[0][1]) if proba.shape[1] > 1 else float(proba[0][0])
        
        # Determine confidence level
        if probability >= 0.8:
            confidence = "high"
        elif probability >= 0.6:
            confidence = "medium"
        else:
            confidence = "low"
        
        return PredictionResponse(
            prediction=prediction,
            probability=probability,
            confidence=confidence
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error making prediction: {str(e)}"
        )

@router.get("/model-metrics")
async def get_model_metrics():
    """
    Get the current model's performance metrics
    """
    try:
        # This would typically load test data and evaluate the model
        # For demonstration, returning dummy metrics
        return {
            "accuracy": 0.85,
            "precision": 0.83,
            "recall": 0.87,
            "f1_score": 0.85
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting model metrics: {str(e)}"
        )