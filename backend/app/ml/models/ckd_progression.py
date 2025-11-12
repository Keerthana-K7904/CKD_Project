import numpy as np
import pandas as pd
from sklearn.ensemble import VotingClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib

try:
    from catboost import CatBoostClassifier  # type: ignore
    _HAS_CATBOOST = True
except Exception:  # ImportError and others
    CatBoostClassifier = None  # type: ignore
    _HAS_CATBOOST = False

class CKDProgressionModel:
    def __init__(self):
        self.models = {
            'xgb': XGBClassifier(
                n_estimators=300,
                learning_rate=0.05,
                max_depth=5,
                random_state=42
            ),
            'lgbm': LGBMClassifier(
                n_estimators=300,
                learning_rate=0.05,
                max_depth=5,
                random_state=42
            ),
        }
        if _HAS_CATBOOST:
            self.models['catboost'] = CatBoostClassifier(
                iterations=300,
                learning_rate=0.05,
                depth=5,
                random_state=42,
                verbose=False
            )
        
        estimators = [('xgb', self.models['xgb']), ('lgbm', self.models['lgbm'])]
        if 'catboost' in self.models:
            estimators.append(('catboost', self.models['catboost']))
        self.ensemble = VotingClassifier(estimators=estimators, voting='soft')
        
    def train(self, X_train: pd.DataFrame, y_train: pd.Series):
        """Train the ensemble model"""
        self.ensemble.fit(X_train, y_train)
        
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions using the ensemble model"""
        return self.ensemble.predict(X)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Get probability predictions"""
        return self.ensemble.predict_proba(X)
    
    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
        """Evaluate model performance"""
        y_pred = self.predict(X_test)
        
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='weighted'),
            'recall': recall_score(y_test, y_pred, average='weighted'),
            'f1': f1_score(y_test, y_pred, average='weighted')
        }
        
        return metrics
    
    def save_model(self, path: str):
        """Save the trained model"""
        joblib.dump(self.ensemble, path)
    
    def load_model(self, path: str):
        """Load a trained model"""
        self.ensemble = joblib.load(path)
    
    def get_feature_importance(self) -> pd.DataFrame:
        """Get feature importance from all models"""
        feature_importance = {}
        
        for name, model in self.models.items():
            if hasattr(model, 'feature_importances_'):
                feature_importance[name] = model.feature_importances_
            elif hasattr(model, 'get_feature_importance'):
                feature_importance[name] = model.get_feature_importance()
        
        return pd.DataFrame(feature_importance)


