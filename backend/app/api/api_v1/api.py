from fastapi import APIRouter
from app.api.api_v1.endpoints import (
    patients,
    predictions,
    medications,
    nutrition,
    iot,
    fhir,
    medication_adherence,
)

api_router = APIRouter()

api_router.include_router(
    patients.router,
    prefix="/patients",
    tags=["patients"]
)

api_router.include_router(
    predictions.router,
    prefix="/predictions",
    tags=["predictions"]
)

api_router.include_router(
    medications.router,
    prefix="/medications",
    tags=["medications"]
)

api_router.include_router(
    nutrition.router,
    prefix="/nutrition",
    tags=["nutrition"]
)

api_router.include_router(
    iot.router,
    prefix="/iot",
    tags=["iot"]
) 

api_router.include_router(
    fhir.router,
    prefix="/fhir",
    tags=["fhir"]
)

api_router.include_router(
    medication_adherence.router,
    prefix="/adherence",
    tags=["adherence"]
)