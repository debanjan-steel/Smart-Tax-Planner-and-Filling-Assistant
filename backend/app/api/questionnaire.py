from fastapi import APIRouter
from backend.app.models.questionnaire import TaxpayerProfile, FormDiagnosisResponse
from backend.app.services.form_finder import diagnose_itr_form

router = APIRouter(prefix="/questionnaire", tags=["ITR Form Finder Questionnaire"])

@router.post("/diagnose", response_model=FormDiagnosisResponse)
def diagnose_form(profile: TaxpayerProfile):
    """
    Diagnoses the required ITR form (ITR-1, 2, 3, or 4) based on taxpayer profile.
    Returns plain-English reasoning, compliance risk alerts, and custom document checklist.
    """
    return diagnose_itr_form(profile)

@router.get("/questions")
def get_question_flow():
    """
    Returns the structured question flow with plain-English tooltips and tax rule justifications.
    """
    return [
        {
            "id": "is_resident",
            "section": "Basic Profile",
            "title": "Are you a Resident of India for Tax Purposes?",
            "subtitle": "You were in India for 182+ days in the FY (or 60 days + 365 days in prior 4 years).",
            "type": "boolean",
            "default": True,
            "law_note": "Non-Residents (NRIs) and RNOR are disqualified from ITR-1 and ITR-4 under CBDT rules."
        },
        {
            "id": "total_income_exceeds_50_lakh",
            "section": "Basic Profile",
            "title": "Does your total annual income exceed ₹50 Lakh?",
            "subtitle": "Total gross income before Chapter VI-A deductions from all sources combined.",
            "type": "boolean",
            "default": False,
            "law_note": "Sections 139(1) strictly limits ITR-1 (Sahaj) and ITR-4 (Sugam) to income up to ₹50 Lakh."
        },
        {
            "id": "has_salary_or_pension",
            "section": "Income Sources",
            "title": "Do you earn income from Salary or Pension?",
            "subtitle": "Form 16 provided by employer or pension statement from bank.",
            "type": "boolean",
            "default": True,
            "law_note": "Eligible for standard deduction (₹75,000 in New Regime for AY 2025-26)."
        },
        {
            "id": "house_property_count",
            "section": "Income Sources",
            "title": "How many house properties do you own?",
            "subtitle": "Self-occupied or rented out.",
            "type": "choice",
            "options": [
                {"label": "None (Living on rent / parents)", "value": 0},
                {"label": "1 House Property (Self-occupied or let out)", "value": 1},
                {"label": "More than 1 House Property", "value": 2}
            ],
            "default": 1,
            "law_note": "Owning more than 1 house property disqualifies you from ITR-1 and forces ITR-2."
        },
        {
            "id": "has_capital_gains",
            "section": "Investments & Capital Gains",
            "title": "Did you sell any Equity Shares, Mutual Funds, Gold, or Real Estate?",
            "subtitle": "Even if you reinvested the proceeds or made a loss.",
            "type": "boolean",
            "default": False,
            "law_note": "Capital gains are reported under Schedule CG, which does NOT exist in ITR-1. Mandates ITR-2."
        },
        {
            "id": "has_crypto_or_vda",
            "section": "Investments & Capital Gains",
            "title": "Did you trade or hold Virtual Digital Assets (Crypto, Bitcoin, NFTs)?",
            "subtitle": "Taxed flat at 30% under Section 115BBH.",
            "type": "boolean",
            "default": False,
            "law_note": "Schedule VDA is only present in ITR-2 and ITR-3."
        },
        {
            "id": "has_business_or_profession",
            "section": "Business & Freelancing",
            "title": "Do you earn from Freelancing, Consultancy, or Business?",
            "subtitle": "Professional fees with 194J TDS or direct business receipts.",
            "type": "boolean",
            "default": False,
            "law_note": "Requires either ITR-4 (Presumptive Scheme) or ITR-3."
        },
        {
            "id": "is_presumptive_eligible",
            "section": "Business & Freelancing",
            "title": "Are you opting for the Presumptive Taxation Scheme (Sec 44AD / 44ADA)?",
            "subtitle": "Declare flat 50% profit (professionals) or 6%/8% (businesses) without maintaining books.",
            "type": "boolean",
            "default": False,
            "depends_on": "has_business_or_profession",
            "law_note": "Allows using the simplified ITR-4 (Sugam)."
        },
        {
            "id": "has_fo_or_intraday",
            "section": "Business & Freelancing",
            "title": "Did you trade in Futures & Options (F&O) or Intraday Equity?",
            "subtitle": "Derivative trading turnover on NSE/BSE.",
            "type": "boolean",
            "default": False,
            "law_note": "Income Tax law classifies F&O as business income. It strictly mandates ITR-3."
        },
        {
            "id": "is_company_director",
            "section": "Directorship & Foreign Assets",
            "title": "Are you a Director in any company?",
            "subtitle": "Any private or public limited company in India or abroad.",
            "type": "boolean",
            "default": False,
            "law_note": "Requires Director Identification Number (DIN) disclosure in ITR-2 or ITR-3."
        },
        {
            "id": "holds_unlisted_shares",
            "section": "Directorship & Foreign Assets",
            "title": "Did you hold unlisted equity shares at any point during the year?",
            "subtitle": "Pre-IPO shares, startup equity, private shares.",
            "type": "boolean",
            "default": False,
            "law_note": "Mandates Schedule AL and detailed unlisted share reporting in ITR-2."
        },
        {
            "id": "has_foreign_assets_or_income",
            "section": "Directorship & Foreign Assets",
            "title": "Do you hold Foreign Assets, Foreign Bank Accounts, or Foreign ESOPs?",
            "subtitle": "US stocks (e.g. Indmoney/Vested), RSUs/ESOPs of MNC employers, foreign bank accounts.",
            "type": "boolean",
            "default": False,
            "law_note": "Mandatory disclosure in Schedule FA under Black Money Act. Only in ITR-2 / ITR-3."
        }
    ]

