from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_itr1_salaried_diagnosis():
    # Pure Salaried Resident with 1 house and < 50L income
    payload = {
        "assessment_year": "2025-26",
        "is_resident": True,
        "total_income_exceeds_50_lakh": False,
        "has_salary_or_pension": True,
        "house_property_count": 1,
        "has_capital_gains": False,
        "has_crypto_or_vda": False,
        "has_business_or_profession": False,
        "is_presumptive_eligible": False,
        "has_fo_or_intraday": False,
        "is_company_director": False,
        "holds_unlisted_shares": False,
        "has_foreign_assets_or_income": False,
        "agricultural_income_exceeds_5000": False,
        "has_brought_forward_losses": False
    }
    response = client.post("/api/v1/questionnaire/diagnose", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["recommended_form"] == "ITR-1"
    doc_ids = [d["id"] for d in data["required_documents"]]
    assert "form_16" in doc_ids
    assert "ais_tis" in doc_ids
    assert "form_26as" in doc_ids

def test_itr2_capital_gains_diagnosis():
    # Salaried with Capital Gains from Mutual Funds / Shares
    payload = {
        "assessment_year": "2025-26",
        "is_resident": True,
        "total_income_exceeds_50_lakh": False,
        "has_salary_or_pension": True,
        "house_property_count": 1,
        "has_capital_gains": True,
        "has_crypto_or_vda": False,
        "has_business_or_profession": False,
        "is_presumptive_eligible": False,
        "has_fo_or_intraday": False,
        "is_company_director": False,
        "holds_unlisted_shares": False,
        "has_foreign_assets_or_income": False,
        "agricultural_income_exceeds_5000": False,
        "has_brought_forward_losses": False
    }
    response = client.post("/api/v1/questionnaire/diagnose", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["recommended_form"] == "ITR-2"
    assert any("Notice 139(9)" in risk for risk in data["compliance_risks"])
    doc_ids = [d["id"] for d in data["required_documents"]]
    assert "broker_capital_gains" in doc_ids

def test_itr4_freelancer_presumptive():
    # Freelancer eligible for 44ADA
    payload = {
        "assessment_year": "2025-26",
        "is_resident": True,
        "total_income_exceeds_50_lakh": False,
        "has_salary_or_pension": False,
        "house_property_count": 1,
        "has_capital_gains": False,
        "has_crypto_or_vda": False,
        "has_business_or_profession": True,
        "is_presumptive_eligible": True,
        "has_fo_or_intraday": False,
        "is_company_director": False,
        "holds_unlisted_shares": False,
        "has_foreign_assets_or_income": False,
        "agricultural_income_exceeds_5000": False,
        "has_brought_forward_losses": False
    }
    response = client.post("/api/v1/questionnaire/diagnose", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["recommended_form"] == "ITR-4"
    doc_ids = [d["id"] for d in data["required_documents"]]
    assert "gross_receipts_summary" in doc_ids

def test_itr3_fo_trader():
    # Futures & Options trader
    payload = {
        "assessment_year": "2025-26",
        "is_resident": True,
        "total_income_exceeds_50_lakh": False,
        "has_salary_or_pension": True,
        "house_property_count": 1,
        "has_capital_gains": True,
        "has_crypto_or_vda": False,
        "has_business_or_profession": False,
        "is_presumptive_eligible": False,
        "has_fo_or_intraday": True,
        "is_company_director": False,
        "holds_unlisted_shares": False,
        "has_foreign_assets_or_income": False,
        "agricultural_income_exceeds_5000": False,
        "has_brought_forward_losses": False
    }
    response = client.post("/api/v1/questionnaire/diagnose", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["recommended_form"] == "ITR-3"
    doc_ids = [d["id"] for d in data["required_documents"]]
    assert "broker_tax_pnl" in doc_ids

def test_questionnaire_flow_endpoint():
    response = client.get("/api/v1/questionnaire/questions")
    assert response.status_code == 200
    questions = response.json()
    assert len(questions) >= 8
    assert any(q["id"] == "has_capital_gains" for q in questions)

