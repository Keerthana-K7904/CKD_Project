from fastapi import APIRouter, HTTPException
from typing import List, Dict
from pydantic import BaseModel
from app.ml.models.drug_interaction import DrugInteractionAnalyzer

router = APIRouter()

class MedicationRequest(BaseModel):
    patient_id: int
    medications: List[str]

class InteractionResponse(BaseModel):
    contraindications: List[Dict]
    warnings: List[Dict]
    precautions: List[Dict]
    summary: str

# Initialize analyzer
interaction_analyzer = DrugInteractionAnalyzer()

@router.post("/check-interactions", response_model=InteractionResponse)
async def check_medication_interactions(request: MedicationRequest):
    """
    Check for potential drug interactions
    """
    try:
        # Analyze interactions
        interactions = interaction_analyzer.analyze_interactions(request.medications)
        
        # Generate summary
        summary = interaction_analyzer.get_interaction_summary(interactions)
        
        return InteractionResponse(
            contraindications=interactions['contraindications'],
            warnings=interactions['warnings'],
            precautions=interactions['precautions'],
            summary=summary
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing interactions: {str(e)}"
        )

@router.post("/add-interaction")
async def add_interaction(medication1: str, medication2: str, interaction_type: str):
    """
    Add a new drug interaction to the knowledge base
    """
    try:
        interaction_analyzer.add_interaction(medication1, medication2, interaction_type)
        return {"message": "Interaction added successfully"}
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error adding interaction: {str(e)}"
        )

@router.get("/medication-adherence/{patient_id}")
async def get_medication_adherence(patient_id: int):
    """
    Get medication adherence metrics for a patient
    """
    try:
        # This would typically query the database for adherence data
        # For demonstration, returning dummy data
        return {
            "patient_id": patient_id,
            "overall_adherence": 0.85,
            "medications": [
                {
                    "name": "Medication A",
                    "adherence_rate": 0.9,
                    "missed_doses": 2
                },
                {
                    "name": "Medication B",
                    "adherence_rate": 0.8,
                    "missed_doses": 4
                }
            ]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting adherence data: {str(e)}"
        ) 