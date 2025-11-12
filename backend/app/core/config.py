from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "CKD Predictive Care System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "ckd_db"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    
    # ML Model settings
    ML_MODEL_PATH: str = "ml/models"
    TRAINING_DATA_PATH: str = "ml/data"
    
    # FHIR API settings
    FHIR_SERVER_URL: str = "https://fhir.example.com"
    FHIR_CLIENT_ID: Optional[str] = None
    FHIR_CLIENT_SECRET: Optional[str] = None
    FHIR_BEARER_TOKEN: Optional[str] = "demo-token"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()

# Construct database URI - Use SQLite for development
if not settings.SQLALCHEMY_DATABASE_URI:
    settings.SQLALCHEMY_DATABASE_URI = "sqlite:///./app/ckd.db" 