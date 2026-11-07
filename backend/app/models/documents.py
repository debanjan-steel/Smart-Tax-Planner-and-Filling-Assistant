from typing import Optional, List, Dict
from pydantic import BaseModel, Field

class Form16SalaryBreakup(BaseModel):
    gross_salary_sec17_1: float = Field(default=0.0, description="Gross salary u/s 17(1)")
    perquisites_sec17_2: float = Field(default=0.0, description="Value of perquisites u/s 17(2)")
    profits_in_lieu_sec17_3: float = Field(default=0.0, description="Profits in lieu of salary u/s 17(3)")
    total_gross_salary: float = Field(default=0.0, description="Total gross salary before exemptions")
    
    # Exemptions u/s 10
    hra_exempt_sec10_13a: float = Field(default=0.0, description="House Rent Allowance exempt u/s 10(13A)")
    lta_exempt_sec10_5: float = Field(default=0.0, description="Leave Travel Assistance exempt u/s 10(5)")
    other_exemptions_sec10: float = Field(default=0.0, description="Other allowances exempt u/s 10")
    total_exemptions_sec10: float = Field(default=0.0, description="Total exemptions under Section 10")
    
    net_salary: float = Field(default=0.0, description="Salary after Section 10 exemptions")
    
    # Deductions u/s 16
    standard_deduction_sec16_ia: float = Field(default=50000.0, description="Standard deduction u/s 16(ia)")
    professional_tax_sec16_iii: float = Field(default=0.0, description="Tax on employment / Professional tax u/s 16(iii)")
    income_chargeable_salaries: float = Field(default=0.0, description="Income chargeable under head Salaries")

class Form16Deductions(BaseModel):
    section_80c: float = Field(default=0.0, description="EPF, PPF, ELSS, Life Insurance u/s 80C")
    section_80ccd_1b: float = Field(default=0.0, description="NPS employee contribution u/s 80CCD(1B)")
    section_80d_health_insurance: float = Field(default=0.0, description="Health Insurance premium u/s 80D")
    section_80e_education_loan: float = Field(default=0.0, description="Interest on education loan u/s 80E")
    section_80g_donations: float = Field(default=0.0, description="Donations to relief funds u/s 80G")
    section_80tta: float = Field(default=0.0, description="Interest on savings account u/s 80TTA")
    section_24b_house_loan_interest: float = Field(default=0.0, description="Loss/interest from house property u/s 24(b)")
    other_deductions: float = Field(default=0.0, description="Other Chapter VI-A deductions")
    total_chapter_via_deductions: float = Field(default=0.0, description="Total Chapter VI-A deductions allowable")

class Form16Parsed(BaseModel):
    employer_name: str = "Unknown Employer"
    employer_tan: str = "XXXX00000X"
    employer_pan: str = "XXXXX0000X"
    employee_pan: str = "XXXXX0000X"
    employee_name: Optional[str] = None
    assessment_year: str = "2025-26"
    financial_year: str = "2024-25"
    
    salary_breakup: Form16SalaryBreakup = Field(default_factory=Form16SalaryBreakup)
    deductions: Form16Deductions = Field(default_factory=Form16Deductions)
    
    gross_total_income: float = 0.0
    total_taxable_income: float = 0.0
    tax_on_total_income: float = 0.0
    rebate_87a: float = 0.0
    cess_4_percent: float = 0.0
    total_tax_payable: float = 0.0
    total_tds_deducted: float = 0.0
    
    confidence_score: float = 0.95
    extraction_notes: List[str] = []

class AISFinancialItem(BaseModel):
    category: str  # Savings Interest, FD Interest, Dividend, Securities Sale, etc.
    sft_code: Optional[str] = None
    description: str
    reported_by: str  # Bank / Depository / Company name
    amount: float
    tds_deducted: float = 0.0

class AISParsed(BaseModel):
    taxpayer_pan: str = "XXXXX0000X"
    taxpayer_name: Optional[str] = None
    assessment_year: str = "2025-26"
    
    total_savings_interest: float = 0.0
    total_fd_interest: float = 0.0
    total_dividend_income: float = 0.0
    total_securities_sale_turnover: float = 0.0
    total_tds_reported_ais: float = 0.0
    
    items: List[AISFinancialItem] = []
    high_value_transactions_count: int = 0
    extraction_notes: List[str] = []

class DiscrepancyNotice(BaseModel):
    severity: str  # WARNING, HIGH, INFO
    title: str
    message: str
    legal_impact: str
    recommended_action: str

class ReconciliationReport(BaseModel):
    form16_summary: Optional[Form16Parsed] = None
    ais_summary: Optional[AISParsed] = None
    total_estimated_gross_income: float = 0.0
    total_tds_available: float = 0.0
    discrepancies: List[DiscrepancyNotice] = []

