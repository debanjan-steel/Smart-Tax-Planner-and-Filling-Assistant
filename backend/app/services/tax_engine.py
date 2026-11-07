import math
from typing import List, Tuple, Dict, Any
from backend.app.models.tax import (
    TaxCalculationInput, 
    RegimeTaxResult, 
    SlabBreakdown, 
    TaxOptimizationComparison
)
from backend.app.services.rule_engine import rule_engine

def calculate_slab_tax(taxable_income: float, slabs: List[Dict[str, Any]]) -> Tuple[float, List[SlabBreakdown]]:
    """
    Computes progressive slab tax bracket by bracket and returns the itemized breakdown.
    """
    total_tax = 0.0
    breakdowns: List[SlabBreakdown] = []

    for s in slabs:
        s_min = float(s["min"])
        s_max = float(s["max"]) if s.get("max") is not None else float("inf")
        rate = float(s["rate"])

        if taxable_income > s_min:
            taxable_in_slab = min(taxable_income, s_max) - s_min
            tax_for_slab = taxable_in_slab * rate
            total_tax += tax_for_slab

            range_label = f"₹{int(s_min):,} - ₹{int(s_max):,}" if s_max != float("inf") else f"Above ₹{int(s_min):,}"
            breakdowns.append(SlabBreakdown(
                slab_range=range_label,
                taxable_amount_in_slab=round(taxable_in_slab, 2),
                tax_rate=round(rate * 100, 1),
                tax_computed=round(tax_for_slab, 2)
            ))

    return round(total_tax, 2), breakdowns

def compute_new_regime_tax(inp: TaxCalculationInput, rules: Dict[str, Any]) -> RegimeTaxResult:
    """
    Computes tax under the New Tax Regime (Section 115BAC).
    Includes revised standard deduction (₹75k for AY 2025-26) and Section 87A rebate up to ₹7L.
    """
    # Gross Income
    total_other = inp.savings_interest + inp.fd_interest + inp.dividend_income + inp.other_income
    gross_total = inp.gross_salary + total_other

    # Standard Deduction in New Regime (only for salaried/pensioners)
    std_ded = float(rules.get("standard_deduction", {}).get("salaried_new_regime", 75000)) if inp.gross_salary > 0 else 0.0
    std_ded = min(std_ded, inp.gross_salary)

    # In New Regime, Chapter VI-A (80C, 80D), HRA, and 24(b) are forfeited
    total_exemptions = std_ded
    net_taxable_income = max(0.0, gross_total - total_exemptions)
    
    # Round to nearest 10 (Indian Income Tax Rule)
    net_taxable_income = round(net_taxable_income / 10) * 10

    # Calculate Slab Tax
    slabs = rules.get("tax_slabs", {}).get("new_regime", [])
    tax_before_rebate, slab_breakdowns = calculate_slab_tax(net_taxable_income, slabs)

    # Section 87A Rebate in New Regime
    rebate_threshold = float(rules.get("rebate_87a", {}).get("new_regime", {}).get("threshold_income", 700000))
    rebate_max = float(rules.get("rebate_87a", {}).get("new_regime", {}).get("max_rebate", 25000))
    rebate_87a = 0.0

    if net_taxable_income <= rebate_threshold:
        rebate_87a = min(tax_before_rebate, rebate_max)
    elif net_taxable_income > rebate_threshold:
        # Marginal relief under Section 87A for income marginally exceeding ₹7L
        excess_income = net_taxable_income - rebate_threshold
        if tax_before_rebate > excess_income:
            # Tax payable cannot exceed excess income over 7 Lakh
            rebate_87a = tax_before_rebate - excess_income

    tax_after_rebate = max(0.0, tax_before_rebate - rebate_87a)

    # Surcharge
    surcharge = 0.0
    if net_taxable_income > 5000000:
        if net_taxable_income <= 10000000:
            surcharge = tax_after_rebate * 0.10
        elif net_taxable_income <= 20000000:
            surcharge = tax_after_rebate * 0.15
        else:
            surcharge = tax_after_rebate * 0.25  # Capped at 25% in New Regime

    # Health & Education Cess (4%)
    cess_rate = float(rules.get("cess_rate", 0.04))
    cess = round((tax_after_rebate + surcharge) * cess_rate, 2)
    total_tax_liability = round(tax_after_rebate + surcharge + cess, 2)

    total_taxes_paid = inp.tds_already_paid + inp.advance_tax_paid
    net_payable = max(0.0, round(total_tax_liability - total_taxes_paid, 2))
    refund_due = max(0.0, round(total_taxes_paid - total_tax_liability, 2))

    return RegimeTaxResult(
        regime_name="New Tax Regime (Section 115BAC)",
        is_default=True,
        gross_total_income=round(gross_total, 2),
        standard_deduction=round(std_ded, 2),
        total_exemptions_and_deductions=round(total_exemptions, 2),
        net_taxable_income=round(net_taxable_income, 2),
        slab_breakdown=slab_breakdowns,
        tax_before_rebate=round(tax_before_rebate, 2),
        rebate_87a=round(rebate_87a, 2),
        tax_after_rebate=round(tax_after_rebate, 2),
        surcharge=round(surcharge, 2),
        cess_4_percent=round(cess, 2),
        total_tax_liability=total_tax_liability,
        total_taxes_paid=round(total_taxes_paid, 2),
        net_tax_payable=net_payable,
        refund_due=refund_due
    )

def compute_old_regime_tax(inp: TaxCalculationInput, rules: Dict[str, Any]) -> RegimeTaxResult:
    """
    Computes tax under the Old Tax Regime with Chapter VI-A deductions,
    HRA exemptions, 24(b) home loan interest, and Section 87A rebate up to ₹5L.
    """
    # Gross Income
    total_other = inp.savings_interest + inp.fd_interest + inp.dividend_income + inp.other_income
    gross_total = inp.gross_salary + total_other

    # Section 10 Exemptions
    sec10_exemptions = inp.hra_exemption + inp.lta_exemption
    
    # Standard Deduction in Old Regime (₹50k for salaried)
    std_ded = float(rules.get("standard_deduction", {}).get("salaried_old_regime", 50000)) if inp.gross_salary > 0 else 0.0
    prof_tax = inp.professional_tax
    salary_deductions = sec10_exemptions + std_ded + prof_tax

    # Home Loan Interest u/s 24(b) (max 2L for self-occupied)
    hl_cap = float(rules.get("deduction_limits", {}).get("section_24b_home_loan_interest", 200000))
    ded_24b = min(inp.home_loan_interest_24b, hl_cap)

    # Chapter VI-A Deductions
    cap_80c = float(rules.get("deduction_limits", {}).get("section_80c", 150000))
    ded_80c = min(inp.deduction_80c, cap_80c)

    cap_80ccd = float(rules.get("deduction_limits", {}).get("section_80ccd_1b", 50000))
    ded_80ccd = min(inp.deduction_80ccd_1b, cap_80ccd)

    ded_80d = min(inp.deduction_80d, 75000.0)  # Self (25k) + Senior Parents (50k)

    # Section 80TTA (Savings Interest deduction up to 10k)
    cap_80tta = float(rules.get("deduction_limits", {}).get("section_80tta_savings_interest", 10000))
    ded_80tta = min(inp.savings_interest, cap_80tta)

    other_via = inp.deduction_80e + inp.deduction_80g
    total_via_deductions = ded_80c + ded_80ccd + ded_80d + ded_80tta + other_via

    total_exemptions_and_deductions = salary_deductions + ded_24b + total_via_deductions
    net_taxable_income = max(0.0, gross_total - total_exemptions_and_deductions)
    
    # Round to nearest 10
    net_taxable_income = round(net_taxable_income / 10) * 10

    # Calculate Slab Tax
    slabs = rules.get("tax_slabs", {}).get("old_regime", [])
    tax_before_rebate, slab_breakdowns = calculate_slab_tax(net_taxable_income, slabs)

    # Section 87A Rebate in Old Regime (Rebate up to ₹12,500 if income <= 5L)
    rebate_threshold = float(rules.get("rebate_87a", {}).get("old_regime", {}).get("threshold_income", 500000))
    rebate_max = float(rules.get("rebate_87a", {}).get("old_regime", {}).get("max_rebate", 12500))
    rebate_87a = 0.0

    if net_taxable_income <= rebate_threshold:
        rebate_87a = min(tax_before_rebate, rebate_max)

    tax_after_rebate = max(0.0, tax_before_rebate - rebate_87a)

    # Surcharge
    surcharge = 0.0
    if net_taxable_income > 5000000:
        if net_taxable_income <= 10000000:
            surcharge = tax_after_rebate * 0.10
        elif net_taxable_income <= 20000000:
            surcharge = tax_after_rebate * 0.15
        elif net_taxable_income <= 50000000:
            surcharge = tax_after_rebate * 0.25
        else:
            surcharge = tax_after_rebate * 0.37  # 37% surcharge in Old Regime for >5Cr

    # Health & Education Cess (4%)
    cess_rate = float(rules.get("cess_rate", 0.04))
    cess = round((tax_after_rebate + surcharge) * cess_rate, 2)
    total_tax_liability = round(tax_after_rebate + surcharge + cess, 2)

    total_taxes_paid = inp.tds_already_paid + inp.advance_tax_paid
    net_payable = max(0.0, round(total_tax_liability - total_taxes_paid, 2))
    refund_due = max(0.0, round(total_taxes_paid - total_tax_liability, 2))

    return RegimeTaxResult(
        regime_name="Old Tax Regime",
        is_default=False,
        gross_total_income=round(gross_total, 2),
        standard_deduction=round(std_ded, 2),
        total_exemptions_and_deductions=round(total_exemptions_and_deductions, 2),
        net_taxable_income=round(net_taxable_income, 2),
        slab_breakdown=slab_breakdowns,
        tax_before_rebate=round(tax_before_rebate, 2),
        rebate_87a=round(rebate_87a, 2),
        tax_after_rebate=round(tax_after_rebate, 2),
        surcharge=round(surcharge, 2),
        cess_4_percent=round(cess, 2),
        total_tax_liability=total_tax_liability,
        total_taxes_paid=round(total_taxes_paid, 2),
        net_tax_payable=net_payable,
        refund_due=refund_due
    )

def optimize_tax_regimes(inp: TaxCalculationInput) -> TaxOptimizationComparison:
    """
    Computes both regimes side-by-side using dynamic rules, determines the optimal regime,
    calculates breakeven deduction points, and provides tailored recommendations.
    """
    rules = rule_engine.get_rules(inp.assessment_year)
    
    new_res = compute_new_regime_tax(inp, rules)
    old_res = compute_old_regime_tax(inp, rules)

    savings = round(abs(new_res.total_tax_liability - old_res.total_tax_liability), 2)
    recommendations: List[str] = []

    # Determine Winner
    if new_res.total_tax_liability < old_res.total_tax_liability:
        recommended = "NEW"
        rec_title = "New Tax Regime (Section 115BAC)"
        verdict = f"Choosing the New Tax Regime saves you ₹{savings:,.2f} in tax! It is also the default regime on the e-filing portal."
    elif old_res.total_tax_liability < new_res.total_tax_liability:
        recommended = "OLD"
        rec_title = "Old Tax Regime"
        verdict = f"Choosing the Old Tax Regime saves you ₹{savings:,.2f} in tax because your deductions and HRA exemptions exceed the New Regime advantage."
    else:
        recommended = "NEW"
        rec_title = "New Tax Regime (Section 115BAC)"
        verdict = "Both regimes result in the exact same tax liability. We recommend New Regime as it requires no proof verification on the portal."

    # Breakeven Deduction Calculation
    # Iteratively find how much total deduction is required in Old Regime to match New Regime tax
    breakeven_deductions = 0.0
    gross = new_res.gross_total_income
    
    if gross > 775000:
        # Binary search / step search for breakeven
        low_d = 0.0
        high_d = gross
        for _ in range(25):
            mid_d = (low_d + high_d) / 2
            test_inp = inp.model_copy(update={
                "deduction_80c": min(150000, mid_d),
                "hra_exemption": max(0, mid_d - 150000)
            })
            test_old = compute_old_regime_tax(test_inp, rules)
            if test_old.total_tax_liability > new_res.total_tax_liability:
                low_d = mid_d
            else:
                high_d = mid_d
        breakeven_deductions = round(high_d, 2)

    current_deductions = old_res.total_exemptions_and_deductions
    deduction_gap = max(0.0, round(breakeven_deductions - current_deductions, 2))

    if recommended == "NEW" and deduction_gap > 0 and gross > 775000:
        recommendations.append(
            f"Breakeven Insight: You would need at least ₹{breakeven_deductions:,.2f} in total deductions (HRA + 80C + 80D + 24(b)) for the Old Regime to match the New Regime. Your current deductions are ₹{current_deductions:,.2f} (Gap: ₹{deduction_gap:,.2f})."
        )
    elif recommended == "OLD":
        recommendations.append(
            "Portal Action: To opt for the Old Tax Regime on the official portal, you must explicitly opt out of Section 115BAC in the return filing wizard."
        )

    # 80CCD(1B) NPS tip
    if inp.deduction_80ccd_1b < 50000 and recommended == "OLD":
        nps_gap = 50000 - inp.deduction_80ccd_1b
        recommendations.append(
            f"Tax Saving Tip: You can save up to ₹{nps_gap * 0.312:,.2f} more tax under Old Regime by investing ₹{nps_gap:,.2f} in National Pension System (NPS) u/s 80CCD(1B)."
        )

    return TaxOptimizationComparison(
        assessment_year=inp.assessment_year,
        recommended_regime=recommended,
        recommended_regime_title=rec_title,
        tax_savings_amount=savings,
        summary_verdict=verdict,
        new_regime=new_res,
        old_regime=old_res,
        breakeven_deductions_needed=breakeven_deductions,
        current_old_regime_deductions=current_deductions,
        deduction_gap_to_beat_new_regime=deduction_gap,
        key_recommendations=recommendations
    )

