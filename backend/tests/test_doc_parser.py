import json
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.doc_parser import parse_form16_text, parse_ais_data, reconcile_documents
from backend.app.services.rule_engine import rule_engine
from backend.app.models.documents import Form16Parsed, AISParsed

client = TestClient(app)

SAMPLE_FORM16_TEXT = """
FORM NO. 16
[See rule 31(1)(a)]
Certificate under section 203 of the Income-tax Act, 1961 for tax deducted at source
Assessment Year: 2025-26
Name and address of Employer: TECHSOL SOLUTIONS INDIA PVT LTD
PAN of the Deductor: AABCT1234F
TAN of the Deductor: BLRT09876C
PAN of the Employee: ABCDE1234K

PART B (Annexure)
1. Gross Salary:
(a) Salary as per provisions contained in section 17(1): Rs. 14,50,000.00
2. Less: Allowances to the extent exempt under section 10:
House Rent Allowance exempt under section 10(13A): Rs. 1,20,000.00
Total amount of any other exemption under section 10: Rs. 1,20,000.00
3. Balance (1 - 2): Rs. 13,30,000.00
4. Deductions under section 16:
(a) Standard deduction under section 16(ia): Rs. 50,000.00
(b) Tax on employment under section 16(iii): Rs. 2,400.00
5. Aggregate of 4(a) and 4(b): Rs. 52,400.00
6. Income chargeable under the head 'Salaries' (3 - 5): Rs. 12,77,600.00

9. Deductions under Chapter VI-A:
(a) Deduction under section 80C: Rs. 1,50,000.00
(b) Deduction under section 80CCD(1B): Rs. 50,000.00
(c) Deduction under section 80D: Rs. 25,000.00
Total amount deductible under Chapter VI-A: Rs. 2,25,000.00

10. Total Taxable Income (6 - 9): Rs. 10,52,600.00
Total tax deducted and deposited: Rs. 1,18,500.00
"""

SAMPLE_AIS_JSON = {
    "sftDtls": [
        {
            "sftCode": "SFT-005",
            "infoDesc": "Interest from savings bank",
            "reportedBy": "HDFC BANK LIMITED",
            "amount": 14250.00
        },
        {
            "sftCode": "SFT-006",
            "infoDesc": "Interest from deposit",
            "reportedBy": "STATE BANK OF INDIA",
            "amount": 32000.00
        },
        {
            "sftCode": "SFT-015",
            "infoDesc": "Dividend from companies",
            "reportedBy": "TCS LIMITED",
            "amount": 8500.00
        }
    ],
    "tdsDtls": [
        {
            "tdsDedAmt": 118500.00,
            "deductor": "TECHSOL SOLUTIONS"
        }
    ]
}

def test_form16_text_parser():
    parsed = parse_form16_text(SAMPLE_FORM16_TEXT)
    assert parsed.assessment_year == "2025-26"
    assert parsed.employer_tan == "BLRT09876C"
    assert parsed.salary_breakup.gross_salary_sec17_1 == 1450000.00
    assert parsed.salary_breakup.hra_exempt_sec10_13a == 120000.00
    assert parsed.salary_breakup.standard_deduction_sec16_ia == 50000.00
    assert parsed.deductions.section_80c == 150000.00
    assert parsed.deductions.section_80ccd_1b == 50000.00
    assert parsed.deductions.section_80d_health_insurance == 25000.00
    assert parsed.total_tds_deducted == 118500.00

def test_ais_json_parser():
    raw_bytes = json.dumps(SAMPLE_AIS_JSON).encode("utf-8")
    parsed = parse_ais_data(raw_bytes, filename="ais.json")
    assert parsed.total_savings_interest == 14250.00
    assert parsed.total_fd_interest == 32000.00
    assert parsed.total_dividend_income == 8500.00
    assert parsed.total_tds_reported_ais == 118500.00
    assert len(parsed.items) == 3

def test_reconciliation_detects_undeclared_interest():
    form16 = parse_form16_text(SAMPLE_FORM16_TEXT)
    raw_bytes = json.dumps(SAMPLE_AIS_JSON).encode("utf-8")
    ais = parse_ais_data(raw_bytes, filename="ais.json")
    
    report = reconcile_documents(form16, ais)
    assert report.total_estimated_gross_income > form16.gross_total_income
    assert len(report.discrepancies) >= 1
    # Check that high interest discrepancy warning is generated
    interest_warn = [d for d in report.discrepancies if "Interest & Dividends" in d.title]
    assert len(interest_warn) == 1
    assert "Section 143(1)" in interest_warn[0].legal_impact

def test_dynamic_rule_engine():
    years = rule_engine.get_supported_years()
    assert "2025-26" in years
    assert "2024-25" in years
    
    rules_25 = rule_engine.get_rules("2025-26")
    # Standard deduction in New Regime for AY 2025-26 was increased to 75000
    assert rules_25["standard_deduction"]["salaried_new_regime"] == 75000
    
    rules_24 = rule_engine.get_rules("2024-25")
    # Standard deduction in New Regime for AY 2024-25 was 50000
    assert rules_24["standard_deduction"]["salaried_new_regime"] == 50000

def test_rules_api_endpoints():
    response = client.get("/api/v1/rules/supported-years")
    assert response.status_code == 200
    assert "2025-26" in response.json()

    response = client.get("/api/v1/rules/2025-26")
    assert response.status_code == 200
    data = response.json()
    assert data["assessment_year"] == "2025-26"
    assert data["standard_deduction"]["salaried_new_regime"] == 75000

