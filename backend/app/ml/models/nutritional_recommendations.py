import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

class NutritionalRecommender:
    def __init__(self):
        self.food_items = self._load_food_items()
        self.patient_preferences = {}
        self.tfidf = TfidfVectorizer(stop_words='english')
        
    def _load_food_items(self) -> pd.DataFrame:
        """Load food items with nutritional information"""
        # This would typically be loaded from a database
        return pd.DataFrame({
            'food_id': range(1, 6),
            'name': ['Salmon', 'Spinach', 'Quinoa', 'Blueberries', 'Almonds'],
            'protein': [22, 3, 4, 0.7, 6],
            'potassium': [628, 558, 172, 77, 200],
            'phosphorus': [216, 49, 152, 12, 137],
            'sodium': [59, 79, 7, 1, 1],
            'calories': [208, 23, 120, 57, 164],
            'category': ['protein', 'vegetable', 'grain', 'fruit', 'nuts']
        })
    
    def get_recommendations(self, patient_id: int, ckd_stage: int, 
                          restrictions: List[str] = None) -> List[Dict]:
        """
        Get personalized nutritional recommendations
        """
        # Filter food items based on CKD stage and restrictions
        filtered_foods = self._filter_foods(ckd_stage, restrictions)
        
        # Get content-based recommendations
        content_recs = self._get_content_based_recommendations(
            patient_id, filtered_foods
        )
        
        # Get collaborative recommendations if available
        collab_recs = self._get_collaborative_recommendations(
            patient_id, filtered_foods
        )
        
        # Combine and rank recommendations
        final_recs = self._combine_recommendations(
            content_recs, collab_recs, filtered_foods
        )
        
        return final_recs
    
    def _filter_foods(self, ckd_stage: int, restrictions: List[str]) -> pd.DataFrame:
        """Filter food items based on CKD stage and restrictions"""
        filtered = self.food_items.copy()
        
        # Apply CKD stage-specific restrictions
        if ckd_stage >= 3:
            filtered = filtered[filtered['potassium'] <= 200]
            filtered = filtered[filtered['phosphorus'] <= 100]
        
        if ckd_stage >= 4:
            filtered = filtered[filtered['protein'] <= 15]
        
        # Apply additional restrictions
        if restrictions:
            for restriction in restrictions:
                if restriction == 'low_sodium':
                    filtered = filtered[filtered['sodium'] <= 50]
                elif restriction == 'low_protein':
                    filtered = filtered[filtered['protein'] <= 10]
        
        return filtered
    
    def _get_content_based_recommendations(self, patient_id: int, 
                                         foods: pd.DataFrame) -> pd.Series:
        """Get content-based recommendations using TF-IDF"""
        # Create feature matrix
        features = foods[['protein', 'potassium', 'phosphorus', 'sodium', 'calories']]
        
        # Calculate similarity scores
        similarity_matrix = cosine_similarity(features)
        
        # Get patient preferences if available
        if patient_id in self.patient_preferences:
            preferred_foods = self.patient_preferences[patient_id]
            # Calculate weighted average of similarities
            scores = np.mean(similarity_matrix[preferred_foods], axis=0)
        else:
            # Default to balanced nutritional profile
            scores = np.ones(len(foods))
        
        return pd.Series(scores, index=foods.index)
    
    def _get_collaborative_recommendations(self, patient_id: int,
                                         foods: pd.DataFrame) -> pd.Series:
        """Get collaborative filtering recommendations"""
        # This would typically use a more sophisticated collaborative filtering algorithm
        # For simplicity, we're using a basic implementation
        if patient_id not in self.patient_preferences:
            return pd.Series(np.zeros(len(foods)), index=foods.index)
        
        # Calculate average ratings from similar patients
        # In a real implementation, this would use a proper collaborative filtering algorithm
        return pd.Series(np.random.random(len(foods)), index=foods.index)
    
    def _combine_recommendations(self, content_scores: pd.Series,
                               collab_scores: pd.Series,
                               foods: pd.DataFrame) -> List[Dict]:
        """Combine and rank recommendations"""
        # Combine scores with weights
        combined_scores = 0.7 * content_scores + 0.3 * collab_scores
        
        # Get top recommendations
        top_indices = combined_scores.nlargest(5).index
        recommendations = []
        
        for idx in top_indices:
            food = foods.loc[idx]
            recommendations.append({
                'food_id': food['food_id'],
                'name': food['name'],
                'nutritional_info': {
                    'protein': food['protein'],
                    'potassium': food['potassium'],
                    'phosphorus': food['phosphorus'],
                    'sodium': food['sodium'],
                    'calories': food['calories']
                },
                'category': food['category']
            })
        
        return recommendations
    
    def update_patient_preferences(self, patient_id: int, food_id: int, rating: float):
        """Update patient food preferences"""
        if patient_id not in self.patient_preferences:
            self.patient_preferences[patient_id] = {}
        self.patient_preferences[patient_id][food_id] = rating


