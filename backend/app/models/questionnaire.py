from typing import Optional, List
from pydantic import BaseModel, Field

class TaxpayerProfile(BaseModel):
    assessment_year: str = Field(default="2025-26", description="Assessment Year, e.g. 2025-26")
    is_resident: bool = Field(default=True, description="Is the taxpayer a resident of India for tax purposes?")
    total_income_exceeds_50_lakh: bool = Field(default=False, description="Is total income greater than ₹50 Lakh?")
    
    # Income Sources
    has_salary_or_pension: bool = Field(default=True, description="Income from salary or pension?")
    house_property_count: int = Field(default=1, description="Number of house properties owned (0, 1, or >1)")
    has_capital_gains: bool = Field(default=False, description="Sold stocks, mutual funds, gold, crypto, or real estate?")
    has_crypto_or_vda: bool = Field(default=False, description="Profits/transactions in Virtual Digital Assets (Crypto, NFTs)?")
    
    # Business / Profession
    has_business_or_profession: bool = Field(default=False, description="Income from business, freelancing, or consultancy?")
    is_presumptive_eligible: bool = Field(default=False, description="Eligible and opting for Presumptive Taxation (Sec 44AD, 44ADA, 44AE)?")
    has_fo_or_intraday: bool = Field(default=False, description="Traded in Futures & Options (F&O) or intraday equity?")
    
    # Special Exclusions / Mandatory Disqualifiers
    is_company_director: bool = Field(default=False, description="Director in any Indian or foreign company?")
    holds_unlisted_shares: bool = Field(default=False, description="Held unlisted equity shares at any time during the FY?")
    has_foreign_assets_or_income: bool = Field(default=False, description="Foreign bank accounts, foreign ESOPs, or foreign income?")
    agricultural_income_exceeds_5000: bool = Field(default=False, description="Agricultural income exceeds ₹5,000?")
    has_brought_forward_losses: bool = Field(default=False, description="Brought forward loss from past years or loss to carry forward?")

class DocumentRequirement(BaseModel):
    id: str
    name: str
    description: str
    source: str
    download_steps: List[str]
    mandatory: bool = True
    applicable_reasons: List[str]

class FormDiagnosisResponse(BaseModel):
    recommended_form: str  # ITR-1, ITR-2, ITR-3, ITR-4
    form_title: str
    summary_verdict: str
    primary_reasons: List[str]
    disqualifications: List[str]
    compliance_risks: List[str]
    required_documents: List[DocumentRequirement]

