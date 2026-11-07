from typing import Optional, List, Dict
from pydantic import BaseModel, Field

class TaxCalculationInput(BaseModel):
    assessment_year: str = Field(default="2025-26", description="Assessment Year, e.g. 2025-26")
    
    # Incomes
    gross_salary: float = Field(default=0.0, description="Gross salary u/s 17(1) + 17(2) + 17(3)")
    savings_interest: float = Field(default=0.0, description="Savings bank interest income")
    fd_interest: float = Field(default=0.0, description="Fixed deposit / term deposit interest")
    dividend_income: float = Field(default=0.0, description="Dividend income")
    other_income: float = Field(default=0.0, description="Any other income from other sources")
    
    # Exemptions u/s 10 (Old Regime only)
    hra_exemption: float = Field(default=0.0, description="HRA exempt u/s 10(13A)")
    lta_exemption: float = Field(default=0.0, description="LTA exempt u/s 10(5)")
    professional_tax: float = Field(default=0.0, description="Professional Tax / Tax on employment u/s 16(iii)")
    
    # Chapter VI-A & Other Deductions (Old Regime only)
    deduction_80c: float = Field(default=0.0, description="Section 80C (EPF, PPF, ELSS, LIC, tuition fees, max 1.5L)")
    deduction_80ccd_1b: float = Field(default=0.0, description="Section 80CCD(1B) additional NPS (max 50k)")
    deduction_80d: float = Field(default=0.0, description="Section 80D Mediclaim / Health insurance")
    home_loan_interest_24b: float = Field(default=0.0, description="Home loan interest u/s 24(b) for self-occupied (max 2L)")
    deduction_80e: float = Field(default=0.0, description="Education loan interest u/s 80E")
    deduction_80g: float = Field(default=0.0, description="Eligible donations u/s 80G")
    
    # Taxes Already Paid
    tds_already_paid: float = Field(default=0.0, description="TDS deducted from Form 16 / AIS / 26AS")
    advance_tax_paid: float = Field(default=0.0, description="Advance tax or self-assessment tax paid")

class SlabBreakdown(BaseModel):
    slab_range: str
    taxable_amount_in_slab: float
    tax_rate: float
    tax_computed: float

class RegimeTaxResult(BaseModel):
    regime_name: str  # "New Tax Regime (Sec 115BAC)" or "Old Tax Regime"
    is_default: bool
    gross_total_income: float
    standard_deduction: float
    total_exemptions_and_deductions: float
    net_taxable_income: float
    
    slab_breakdown: List[SlabBreakdown] = []
    tax_before_rebate: float
    rebate_87a: float
    tax_after_rebate: float
    surcharge: float
    cess_4_percent: float
    total_tax_liability: float
    
    total_taxes_paid: float
    net_tax_payable: float  # Positive if tax due
    refund_due: float       # Positive if refund due

class TaxOptimizationComparison(BaseModel):
    assessment_year: str
    recommended_regime: str  # "NEW" or "OLD"
    recommended_regime_title: str
    tax_savings_amount: float
    summary_verdict: str
    
    new_regime: RegimeTaxResult
    old_regime: RegimeTaxResult
    
    breakeven_deductions_needed: float
    current_old_regime_deductions: float
    deduction_gap_to_beat_new_regime: float
    key_recommendations: List[str]

