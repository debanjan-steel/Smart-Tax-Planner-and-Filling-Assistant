from fastapi import APIRouter
from backend.app.models.tax import TaxCalculationInput, TaxOptimizationComparison
from backend.app.models.documents import Form16Parsed, AISParsed
from backend.app.services.tax_engine import optimize_tax_regimes

router = APIRouter(prefix="/tax", tags=["Tax Optimization Engine (Old vs New Regime)"])

@router.post("/calculate", response_model=TaxOptimizationComparison)
def calculate_tax(input_data: TaxCalculationInput):
    """
    Computes comparative tax liability for New Regime (Sec 115BAC) vs Old Regime,
    determines the optimal regime, calculates breakeven deduction thresholds,
    and returns bracket-by-bracket slab breakdowns.
    """
    return optimize_tax_regimes(input_data)

@router.post("/optimize-from-documents", response_model=TaxOptimizationComparison)
def optimize_from_documents(payload: dict):
    """
    Automatically converts parsed Form 16 and AIS data into tax calculation parameters
    and returns the optimized regime recommendation.
    """
    f16_dict = payload.get("form16")
    ais_dict = payload.get("ais")
    ay = payload.get("assessment_year", "2025-26")

    gross_sal = 0.0
    hra_ex = 0.0
    prof_tax = 0.0
    ded_80c = 0.0
    ded_80ccd = 0.0
    ded_80d = 0.0
    ded_24b = 0.0
    tds = 0.0

    if f16_dict:
        sal = f16_dict.get("salary_breakup", {})
        gross_sal = sal.get("gross_salary_sec17_1", 0.0)
        hra_ex = sal.get("hra_exempt_sec10_13a", 0.0)
        prof_tax = sal.get("professional_tax_sec16_iii", 0.0)

        deds = f16_dict.get("deductions", {})
        ded_80c = deds.get("section_80c", 0.0)
        ded_80ccd = deds.get("section_80ccd_1b", 0.0)
        ded_80d = deds.get("section_80d_health_insurance", 0.0)
        ded_24b = deds.get("section_24b_house_loan_interest", 0.0)
        tds = f16_dict.get("total_tds_deducted", 0.0)

    sav_interest = 0.0
    fd_interest = 0.0
    div_income = 0.0

    if ais_dict:
        sav_interest = ais_dict.get("total_savings_interest", 0.0)
        fd_interest = ais_dict.get("total_fd_interest", 0.0)
        div_income = ais_dict.get("total_dividend_income", 0.0)
        # If AIS reports TDS, use the max of Form 16 or AIS
        ais_tds = ais_dict.get("total_tds_reported_ais", 0.0)
        if ais_tds > tds:
            tds = ais_tds

    tax_input = TaxCalculationInput(
        assessment_year=ay,
        gross_salary=gross_sal,
        savings_interest=sav_interest,
        fd_interest=fd_interest,
        dividend_income=div_income,
        hra_exemption=hra_ex,
        professional_tax=prof_tax,
        deduction_80c=ded_80c,
        deduction_80ccd_1b=ded_80ccd,
        deduction_80d=ded_80d,
        home_loan_interest_24b=ded_24b,
        tds_already_paid=tds
    )

    return optimize_tax_regimes(tax_input)

