from typing import Dict, Any, List, Optional
from backend.app.models.portal import PortalFilingPlan, PortalFilingStep, PortalFieldMapping
from backend.app.models.tax import TaxOptimizationComparison
from backend.app.models.questionnaire import FormDiagnosisResponse

def generate_portal_filing_plan(
    tax_comp: TaxOptimizationComparison,
    diagnosis: Optional[FormDiagnosisResponse] = None,
    f16_data: Optional[Dict[str, Any]] = None,
    ais_data: Optional[Dict[str, Any]] = None
) -> PortalFilingPlan:
    """
    Transforms parsed financials and tax optimization calculations into a precise,
    step-by-step hand-holding roadmap for eportal.incometax.gov.in.
    """
    ay = tax_comp.assessment_year
    form_code = diagnosis.recommended_form if diagnosis else "ITR-1"
    form_name = diagnosis.form_title if diagnosis else "ITR-1 (Sahaj)"
    is_new = tax_comp.recommended_regime == "NEW"
    active_reg = tax_comp.new_regime if is_new else tax_comp.old_regime

    regime_instruction = (
        "When the portal asks: 'Do you wish to opt out of the New Tax Regime under Section 115BAC?' "
        "Select: NO (The New Tax Regime is your optimal choice and is the default)."
        if is_new else
        "When the portal asks: 'Do you wish to opt out of the New Tax Regime under Section 115BAC?' "
        "Select: YES (You must opt out to claim Old Regime exemptions like HRA, 80C, 80D, and Home Loan interest)."
    )

    steps: List[PortalFilingStep] = []

    # STEP 1: Login & Initialize Return
    steps.append(PortalFilingStep(
        step_number=1,
        title="Official Portal Login & Return Selection",
        subtitle="Initialize your return on https://eportal.incometax.gov.in",
        official_portal_screen="Dashboard -> e-File -> Income Tax Returns -> File Income Tax Return",
        critical_action=f"Select Assessment Year '{ay}' and Filing Mode 'Online (Recommended)'. Then choose '{form_code}'.",
        fields=[],
        caution_notes=[
            "Ensure you are on the authentic URL: https://eportal.incometax.gov.in (look for the green padlock).",
            "Do NOT share your password with any third-party app or person.",
            f"Filing Type: Select '139(1) - On or before due date' for on-time filing."
        ]
    ))

    # STEP 2: General Information & Section 115BAC Regime Selection
    steps.append(PortalFilingStep(
        step_number=2,
        title="General Information & Tax Regime Choice",
        subtitle="Confirm Personal Details and Select Your Tax Regime",
        official_portal_screen="Schedule Personal Information & Section 115BAC Opt-Out",
        critical_action=regime_instruction,
        fields=[
            PortalFieldMapping(
                schedule_code="PART_GEN",
                schedule_name="General Information",
                field_label="Filing Status",
                portal_field_code="Section 139(1)",
                amount=0.0,
                source_document="Income Tax Act, 1961",
                instructions="Select '139(1) - Return filed on or before due date'"
            ),
            PortalFieldMapping(
                schedule_code="PART_GEN",
                schedule_name="General Information",
                field_label="Opt out of Section 115BAC?",
                portal_field_code="Sec 115BAC Flag",
                amount=0.0,
                source_document="TaxSahayak Regime Optimizer",
                instructions="Click 'NO' for New Regime" if is_new else "Click 'YES' for Old Regime"
            )
        ],
        caution_notes=[
            "Under the Finance Act, New Tax Regime is the default. If you don't explicitly choose YES to opt out, the portal will automatically file under the New Regime."
        ]
    ))

    # STEP 3: Gross Total Income Schedule Entry
    salary_fields: List[PortalFieldMapping] = []
    sal = f16_data.get("salary_breakup", {}) if f16_data else {}

    # Gross Salary 17(1)
    salary_fields.append(PortalFieldMapping(
        schedule_code="SCH_SALARY",
        schedule_name="Income from Salary",
        field_label="Salary as per provisions contained in section 17(1)",
        portal_field_code="1(a)",
        amount=sal.get("gross_salary_sec17_1", active_reg.gross_total_income),
        source_document="Form 16 Part B, Line 1(a)",
        instructions="Verify against pre-filled portal value or enter exact gross salary."
    ))

    # Exemptions u/s 10 (HRA) if Old Regime
    if not is_new and sal.get("hra_exempt_sec10_13a", 0) > 0:
        salary_fields.append(PortalFieldMapping(
            schedule_code="SCH_SALARY",
            schedule_name="Income from Salary",
            field_label="House Rent Allowance exempt under section 10(13A)",
            portal_field_code="2 - Sec 10(13A)",
            amount=sal.get("hra_exempt_sec10_13a", 0),
            source_document="Form 16 Part B, Line 2",
            instructions="Select '10(13A) - Allowance to meet expenditure incurred on house rent' and enter amount."
        ))

    # Standard Deduction 16(ia)
    salary_fields.append(PortalFieldMapping(
        schedule_code="SCH_SALARY",
        schedule_name="Income from Salary",
        field_label="Standard Deduction under section 16(ia)",
        portal_field_code="4(a)",
        amount=active_reg.standard_deduction,
        source_document="Automatic u/s 16(ia)",
        instructions=f"Portal automatically applies ₹{active_reg.standard_deduction:,.0f} for AY {ay}."
    ))

    # Other Sources (Interest from AIS)
    other_fields: List[PortalFieldMapping] = []
    ais_sav = ais_data.get("total_savings_interest", 0.0) if ais_data else 0.0
    ais_fd = ais_data.get("total_fd_interest", 0.0) if ais_data else 0.0
    ais_div = ais_data.get("total_dividend_income", 0.0) if ais_data else 0.0

    if ais_sav > 0:
        other_fields.append(PortalFieldMapping(
            schedule_code="SCH_OS",
            schedule_name="Income from Other Sources",
            field_label="Interest from Savings Bank Accounts",
            portal_field_code="1(a)(i)",
            amount=ais_sav,
            source_document="AIS Line SFT-005 / Bank Interest Certificates",
            instructions="Click '+ Add Details' -> Select 'Interest from Savings Bank Accounts'."
        ))

    if ais_fd > 0:
        other_fields.append(PortalFieldMapping(
            schedule_code="SCH_OS",
            schedule_name="Income from Other Sources",
            field_label="Interest from Deposits (Bank / Post Office / Cooperative)",
            portal_field_code="1(a)(ii)",
            amount=ais_fd,
            source_document="AIS Line SFT-006 / Form 26AS",
            instructions="Click '+ Add Details' -> Select 'Interest from Deposits (Bank/Co-operative Society/Post Office)'."
        ))

    if ais_div > 0:
        other_fields.append(PortalFieldMapping(
            schedule_code="SCH_OS",
            schedule_name="Income from Other Sources",
            field_label="Dividend Income",
            portal_field_code="1(a)(iv)",
            amount=ais_div,
            source_document="AIS Line SFT-015",
            instructions="Enter total dividend income received from domestic companies and mutual funds."
        ))

    steps.append(PortalFilingStep(
        step_number=3,
        title="Schedule Gross Total Income",
        subtitle="Verify Salary, House Property, and AIS Interest Income",
        official_portal_screen="Schedule Salary & Schedule Other Sources",
        critical_action="Ensure all bank interest reported in AIS is entered to prevent Section 143(1) notices.",
        fields=salary_fields + other_fields,
        caution_notes=[
            "Pre-filled salary on portal might not include recent bonuses or allowances. Always verify against your Form 16 Part B.",
            "Never delete or skip bank interest from AIS. Automated mismatch notices are generated if portal finds AIS interest missing from return."
        ]
    ))

    # STEP 4: Total Deductions Schedule (Schedule VI-A)
    ded_fields: List[PortalFieldMapping] = []
    if not is_new:
        deds = f16_data.get("deductions", {}) if f16_data else {}
        if deds.get("section_80c", 0) > 0:
            ded_fields.append(PortalFieldMapping(
                schedule_code="SCH_VIA",
                schedule_name="Deductions under Chapter VI-A",
                field_label="Section 80C (EPF, PPF, ELSS, Life Insurance, Tuition Fees)",
                portal_field_code="80C",
                amount=min(150000.0, deds.get("section_80c", 0)),
                source_document="Form 16 Part B / Investment Receipts",
                instructions="Enter eligible Section 80C investments (maximum limit ₹1,50,000)."
            ))
        if deds.get("section_80ccd_1b", 0) > 0:
            ded_fields.append(PortalFieldMapping(
                schedule_code="SCH_VIA",
                schedule_name="Deductions under Chapter VI-A",
                field_label="Section 80CCD(1B) (National Pension System - NPS)",
                portal_field_code="80CCD(1B)",
                amount=min(50000.0, deds.get("section_80ccd_1b", 0)),
                source_document="NPS Tier-1 Statement / Form 16",
                instructions="Enter additional voluntary NPS contribution (maximum limit ₹50,000)."
            ))
        if deds.get("section_80d_health_insurance", 0) > 0:
            ded_fields.append(PortalFieldMapping(
                schedule_code="SCH_VIA",
                schedule_name="Deductions under Chapter VI-A",
                field_label="Section 80D (Health Insurance / Mediclaim)",
                portal_field_code="80D",
                amount=deds.get("section_80d_health_insurance", 0),
                source_document="Mediclaim Premium Tax Certificate",
                instructions="Complete Schedule 80D (Self/Family and Senior Citizen Parents)."
            ))
        if ais_sav > 0:
            ded_fields.append(PortalFieldMapping(
                schedule_code="SCH_VIA",
                schedule_name="Deductions under Chapter VI-A",
                field_label="Section 80TTA (Interest on Savings Accounts)",
                portal_field_code="80TTA",
                amount=min(10000.0, ais_sav),
                source_document="Calculated from Savings Interest",
                instructions="Claim deduction for savings bank interest up to ₹10,000."
            ))
    else:
        ded_fields.append(PortalFieldMapping(
            schedule_code="SCH_VIA",
            schedule_name="Deductions under Chapter VI-A",
            field_label="Chapter VI-A Deductions",
            portal_field_code="N/A",
            amount=0.0,
            source_document="New Tax Regime u/s 115BAC",
            instructions="Under New Regime, 80C, 80D, and 80TTA are not claimed; only standard deduction applies."
        ))

    steps.append(PortalFilingStep(
        step_number=4,
        title="Schedule Total Deductions (Chapter VI-A)",
        subtitle="Claim Eligible Tax Deductions" if not is_new else "New Regime Deductions Forfeited Notice",
        official_portal_screen="Schedule Deductions u/c VI-A",
        critical_action="Enter your investments and insurance deductions exactly as documented." if not is_new else "Proceed past deductions as New Regime applies flat lower rates.",
        fields=ded_fields,
        caution_notes=[
            "Keep proof documents (ELSS statements, insurance premium receipts) safely archived for 6 years in case of scrutiny."
        ]
    ))

    # STEP 5: Taxes Paid (TDS & Advance Tax)
    tds_fields: List[PortalFieldMapping] = []
    tds_fields.append(PortalFieldMapping(
        schedule_code="SCH_TDS",
        schedule_name="Taxes Paid & Verification",
        field_label="Total TDS on Salary (Matched with 26AS)",
        portal_field_code="Schedule TDS-1",
        amount=active_reg.total_taxes_paid,
        source_document="Form 16 Part A & Form 26AS",
        instructions="Confirm that your employer's TAN and TDS amount match Form 26AS exactly."
    ))

    steps.append(PortalFilingStep(
        step_number=5,
        title="Schedule Taxes Paid & Verification",
        subtitle="Verify TDS Credits from Employer and Banks",
        official_portal_screen="Schedule Taxes Paid (TDS1, TDS2, Advance Tax)",
        critical_action="Confirm that total tax credits match your Form 26AS and Form 16 Part A.",
        fields=tds_fields,
        caution_notes=[
            "Tax credit is allowed only if the TAN and TDS amount are reflected in TRACES/Form 26AS. If there is a shortfall, contact your employer immediately."
        ]
    ))

    # STEP 6: Computation & E-Verification
    steps.append(PortalFilingStep(
        step_number=6,
        title="Final Computation & Instant E-Verification",
        subtitle="Verify Net Tax Liability, Validate Bank Account & Complete with Aadhaar OTP",
        official_portal_screen="Part B - TTI (Computation of Tax Liability) & e-Verify",
        critical_action="Select 'e-Verify Now' with Aadhaar OTP to complete filing in under 60 seconds.",
        fields=[
            PortalFieldMapping(
                schedule_code="PART_TTI",
                schedule_name="Computation of Tax Liability",
                field_label="Total Tax, Surcharge & Cess",
                portal_field_code="Line 4",
                amount=active_reg.total_tax_liability,
                source_document="TaxSahayak Tax Engine",
                instructions="Verify that portal total tax matches TaxSahayak within ±₹10."
            ),
            PortalFieldMapping(
                schedule_code="PART_TTI",
                schedule_name="Computation of Tax Liability",
                field_label="Estimated Refund Due" if active_reg.refund_due > 0 else "Self-Assessment Tax Due",
                portal_field_code="Line 11 / Line 12",
                amount=active_reg.refund_due if active_reg.refund_due > 0 else active_reg.net_tax_payable,
                source_document="TaxSahayak Tax Engine",
                instructions="Confirm refund or pay self-assessment tax via Challan 280 / e-Pay Tax if due."
            )
        ],
        caution_notes=[
            "Do NOT skip e-Verification! An unverified ITR is legally considered invalid after 30 days under Rule 12.",
            "Make sure your bank account has 'Pre-validated' status on the portal to receive your income tax refund directly via ECS/NEFT."
        ]
    ))

    is_refund = active_reg.refund_due > 0
    refund_or_due = active_reg.refund_due if is_refund else active_reg.net_tax_payable

    pre_filing = [
        "Aadhaar card linked with PAN",
        "Active mobile number linked with Aadhaar to receive e-Verification OTP",
        "Pre-validated bank account on e-Filing portal for tax refund direct credit",
        "Form 16 Part A & B and Annual Information Statement (AIS) kept open for cross-reference"
    ]

    e_verif = [
        "Select 'I would like to e-Verify now using Aadhaar OTP (Recommended)'",
        "Click 'I agree to validate my Aadhaar details with UIDAI' -> 'Generate Aadhaar OTP'",
        "Enter the 6-digit OTP received on your mobile and click 'Submit'",
        "Download and save the ITR-V Acknowledgment Slip (PDF) for your permanent records."
    ]

    return PortalFilingPlan(
        assessment_year=ay,
        recommended_form=form_code,
        form_title=form_name,
        regime_choice=tax_comp.recommended_regime,
        regime_portal_instruction=regime_instruction,
        total_gross_income=active_reg.gross_total_income,
        total_taxable_income=active_reg.net_taxable_income,
        total_tax_liability=active_reg.total_tax_liability,
        total_tds_credit=active_reg.total_taxes_paid,
        estimated_refund_or_due=refund_or_due,
        is_refund=is_refund,
        steps=steps,
        pre_filing_checklist=pre_filing,
        e_verification_instructions=e_verif
    )

