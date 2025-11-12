from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional
from pydantic import BaseModel
from app.ml.models.nutritional_recommendations import NutritionalRecommender

router = APIRouter()

class NutritionRequest(BaseModel):
    patient_id: int
    ckd_stage: int
    restrictions: Optional[List[str]] = None

class FoodRecommendation(BaseModel):
    food_id: int
    name: str
    nutritional_info: Dict[str, float]
    category: str

class NutritionResponse(BaseModel):
    recommendations: List[FoodRecommendation]
    daily_nutritional_goals: Dict[str, float]

# Initialize recommender
nutrition_recommender = NutritionalRecommender()

@router.post("/recommendations", response_model=NutritionResponse)
async def get_nutritional_recommendations(request: NutritionRequest):
    """
    Get personalized nutritional recommendations
    """
    try:
        # Get food recommendations
        recommendations = nutrition_recommender.get_recommendations(
            request.patient_id,
            request.ckd_stage,
            request.restrictions
        )
        
        # Calculate daily nutritional goals based on CKD stage
        daily_goals = _calculate_daily_goals(request.ckd_stage)
        
        return NutritionResponse(
            recommendations=recommendations,
            daily_nutritional_goals=daily_goals
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting nutritional recommendations: {str(e)}"
        )

@router.post("/update-preferences")
async def update_food_preferences(patient_id: int, food_id: int, rating: float):
    """
    Update patient's food preferences
    """
    try:
        nutrition_recommender.update_patient_preferences(patient_id, food_id, rating)
        return {"message": "Preferences updated successfully"}
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating preferences: {str(e)}"
        )

def _calculate_daily_goals(ckd_stage: int) -> Dict[str, float]:
    """
    Calculate daily nutritional goals based on CKD stage
    """
    goals = {
        "protein": 0.8,  # g/kg body weight
        "potassium": 2000,  # mg
        "phosphorus": 800,  # mg
        "sodium": 2000,  # mg
        "calories": 2000  # kcal
    }
    
    # Adjust goals based on CKD stage
    if ckd_stage >= 3:
        goals["protein"] = 0.6
        goals["potassium"] = 1500
        goals["phosphorus"] = 600
    
    if ckd_stage >= 4:
        goals["protein"] = 0.55
        goals["potassium"] = 1000
        goals["phosphorus"] = 500
    
    return goals 