import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split

class CKDDataPreprocessor:
    def __init__(self):
        # Fitted artifacts
        self.scaler: StandardScaler = StandardScaler()
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self.numeric_medians: Dict[str, float] = {}

        # Schema tracking
        self.numerical_features: List[str] = []
        self.categorical_features: List[str] = []
        self.feature_columns: List[str] = []

    def preprocess_data(self, df: pd.DataFrame, target_column: str = 'ckd_stage_progression') -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """
        Fit transformers on training data, transform features, and return train/test splits.
        Also stores fitted artifacts for later inference.
        """
        df = df.copy()

        # Detect feature types
        self.categorical_features = df.select_dtypes(include=['object']).columns.tolist()
        self.numerical_features = df.select_dtypes(include=[np.number]).columns.tolist()

        # Ensure target is present
        if target_column not in df.columns:
            raise ValueError(f"Target column '{target_column}' not found in dataframe")

        # Compute and apply numeric medians
        for col in self.numerical_features:
            if col == target_column:
                continue
            median_value = float(df[col].median()) if not df[col].empty else 0.0
            self.numeric_medians[col] = median_value
            df[col] = df[col].fillna(median_value)

        # Fill missing categorical with mode and fit per-column encoders
        for col in self.categorical_features:
            mode_value = df[col].mode().iloc[0] if not df[col].mode().empty else ''
            df[col] = df[col].fillna(mode_value)
            encoder = LabelEncoder()
            df[col] = encoder.fit_transform(df[col].astype(str))
            self.label_encoders[col] = encoder

        # Scale numerical (excluding target)
        numerical_for_scaling = [c for c in self.numerical_features if c != target_column]
        if numerical_for_scaling:
            df[numerical_for_scaling] = self.scaler.fit_transform(df[numerical_for_scaling])

        # Define feature columns order
        self.feature_columns = [c for c in df.columns if c != target_column]

        # Split X/y and then train/test
        X = df[self.feature_columns]
        y = df[target_column]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        return X_train, X_test, y_train, y_test

    def transform_for_inference(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply stored transformers to an inference dataframe. Expects the same schema
        as training (missing columns will be added with NaN and handled).
        """
        if not self.feature_columns:
            raise RuntimeError("Preprocessor is not fitted. Load it or fit on training data first.")

        df = df.copy()

        # Ensure all expected columns are present
        for col in self.feature_columns:
            if col not in df.columns:
                df[col] = np.nan

        # Restrict to expected columns
        df = df[self.feature_columns]

        # Handle numeric columns
        for col in self.numerical_features:
            if col in df.columns:
                median_value = self.numeric_medians.get(col, 0.0)
                df[col] = df[col].astype(float).fillna(median_value)

        # Handle categorical columns with stored encoders
        for col in self.categorical_features:
            if col in df.columns:
                # Fill missing with placeholder seen during training if possible
                df[col] = df[col].astype(str).fillna('')
                encoder = self.label_encoders.get(col)
                if encoder is None:
                    # No encoder was fitted (edge case) – fall back to zeros
                    df[col] = 0
                else:
                    # Map using classes_, unseen -> -1
                    classes = list(encoder.classes_)
                    mapping = {label: idx for idx, label in enumerate(classes)}
                    df[col] = df[col].map(mapping).fillna(-1).astype(int)

        # Scale numerical features with fitted scaler
        numerical_for_scaling = [c for c in self.numerical_features if c in df.columns]
        if numerical_for_scaling:
            df[numerical_for_scaling] = self.scaler.transform(df[numerical_for_scaling])

        return df[self.feature_columns]

    def save_preprocessor(self, path: str):
        """Save the fitted preprocessor and schema for later use"""
        import joblib
        joblib.dump({
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'numeric_medians': self.numeric_medians,
            'numerical_features': self.numerical_features,
            'categorical_features': self.categorical_features,
            'feature_columns': self.feature_columns,
        }, path)

    def load_preprocessor(self, path: str):
        """Load a saved preprocessor"""
        import joblib
        preprocessor = joblib.load(path)
        self.scaler = preprocessor['scaler']
        self.label_encoders = preprocessor.get('label_encoders', {})
        self.numeric_medians = preprocessor.get('numeric_medians', {})
        self.numerical_features = preprocessor.get('numerical_features', [])
        self.categorical_features = preprocessor.get('categorical_features', [])
        self.feature_columns = preprocessor.get('feature_columns', [])


