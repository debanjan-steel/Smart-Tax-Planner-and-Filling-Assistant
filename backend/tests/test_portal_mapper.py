from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.models.tax import TaxOptimizationComparison, RegimeTaxResult

client = TestClient(app)

SAMPLE_COMPARISON = {
    "assessment_year": "2025-26",
    "recommended_regime": "NEW",
    "recommended_regime_title": "New Tax Regime (Section 115BAC)",
    "tax_savings_amount": 48600.0,
    "summary_verdict": "New Regime saves you ₹48,600!",
    "new_regime": {
        "regime_name": "New Tax Regime (Section 115BAC)",
        "is_default": True,
        "gross_total_income": 1540000.0,
        "standard_deduction": 75000.0,
        "total_exemptions_and_deductions": 75000.0,
        "net_taxable_income": 1465000.0,
        "slab_breakdown": [],
        "tax_before_rebate": 133000.0,
        "rebate_87a": 0.0,
        "tax_after_rebate": 133000.0,
        "surcharge": 0.0,
        "cess_4_percent": 5320.0,
        "total_tax_liability": 138320.0,
        "total_taxes_paid": 145000.0,
        "net_tax_payable": 0.0,
        "refund_due": 6680.0
    },
    "old_regime": {
        "regime_name": "Old Tax Regime",
        "is_default": False,
        "gross_total_income": 1540000.0,
        "standard_deduction": 50000.0,
        "total_exemptions_and_deductions": 275000.0,
        "net_taxable_income": 1265000.0,
        "slab_breakdown": [],
        "tax_before_rebate": 179500.0,
        "rebate_87a": 0.0,
        "tax_after_rebate": 179500.0,
        "surcharge": 0.0,
        "cess_4_percent": 7180.0,
        "total_tax_liability": 186920.0,
        "total_taxes_paid": 145000.0,
        "net_tax_payable": 41920.0,
        "refund_due": 0.0
    },
    "breakeven_deductions_needed": 425000.0,
    "current_old_regime_deductions": 275000.0,
    "deduction_gap_to_beat_new_regime": 150000.0,
    "key_recommendations": ["Opt in for Section 115BAC on portal."]
}

def test_portal_filing_plan_generation():
    payload = {
        "tax_comparison": SAMPLE_COMPARISON,
        "form_diagnosis": {
            "recommended_form": "ITR-1",
            "form_title": "ITR-1 (Sahaj)",
            "summary_verdict": "Qualified for ITR-1",
            "primary_reasons": ["Resident salaried"],
            "disqualifications": [],
            "compliance_risks": [],
            "required_documents": []
        },
        "form16": {
            "salary_breakup": {
                "gross_salary_sec17_1": 1540000.0
            }
        },
        "ais": {
            "total_savings_interest": 18450.0
        }
    }
    response = client.post("/api/v1/portal/filing-plan", json=payload)
    assert response.status_code == 200
    plan = response.json()
    assert plan["recommended_form"] == "ITR-1"
    assert len(plan["steps"]) == 6
    assert plan["is_refund"] is True
    assert plan["estimated_refund_or_due"] == 6680.0
    
    # Check Section 115BAC instruction says NO (for New Regime)
    step2 = [s for s in plan["steps"] if s["step_number"] == 2][0]
    assert "NO" in step2["critical_action"]

    # Check Step 3 has Schedule Salary and Schedule OS
    step3 = [s for s in plan["steps"] if s["step_number"] == 3][0]
    field_labels = [f["field_label"] for f in step3["fields"]]
    assert any("Salary as per provisions" in label for label in field_labels)
    assert any("Interest from Savings Bank" in label for label in field_labels)

def test_computation_sheet_html_generation():
    payload = {
        "tax_comparison": SAMPLE_COMPARISON,
        "form16": {
            "salary_breakup": {
                "gross_salary_sec17_1": 1540000.0
            }
        },
        "ais": {
            "total_savings_interest": 18450.0
        }
    }
    response = client.post("/api/v1/portal/computation-sheet-html", json=payload)
    assert response.status_code == 200
    assert "STATEMENT OF TAX COMPUTATION" in response.text
    assert "Assessment Year: <strong>2025-26</strong>" in response.text
    assert "NET REFUND DUE TO TAXPAYER" in response.text

