from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class PortalFieldMapping(BaseModel):
    schedule_code: str  # e.g. "SCH_SALARY", "SCH_OS", "SCH_VIA", "SCH_TDS"
    schedule_name: str  # e.g. "Schedule Salary (Part B)"
    field_label: str    # e.g. "Salary as per Section 17(1)"
    portal_field_code: str  # e.g. "1(a)", "1(b)", "80C"
    amount: float
    source_document: str  # e.g. "Form 16 Part B, Line 1(a)"
    instructions: str

class PortalFilingStep(BaseModel):
    step_number: int
    title: str
    subtitle: str
    official_portal_screen: str
    critical_action: str
    fields: List[PortalFieldMapping] = []
    caution_notes: List[str] = []

class PortalFilingPlan(BaseModel):
    assessment_year: str = "2025-26"
    recommended_form: str = "ITR-1"
    form_title: str = "ITR-1 (Sahaj)"
    regime_choice: str = "NEW"  # "NEW" or "OLD"
    regime_portal_instruction: str
    
    total_gross_income: float
    total_taxable_income: float
    total_tax_liability: float
    total_tds_credit: float
    estimated_refund_or_due: float
    is_refund: bool
    
    steps: List[PortalFilingStep] = []
    pre_filing_checklist: List[str] = []
    e_verification_instructions: List[str] = []

