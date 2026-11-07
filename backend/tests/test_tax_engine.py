from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.models.tax import TaxCalculationInput
from backend.app.services.tax_engine import optimize_tax_regimes

client = TestClient(app)

def test_new_regime_zero_tax_up_to_7_lakh_taxable():
    # AY 2025-26: Gross Salary 7,75,000 -> Standard Deduction 75,000 -> Net 7,00,000 -> 87A rebate makes tax ZERO
    inp = TaxCalculationInput(
        assessment_year="2025-26",
        gross_salary=775000.0,
        tds_already_paid=0.0
    )
    result = optimize_tax_regimes(inp)
    assert result.new_regime.standard_deduction == 75000.0
    assert result.new_regime.net_taxable_income == 700000.0
    assert result.new_regime.rebate_87a == 20000.0
    assert result.new_regime.total_tax_liability == 0.0
    assert result.recommended_regime == "NEW"

def test_new_regime_beats_old_regime_for_moderate_deductions():
    # Salaried 15,00,000 with 1.5L 80C and 25k 80D
    inp = TaxCalculationInput(
        assessment_year="2025-26",
        gross_salary=1500000.0,
        deduction_80c=150000.0,
        deduction_80d=25000.0,
        tds_already_paid=130000.0
    )
    result = optimize_tax_regimes(inp)
    # New Regime tax should be ~1,30,000 vs Old Regime ~2,02,800
    assert result.new_regime.total_tax_liability < result.old_regime.total_tax_liability
    assert result.recommended_regime == "NEW"
    assert result.tax_savings_amount > 50000.0

def test_old_regime_wins_with_heavy_deductions():
    # Salaried 18,00,000 with HRA 3L, 80C 1.5L, Home Loan Interest 2L, 80D 50k, 80CCD 50k
    inp = TaxCalculationInput(
        assessment_year="2025-26",
        gross_salary=1800000.0,
        hra_exemption=300000.0,
        home_loan_interest_24b=200000.0,
        deduction_80c=150000.0,
        deduction_80ccd_1b=50000.0,
        deduction_80d=50000.0
    )
    result = optimize_tax_regimes(inp)
    # Total deductions in Old Regime exceed 8 Lakhs
    assert result.old_regime.total_tax_liability < result.new_regime.total_tax_liability
    assert result.recommended_regime == "OLD"
    assert result.tax_savings_amount > 10000.0

def test_tax_api_calculate_endpoint():
    payload = {
        "assessment_year": "2025-26",
        "gross_salary": 1200000.0,
        "savings_interest": 15000.0,
        "deduction_80c": 150000.0,
        "tds_already_paid": 80000.0
    }
    response = client.post("/api/v1/tax/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "recommended_regime" in data
    assert "new_regime" in data
    assert "old_regime" in data
    assert len(data["new_regime"]["slab_breakdown"]) > 0

def test_tax_api_optimize_from_documents():
    doc_payload = {
        "assessment_year": "2025-26",
        "form16": {
            "salary_breakup": {
                "gross_salary_sec17_1": 1400000.0,
                "hra_exempt_sec10_13a": 120000.0,
                "professional_tax_sec16_iii": 2400.0
            },
            "deductions": {
                "section_80c": 150000.0,
                "section_80d_health_insurance": 25000.0
            },
            "total_tds_deducted": 110000.0
        },
        "ais": {
            "total_savings_interest": 12000.0,
            "total_fd_interest": 20000.0
        }
    }
    response = client.post("/api/v1/tax/optimize-from-documents", json=doc_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["assessment_year"] == "2025-26"
    assert data["new_regime"]["gross_total_income"] == 1432000.0

