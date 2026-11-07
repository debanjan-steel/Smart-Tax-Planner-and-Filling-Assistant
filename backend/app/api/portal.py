from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from typing import Dict, Any
from backend.app.models.portal import PortalFilingPlan
from backend.app.models.tax import TaxOptimizationComparison
from backend.app.models.questionnaire import FormDiagnosisResponse
from backend.app.services.portal_mapper import generate_portal_filing_plan

router = APIRouter(prefix="/portal", tags=["Official Portal Guide & Schedule Mapper"])

@router.post("/filing-plan", response_model=PortalFilingPlan)
def get_filing_plan(payload: dict):
    """
    Produces the schedule-by-schedule official portal filing roadmap,
    complete with 1-click copyable figures and Section 115BAC instructions.
    """
    tax_comp_dict = payload.get("tax_comparison", {})
    diagnosis_dict = payload.get("form_diagnosis", {})
    f16_data = payload.get("form16", {})
    ais_data = payload.get("ais", {})

    tax_comp = TaxOptimizationComparison(**tax_comp_dict)
    diagnosis = FormDiagnosisResponse(**diagnosis_dict) if diagnosis_dict else None

    return generate_portal_filing_plan(tax_comp, diagnosis, f16_data, ais_data)

@router.post("/computation-sheet-html", response_class=HTMLResponse)
def get_computation_sheet_html(payload: dict):
    """
    Generates a clean, print-ready HTML Tax Computation Sheet that the user
    can print or export as PDF for their permanent tax records.
    """
    tax_comp_dict = payload.get("tax_comparison", {})
    f16 = payload.get("form16", {})
    ais = payload.get("ais", {})
    
    comp = TaxOptimizationComparison(**tax_comp_dict)
    is_new = comp.recommended_regime == "NEW"
    active_reg = comp.new_regime if is_new else comp.old_regime
    ay = comp.assessment_year
    fy = "2024-25" if "2025-26" in ay else "2023-24"

    sal = f16.get("salary_breakup", {})
    gross_sal = sal.get("gross_salary_sec17_1", active_reg.gross_total_income)
    hra = sal.get("hra_exempt_sec10_13a", 0.0)
    std_ded = active_reg.standard_deduction
    
    sav_int = ais.get("total_savings_interest", 0.0)
    fd_int = ais.get("total_fd_interest", 0.0)
    div_inc = ais.get("total_dividend_income", 0.0)
    
    deds = f16.get("deductions", {})
    d_80c = deds.get("section_80c", 0.0)
    d_80d = deds.get("section_80d_health_insurance", 0.0)
    d_80ccd = deds.get("section_80ccd_1b", 0.0)

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Tax Computation Sheet — AY {ay}</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 40px; color: #1e293b; }}
            .header {{ border-bottom: 2px solid #0f172a; padding-bottom: 12px; margin-bottom: 24px; }}
            .title {{ font-size: 24px; font-weight: bold; margin: 0; color: #0f172a; }}
            .meta {{ font-size: 13px; color: #64748b; margin-top: 4px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 16px; font-size: 13px; }}
            th, td {{ padding: 10px 12px; border-bottom: 1px solid #e2e8f0; text-align: left; }}
            th {{ background-color: #f8fafc; font-weight: 600; color: #475569; }}
            .amount {{ text-align: right; font-variant-numeric: tabular-nums; }}
            .bold {{ font-weight: bold; }}
            .highlight {{ background-color: #f1f5f9; font-weight: bold; }}
            .winner-box {{ background-color: #ecfdf5; border: 1px solid #a7f3d0; padding: 16px; border-radius: 8px; margin-top: 24px; }}
            .footer {{ margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 12px; }}
            @media print {{ body {{ margin: 0; }} }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1 class="title">STATEMENT OF TAX COMPUTATION</h1>
            <div class="meta">
                <span>Assessment Year: <strong>{ay}</strong></span> | 
                <span>Financial Year: <strong>{fy}</strong></span> | 
                <span>Regime: <strong>{active_reg.regime_name}</strong></span>
            </div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Particulars / Head of Income</th>
                    <th>Schedule</th>
                    <th class="amount">Amount (₹)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><strong>Income from Salary / Pension</strong></td>
                    <td>Schedule S</td>
                    <td class="amount"></td>
                </tr>
                <tr>
                    <td style="padding-left: 24px;">Gross Salary u/s 17(1)</td>
                    <td>1(a)</td>
                    <td class="amount">₹{gross_sal:,.2f}</td>
                </tr>
                {"<tr><td style='padding-left: 24px;'>Less: HRA Exempt u/s 10(13A)</td><td>2</td><td class='amount'>-₹" + f"{hra:,.2f}</td></tr>" if not is_new and hra > 0 else ""}
                <tr>
                    <td style="padding-left: 24px;">Less: Standard Deduction u/s 16(ia)</td>
                    <td>4(a)</td>
                    <td class="amount">-₹{std_ded:,.2f}</td>
                </tr>
                <tr class="highlight">
                    <td><strong>Income Chargeable under Head 'Salaries'</strong></td>
                    <td>Part B - TI</td>
                    <td class="amount">₹{max(0.0, gross_sal - (hra if not is_new else 0) - std_ded):,.2f}</td>
                </tr>
                <tr>
                    <td><strong>Income from Other Sources</strong></td>
                    <td>Schedule OS</td>
                    <td class="amount"></td>
                </tr>
                <tr>
                    <td style="padding-left: 24px;">Interest from Savings Bank Accounts (AIS)</td>
                    <td>1(a)(i)</td>
                    <td class="amount">₹{sav_int:,.2f}</td>
                </tr>
                <tr>
                    <td style="padding-left: 24px;">Interest from Fixed / Term Deposits (AIS)</td>
                    <td>1(a)(ii)</td>
                    <td class="amount">₹{fd_int:,.2f}</td>
                </tr>
                <tr>
                    <td style="padding-left: 24px;">Dividend Income (AIS)</td>
                    <td>1(a)(iv)</td>
                    <td class="amount">₹{div_inc:,.2f}</td>
                </tr>
                <tr class="highlight">
                    <td><strong>GROSS TOTAL INCOME (GTI)</strong></td>
                    <td>Part B - TI</td>
                    <td class="amount">₹{active_reg.gross_total_income:,.2f}</td>
                </tr>
                {"<tr><td><strong>Deductions under Chapter VI-A</strong></td><td>Schedule VI-A</td><td class='amount'></td></tr>" if not is_new else ""}
                {"<tr><td style='padding-left: 24px;'>Section 80C (Life Insurance, EPF, ELSS, PPF)</td><td>80C</td><td class='amount'>-₹" + f"{d_80c:,.2f}</td></tr>" if not is_new and d_80c > 0 else ""}
                {"<tr><td style='padding-left: 24px;'>Section 80CCD(1B) (NPS Voluntary)</td><td>80CCD</td><td class='amount'>-₹" + f"{d_80ccd:,.2f}</td></tr>" if not is_new and d_80ccd > 0 else ""}
                {"<tr><td style='padding-left: 24px;'>Section 80D (Health Insurance Premium)</td><td>80D</td><td class='amount'>-₹" + f"{d_80d:,.2f}</td></tr>" if not is_new and d_80d > 0 else ""}
                <tr class="bold" style="background-color: #e2e8f0;">
                    <td>TOTAL TAXABLE INCOME (Rounded to nearest ₹10)</td>
                    <td>Line 12</td>
                    <td class="amount">₹{active_reg.net_taxable_income:,.2f}</td>
                </tr>
                <tr>
                    <td>Tax Computed on Total Income at Slab Rates</td>
                    <td>Part B - TTI</td>
                    <td class="amount">₹{active_reg.tax_before_rebate:,.2f}</td>
                </tr>
                {"<tr><td>Less: Tax Rebate under Section 87A</td><td>Line 2(e)</td><td class='amount' style='color: #059669;'>-₹" + f"{active_reg.rebate_87a:,.2f}</td></tr>" if active_reg.rebate_87a > 0 else ""}
                <tr>
                    <td>Add: Health & Education Cess (4%)</td>
                    <td>Line 3</td>
                    <td class="amount">₹{active_reg.cess_4_percent:,.2f}</td>
                </tr>
                <tr class="bold highlight" style="font-size: 14px;">
                    <td>TOTAL TAX LIABILITY</td>
                    <td>Line 4</td>
                    <td class="amount">₹{active_reg.total_tax_liability:,.2f}</td>
                </tr>
                <tr>
                    <td>Less: Taxes Deducted at Source (TDS Credits from Form 16 & 26AS)</td>
                    <td>Schedule TDS</td>
                    <td class="amount">-₹{active_reg.total_taxes_paid:,.2f}</td>
                </tr>
                <tr class="bold" style="background-color: {'#d1fae5' if active_reg.refund_due > 0 else '#fee2e2'}; font-size: 15px;">
                    <td>{'NET REFUND DUE TO TAXPAYER' if active_reg.refund_due > 0 else 'BALANCE TAX PAYABLE (Self-Assessment)'}</td>
                    <td>Line 11 / 12</td>
                    <td class="amount" style="color: {'#065f46' if active_reg.refund_due > 0 else '#991b1b'};">
                        ₹{(active_reg.refund_due if active_reg.refund_due > 0 else active_reg.net_tax_payable):,.2f}
                    </td>
                </tr>
            </tbody>
        </table>

        <div class="winner-box">
            <strong>Optimal Tax Planning Strategy:</strong> {comp.summary_verdict}
        </div>

        <div class="footer">
            Generated via TaxSahayak • Compliant with Indian Income Tax Act 1961 and DPDP Act 2023. Keep this computation sheet archived with your ITR-V acknowledgment.
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

