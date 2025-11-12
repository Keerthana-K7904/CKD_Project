from fastapi import APIRouter, HTTPException, Depends, Query, Header
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.config import settings
from app.models.audit import AuditEvent
from app.models.patient import Patient, LabResult, Medication


router = APIRouter()


def require_bearer(authorization: str = Header(None)) -> str:
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:]
    if token != (settings.FHIR_BEARER_TOKEN or "demo-token"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return token or ""


# Minimal terminology mapping for demo (extend as needed)
LOINC_CODES: Dict[str, str] = {
    "creatinine": "2160-0",           # Creatinine [Mass/volume] in Serum or Plasma
    "gfr": "48643-1",                 # Glomerular filtration rate/1.73 sq M.predicted
    "systolic_bp": "8480-6",          # Systolic blood pressure
    "diastolic_bp": "8462-4",         # Diastolic blood pressure
    "glucose": "2339-0",              # Glucose [Mass/volume] in Blood
    "hba1c": "4548-4",                # Hemoglobin A1c/Hemoglobin.total in Blood
}


def to_fhir_patient(p: Patient) -> Dict[str, Any]:
    name_text = f"{p.first_name} {p.last_name}".strip()
    resource: Dict[str, Any] = {
        "resourceType": "Patient",
        "id": str(p.id),
        "identifier": [
            {"system": "urn:ehr:id", "value": p.ehr_id}
        ],
        "name": [
            {"use": "official", "text": name_text, "family": p.last_name, "given": [p.first_name]}
        ],
        "gender": p.gender.lower() if p.gender else None,
        "birthDate": p.date_of_birth,
        "telecom": [
            {"system": "phone", "value": p.phone, "use": "mobile"} if p.phone else None,
            {"system": "email", "value": p.email, "use": "home"} if p.email else None,
        ],
        "extension": [
            {
                "url": "urn:finpro:ckd:stage",
                "valueInteger": p.ckd_stage,
            }
        ],
        "meta": {"lastUpdated": (p.updated_at or p.created_at).isoformat() + "Z"},
    }
    # Remove Nones
    resource["telecom"] = [v for v in resource["telecom"] if v]
    return resource


def lab_to_observation(lab: LabResult, patient: Patient) -> Dict[str, Any]:
    code_text = lab.test_name
    loinc = None
    key = lab.test_name.strip().lower()
    if "creatinine" in key:
        loinc = LOINC_CODES["creatinine"]
    elif key in ("gfr", "egfr", "estimated gfr"):
        loinc = LOINC_CODES["gfr"]
    elif "glucose" in key:
        loinc = LOINC_CODES["glucose"]
    elif "hba1c" in key or "a1c" in key:
        loinc = LOINC_CODES["hba1c"]

    return {
        "resourceType": "Observation",
        "id": str(lab.id),
        "status": "final",
        "category": [{
            "coding": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "laboratory"}],
            "text": "laboratory",
        }],
        "code": {
            "coding": ([{"system": "http://loinc.org", "code": loinc, "display": code_text}] if loinc else []),
            "text": code_text,
        },
        "subject": {"reference": f"Patient/{patient.id}"},
        "effectiveDateTime": lab.date_taken,
        "valueQuantity": {
            "value": lab.result_value,
            "unit": lab.unit,
        },
        "meta": {"lastUpdated": (lab.updated_at or lab.created_at).isoformat() + "Z"},
    }


def bp_to_observations(patient: Patient) -> List[Dict[str, Any]]:
    obs: List[Dict[str, Any]] = []
    bp = patient.blood_pressure or {}
    for comp, loinc_key in [("systolic", "systolic_bp"), ("diastolic", "diastolic_bp")]:
        if comp in bp:
            obs.append({
                "resourceType": "Observation",
                "id": f"bp-{patient.id}-{comp}",
                "status": "final",
                "category": [{
                    "coding": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "vital-signs"}],
                    "text": "vital-signs",
                }],
                "code": {
                    "coding": [{"system": "http://loinc.org", "code": LOINC_CODES[loinc_key], "display": f"{comp.capitalize()} blood pressure"}],
                    "text": f"{comp.capitalize()} blood pressure",
                },
                "subject": {"reference": f"Patient/{patient.id}"},
                "effectiveDateTime": datetime.utcnow().isoformat() + "Z",
                "valueQuantity": {
                    "value": float(bp.get(comp)),
                    "unit": "mmHg",
                },
                "meta": {"lastUpdated": datetime.utcnow().isoformat() + "Z"},
            })
    return obs


@router.get("/Patient/{patient_id}")
def get_fhir_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    _bearer: str = Depends(require_bearer),
) -> Dict[str, Any]:
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    resource = to_fhir_patient(patient)
    # audit
    db.add(AuditEvent(route="/fhir/Patient", method="GET", subject_type="Patient", subject_id=str(patient_id)))
    db.commit()
    return resource


@router.get("/Observation")
def list_fhir_observations(
    patient: int = Query(..., description="Patient id"),
    db: Session = Depends(get_db),
    _bearer: str = Depends(require_bearer),
) -> Dict[str, Any]:
    """Return a FHIR Bundle of Observation resources for the given patient id."""
    p = db.query(Patient).filter(Patient.id == patient).first()
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")

    labs = db.query(LabResult).filter(LabResult.patient_id == p.id).all()
    entries: List[Dict[str, Any]] = []
    # BP vitals
    for ob in bp_to_observations(p):
        entries.append({"resource": ob})
    # Lab results
    for lab in labs:
        entries.append({"resource": lab_to_observation(lab, p)})

    bundle: Dict[str, Any] = {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": len(entries),
        "entry": entries,
    }
    db.add(AuditEvent(route="/fhir/Observation", method="GET", subject_type="Patient", subject_id=str(patient)))
    db.commit()
    return bundle



@router.get("/MedicationStatement")
def list_fhir_medication_statements(
    patient: int = Query(..., description="Patient id"),
    db: Session = Depends(get_db),
    _bearer: str = Depends(require_bearer),
) -> Dict[str, Any]:
    p = db.query(Patient).filter(Patient.id == patient).first()
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")

    meds = db.query(Medication).filter(Medication.patient_id == p.id).all()
    entries: List[Dict[str, Any]] = []
    RXNORM: Dict[str, str] = {
        "lisinopril": "29046",
        "metformin": "6809",
        "atorvastatin": "83367",
        "amlodipine": "17767",
    }
    for m in meds:
        rx = RXNORM.get((m.name or "").strip().lower())
        rxnorm_coding: List[Dict[str, Any]] = ([{"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": rx}] if rx else [])
        ms = {
            "resourceType": "MedicationStatement",
            "id": str(m.id),
            "status": "active",
            "medicationCodeableConcept": {
                "coding": rxnorm_coding,
                "text": m.name,
            },
            "subject": {"reference": f"Patient/{p.id}"},
            "effectivePeriod": {
                "start": m.start_date,
                **({"end": m.end_date} if m.end_date else {}),
            },
            "dosage": [{
                "text": f"{m.dosage} {m.frequency}",
            }],
            "meta": {"lastUpdated": (m.updated_at or m.created_at).isoformat() + "Z"},
        }
        entries.append({"resource": ms})

    db.add(AuditEvent(route="/fhir/MedicationStatement", method="GET", subject_type="Patient", subject_id=str(patient)))
    db.commit()
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": len(entries),
        "entry": entries,
    }


@router.get("/Condition")
def list_fhir_conditions(
    patient: int = Query(..., description="Patient id"),
    db: Session = Depends(get_db),
    _bearer: str = Depends(require_bearer),
) -> Dict[str, Any]:
    p = db.query(Patient).filter(Patient.id == patient).first()
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")

    ckd_stage = int(p.ckd_stage or 0)
    snomed_code = "709044004"  # illustrative CKD code
    icd10_code = f"N18.{max(0, min(ckd_stage, 9))}" if ckd_stage else "N18.9"

    condition = {
        "resourceType": "Condition",
        "id": f"ckd-{p.id}",
        "clinicalStatus": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-clinical", "code": "active"}]},
        "verificationStatus": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-ver-status", "code": "confirmed"}]},
        "category": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-category", "code": "problem-list-item"}]}],
        "code": {
            "coding": [
                {"system": "http://snomed.info/sct", "code": snomed_code, "display": "Chronic kidney disease"},
                {"system": "http://hl7.org/fhir/sid/icd-10", "code": icd10_code, "display": "Chronic kidney disease"},
            ],
            "text": f"CKD Stage {ckd_stage}" if ckd_stage else "Chronic kidney disease",
        },
        "subject": {"reference": f"Patient/{p.id}"},
        "onsetDateTime": p.created_at.isoformat() + "Z",
        "meta": {"lastUpdated": (p.updated_at or p.created_at).isoformat() + "Z"},
    }

    db.add(AuditEvent(route="/fhir/Condition", method="GET", subject_type="Patient", subject_id=str(patient)))
    db.commit()
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": 1,
        "entry": [{"resource": condition}],
    }


