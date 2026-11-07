from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from backend.app.services.rule_engine import rule_engine

router = APIRouter(prefix="/rules", tags=["Dynamic Indian Tax Rules Engine"])

@router.get("/supported-years", response_model=List[str])
def get_supported_years():
    """
    Returns all dynamically loaded Assessment Years.
    Adding a new JSON file to backend/app/rules/ automatically registers a new AY.
    """
    return rule_engine.get_supported_years()

@router.get("/{assessment_year}")
def get_rules_for_year(assessment_year: str):
    """
    Returns the tax law parameters, slabs, rebate limits, and deduction rules
    for the requested Assessment Year.
    """
    try:
        return rule_engine.get_rules(assessment_year)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/reload")
def reload_rules():
    """
    Hot-reloads all tax rules from disk without restarting the application.
    """
    rule_engine.reload_rules()
    return {
        "status": "success",
        "supported_years": rule_engine.get_supported_years(),
        "message": "Tax rules reloaded dynamically."
    }

