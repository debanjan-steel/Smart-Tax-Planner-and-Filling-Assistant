import React, { useState, useEffect } from 'react';
import { 
  Calculator, 
  TrendingDown, 
  Trophy, 
  Sparkles, 
  CheckCircle2, 
  ArrowRight, 
  ChevronDown, 
  ChevronUp, 
  ShieldCheck,
  AlertCircle,
  HelpCircle,
  IndianRupee,
  Layers,
  ArrowUpRight
} from 'lucide-react';
import { API_BASE } from '../config';

export default function TaxOptimizerEngine({ financialData, assessmentYear, onProceed }) {
  // Pre-fill from financialData (Form 16 + AIS) or defaults
  const f16 = financialData?.form16;
  const ais = financialData?.ais;

  const [inputs, setInputs] = useState({
    assessment_year: assessmentYear || '2025-26',
    gross_salary: f16?.salary_breakup?.gross_salary_sec17_1 || 1540000,
    savings_interest: ais?.total_savings_interest || 18450,
    fd_interest: ais?.total_fd_interest || 45000,
    dividend_income: ais?.total_dividend_income || 12500,
    other_income: 0,
    hra_exemption: f16?.salary_breakup?.hra_exempt_sec10_13a || 140000,
    lta_exemption: 0,
    professional_tax: f16?.salary_breakup?.professional_tax_sec16_iii || 2400,
    deduction_80c: f16?.deductions?.section_80c || 150000,
    deduction_80ccd_1b: f16?.deductions?.section_80ccd_1b || 50000,
    deduction_80d: f16?.deductions?.section_80d_health_insurance || 25000,
    home_loan_interest_24b: f16?.deductions?.section_24b_house_loan_interest || 0,
    deduction_80e: 0,
    deduction_80g: 0,
    tds_already_paid: f16?.total_tds_deducted || ais?.total_tds_reported_ais || 132400,
    advance_tax_paid: 0
  });

  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showSlabsNew, setShowSlabsNew] = useState(false);
  const [showSlabsOld, setShowSlabsOld] = useState(false);
  const [activeTab, setActiveTab] = useState('summary'); // 'summary' or 'simulator'

  const runCalculation = (currInputs = inputs) => {
    setLoading(true);
    fetch(`${API_BASE}/api/v1/tax/calculate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(currInputs)
    })
      .then(res => res.json())
      .then(data => {
        setComparison(data);
        setLoading(false);
      })
      .catch(() => {
        // Fallback calculation
        fallbackCalculate(currInputs);
      });
  };

  const fallbackCalculate = (inp) => {
    // Standard Fallback calculation
    const is25 = inp.assessment_year === '2025-26';
    const stdNew = is25 ? 75000 : 50000;
    const gross = Number(inp.gross_salary) + Number(inp.savings_interest) + Number(inp.fd_interest) + Number(inp.dividend_income);
    
    // New Regime
    const taxableNew = Math.max(0, gross - stdNew);
    let taxNew = 0;
    if (taxableNew > 1500000) taxNew = 140000 + (taxableNew - 1500000) * 0.3;
    else if (taxableNew > 1200000) taxNew = 80000 + (taxableNew - 1200000) * 0.2;
    else if (taxableNew > 1000000) taxNew = 50000 + (taxableNew - 1000000) * 0.15;
    else if (taxableNew > 700000) taxNew = 20000 + (taxableNew - 700000) * 0.1;
    else if (taxableNew > 300000) taxNew = (taxableNew - 300000) * 0.05;

    let rebateNew = 0;
    if (taxableNew <= 700000) rebateNew = Math.min(taxNew, 25000);
    const taxAfterRebateNew = Math.max(0, taxNew - rebateNew);
    const cessNew = taxAfterRebateNew * 0.04;
    const totalNew = taxAfterRebateNew + cessNew;

    // Old Regime
    const totalDedsOld = 50000 + Math.min(150000, Number(inp.deduction_80c)) + Math.min(50000, Number(inp.deduction_80ccd_1b)) + Math.min(75000, Number(inp.deduction_80d)) + Number(inp.hra_exemption) + Number(inp.professional_tax);
    const taxableOld = Math.max(0, gross - totalDedsOld);
    let taxOld = 0;
    if (taxableOld > 1000000) taxOld = 112500 + (taxableOld - 1000000) * 0.3;
    else if (taxableOld > 500000) taxOld = 12500 + (taxableOld - 500000) * 0.2;
    else if (taxableOld > 250000) taxOld = (taxableOld - 250000) * 0.05;

    let rebateOld = 0;
    if (taxableOld <= 500000) rebateOld = Math.min(taxOld, 12500);
    const taxAfterRebateOld = Math.max(0, taxOld - rebateOld);
    const cessOld = taxAfterRebateOld * 0.04;
    const totalOld = taxAfterRebateOld + cessOld;

    const winner = totalNew <= totalOld ? 'NEW' : 'OLD';
    const diff = Math.abs(totalNew - totalOld);

    setComparison({
      assessment_year: inp.assessment_year,
      recommended_regime: winner,
      recommended_regime_title: winner === 'NEW' ? 'New Tax Regime (Section 115BAC)' : 'Old Tax Regime',
      tax_savings_amount: diff,
      summary_verdict: winner === 'NEW' 
        ? `New Regime saves you ₹${diff.toLocaleString('en-IN', { maximumFractionDigits: 0 })}!`
        : `Old Regime saves you ₹${diff.toLocaleString('en-IN', { maximumFractionDigits: 0 })}!`,
      new_regime: {
        regime_name: "New Tax Regime (Section 115BAC)",
        is_default: true,
        gross_total_income: gross,
        standard_deduction: stdNew,
        total_exemptions_and_deductions: stdNew,
        net_taxable_income: taxableNew,
        slab_breakdown: [],
        tax_before_rebate: taxNew,
        rebate_87a: rebateNew,
        tax_after_rebate: taxAfterRebateNew,
        surcharge: 0,
        cess_4_percent: cessNew,
        total_tax_liability: totalNew,
        total_taxes_paid: Number(inp.tds_already_paid),
        net_tax_payable: Math.max(0, totalNew - Number(inp.tds_already_paid)),
        refund_due: Math.max(0, Number(inp.tds_already_paid) - totalNew)
      },
      old_regime: {
        regime_name: "Old Tax Regime",
        is_default: false,
        gross_total_income: gross,
        standard_deduction: 50000,
        total_exemptions_and_deductions: totalDedsOld,
        net_taxable_income: taxableOld,
        slab_breakdown: [],
        tax_before_rebate: taxOld,
        rebate_87a: rebateOld,
        tax_after_rebate: taxAfterRebateOld,
        surcharge: 0,
        cess_4_percent: cessOld,
        total_tax_liability: totalOld,
        total_taxes_paid: Number(inp.tds_already_paid),
        net_tax_payable: Math.max(0, totalOld - Number(inp.tds_already_paid)),
        refund_due: Math.max(0, Number(inp.tds_already_paid) - totalOld)
      },
      breakeven_deductions_needed: 375000,
      current_old_regime_deductions: totalDedsOld,
      deduction_gap_to_beat_new_regime: Math.max(0, 375000 - totalDedsOld),
      key_recommendations: [
        winner === 'NEW' 
          ? "New Regime provides lower tax without needing to submit investment proof documents."
          : "You must explicitly opt out of Section 115BAC on the official portal to claim Old Regime."
      ]
    });
    setLoading(false);
  };

  useEffect(() => {
    runCalculation(inputs);
  }, [inputs.assessment_year]);

  const handleInputChange = (field, val) => {
    const updated = { ...inputs, [field]: Number(val) || 0 };
    setInputs(updated);
    runCalculation(updated);
  };

  if (loading && !comparison) {
    return (
      <div className="bg-white p-12 rounded-2xl border border-slate-200 text-center">
        <Sparkles className="w-8 h-8 text-blue-600 animate-spin mx-auto mb-3" />
        <p className="text-slate-600 text-sm font-medium">Computing comparative tax regimes...</p>
      </div>
    );
  }

  const isNewWinner = comparison?.recommended_regime === 'NEW';
  const newReg = comparison?.new_regime;
  const oldReg = comparison?.old_regime;

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Winner Hero Banner */}
      <div className="bg-gradient-to-r from-blue-900 via-indigo-900 to-slate-900 text-white p-6 sm:p-8 rounded-2xl shadow-md relative overflow-hidden">
        <div className="relative z-10">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/20 border border-emerald-400/40 text-emerald-300 text-xs font-bold mb-3 uppercase tracking-wider">
            <Trophy className="w-3.5 h-3.5 text-emerald-400" />
            Tax Optimization Recommendation
          </div>

          <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            {comparison?.recommended_regime_title} Saves You{' '}
            <span className="text-emerald-400">₹{comparison?.tax_savings_amount?.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</span>
          </h2>
          <p className="text-slate-300 text-sm mt-2 max-w-2xl leading-relaxed">
            {comparison?.summary_verdict}
          </p>

          <div className="mt-5 flex flex-wrap items-center gap-3">
            <span className="text-xs bg-white/10 px-3 py-1.5 rounded-lg border border-white/20">
              Assessment Year: <strong>{inputs.assessment_year}</strong>
            </span>
            <span className="text-xs bg-white/10 px-3 py-1.5 rounded-lg border border-white/20">
              Gross Total Income: <strong>₹{newReg?.gross_total_income?.toLocaleString('en-IN')}</strong>
            </span>
          </div>
        </div>
      </div>

      {/* Tabs Switcher: Side-by-Side Summary vs Interactive Deduction Simulator */}
      <div className="flex border-b border-slate-200 gap-6 text-sm font-bold">
        <button
          onClick={() => setActiveTab('summary')}
          className={`pb-3 border-b-2 transition ${
            activeTab === 'summary' ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          Side-by-Side Regime Comparison
        </button>
        <button
          onClick={() => setActiveTab('simulator')}
          className={`pb-3 border-b-2 transition flex items-center gap-1.5 ${
            activeTab === 'simulator' ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Calculator className="w-4 h-4" /> Interactive Deduction Simulator
        </button>
      </div>

      {/* TAB 1: SIDE-BY-SIDE REGIME COMPARISON */}
      {activeTab === 'summary' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* NEW TAX REGIME CARD */}
          <div className={`rounded-2xl border p-6 flex flex-col justify-between transition-all ${
            isNewWinner 
              ? 'bg-white border-emerald-400 shadow-md ring-2 ring-emerald-100' 
              : 'bg-slate-50/60 border-slate-200'
          }`}>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold uppercase tracking-wider text-blue-700 bg-blue-50 border border-blue-200 px-2.5 py-0.5 rounded-full">
                  Section 115BAC (Default)
                </span>
                {isNewWinner && (
                  <span className="text-xs font-bold text-emerald-700 bg-emerald-50 border border-emerald-300 px-2.5 py-0.5 rounded-full flex items-center gap-1">
                    <Trophy className="w-3.5 h-3.5" /> Best Choice
                  </span>
                )}
              </div>

              <h3 className="text-lg font-bold text-slate-900">New Tax Regime</h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Lower slab rates with ₹75,000 Standard Deduction (No proofs needed).
              </p>

              {/* Numbers Table */}
              <div className="mt-5 space-y-2.5 text-xs">
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">Gross Income:</span>
                  <span className="font-semibold text-slate-800">₹{newReg?.gross_total_income?.toLocaleString('en-IN')}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">Standard Deduction (16(ia)):</span>
                  <span className="font-semibold text-emerald-700">-₹{newReg?.standard_deduction?.toLocaleString('en-IN')}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500 font-bold">Net Taxable Income:</span>
                  <span className="font-bold text-slate-900">₹{newReg?.net_taxable_income?.toLocaleString('en-IN')}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">Slab Tax (before rebate):</span>
                  <span className="font-semibold text-slate-800">₹{newReg?.tax_before_rebate?.toLocaleString('en-IN')}</span>
                </div>
                {newReg?.rebate_87a > 0 && (
                  <div className="flex justify-between py-1.5 border-b border-slate-100 text-emerald-700">
                    <span>Rebate u/s 87A (Up to ₹7L):</span>
                    <span className="font-bold">-₹{newReg?.rebate_87a?.toLocaleString('en-IN')}</span>
                  </div>
                )}
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">Health & Education Cess (4%):</span>
                  <span className="font-semibold text-slate-800">₹{newReg?.cess_4_percent?.toLocaleString('en-IN')}</span>
                </div>

                {/* Total Tax Liability Highlight */}
                <div className="pt-2 flex justify-between items-center text-sm font-extrabold">
                  <span className="text-slate-900">Total Tax Liability:</span>
                  <span className={isNewWinner ? 'text-emerald-700 text-lg' : 'text-slate-800 text-base'}>
                    ₹{newReg?.total_tax_liability?.toLocaleString('en-IN')}
                  </span>
                </div>

                {/* Refund vs Due */}
                <div className="mt-3 p-3 rounded-xl bg-slate-50 border border-slate-200">
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-600">TDS Already Deducted:</span>
                    <span className="font-semibold text-slate-800">₹{newReg?.total_taxes_paid?.toLocaleString('en-IN')}</span>
                  </div>
                  {newReg?.refund_due > 0 ? (
                    <div className="flex justify-between text-xs font-bold text-emerald-700 mt-1.5 pt-1.5 border-t border-slate-200">
                      <span>🎉 Estimated Refund Due:</span>
                      <span>₹{newReg?.refund_due?.toLocaleString('en-IN')}</span>
                    </div>
                  ) : (
                    <div className="flex justify-between text-xs font-bold text-amber-700 mt-1.5 pt-1.5 border-t border-slate-200">
                      <span>Self-Assessment Tax Payable:</span>
                      <span>₹{newReg?.net_tax_payable?.toLocaleString('en-IN')}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Slabs Accordion */}
            <div className="mt-4 pt-3 border-t border-slate-100">
              <button
                onClick={() => setShowSlabsNew(!showSlabsNew)}
                className="text-xs text-blue-600 hover:underline flex items-center gap-1 font-semibold"
              >
                {showSlabsNew ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                {showSlabsNew ? 'Hide Slab Details' : 'View Slab Breakdown'}
              </button>

              {showSlabsNew && newReg?.slab_breakdown && (
                <div className="mt-3 space-y-1 text-[11px] bg-slate-50 p-2.5 rounded-lg border border-slate-200">
                  {newReg.slab_breakdown.map((sb, idx) => (
                    <div key={idx} className="flex justify-between text-slate-600">
                      <span>{sb.slab_range} ({sb.tax_rate}%):</span>
                      <span className="font-semibold">₹{sb.tax_computed.toLocaleString('en-IN')}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* OLD TAX REGIME CARD */}
          <div className={`rounded-2xl border p-6 flex flex-col justify-between transition-all ${
            !isNewWinner 
              ? 'bg-white border-emerald-400 shadow-md ring-2 ring-emerald-100' 
              : 'bg-slate-50/60 border-slate-200'
          }`}>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-600 bg-slate-200 px-2.5 py-0.5 rounded-full">
                  Exemptions & Deductions
                </span>
                {!isNewWinner && (
                  <span className="text-xs font-bold text-emerald-700 bg-emerald-50 border border-emerald-300 px-2.5 py-0.5 rounded-full flex items-center gap-1">
                    <Trophy className="w-3.5 h-3.5" /> Best Choice
                  </span>
                )}
              </div>

              <h3 className="text-lg font-bold text-slate-900">Old Tax Regime</h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Allows 80C, 80D, HRA, Home Loan Interest (Requires proof submission).
              </p>

              {/* Numbers Table */}
              <div className="mt-5 space-y-2.5 text-xs">
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">Gross Income:</span>
                  <span className="font-semibold text-slate-800">₹{oldReg?.gross_total_income?.toLocaleString('en-IN')}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">Standard Deduction (16(ia)):</span>
                  <span className="font-semibold text-emerald-700">-₹{oldReg?.standard_deduction?.toLocaleString('en-IN')}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">Total Deductions (80C, 80D, HRA):</span>
                  <span className="font-semibold text-emerald-700">-₹{(oldReg?.total_exemptions_and_deductions - oldReg?.standard_deduction)?.toLocaleString('en-IN')}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500 font-bold">Net Taxable Income:</span>
                  <span className="font-bold text-slate-900">₹{oldReg?.net_taxable_income?.toLocaleString('en-IN')}</span>
                </div>
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">Slab Tax (before rebate):</span>
                  <span className="font-semibold text-slate-800">₹{oldReg?.tax_before_rebate?.toLocaleString('en-IN')}</span>
                </div>
                {oldReg?.rebate_87a > 0 && (
                  <div className="flex justify-between py-1.5 border-b border-slate-100 text-emerald-700">
                    <span>Rebate u/s 87A (Up to ₹5L):</span>
                    <span className="font-bold">-₹{oldReg?.rebate_87a?.toLocaleString('en-IN')}</span>
                  </div>
                )}
                <div className="flex justify-between py-1.5 border-b border-slate-100">
                  <span className="text-slate-500">Health & Education Cess (4%):</span>
                  <span className="font-semibold text-slate-800">₹{oldReg?.cess_4_percent?.toLocaleString('en-IN')}</span>
                </div>

                {/* Total Tax Liability Highlight */}
                <div className="pt-2 flex justify-between items-center text-sm font-extrabold">
                  <span className="text-slate-900">Total Tax Liability:</span>
                  <span className={!isNewWinner ? 'text-emerald-700 text-lg' : 'text-slate-800 text-base'}>
                    ₹{oldReg?.total_tax_liability?.toLocaleString('en-IN')}
                  </span>
                </div>

                {/* Refund vs Due */}
                <div className="mt-3 p-3 rounded-xl bg-slate-50 border border-slate-200">
                  <div className="flex justify-between text-xs">
                    <span className="text-slate-600">TDS Already Deducted:</span>
                    <span className="font-semibold text-slate-800">₹{oldReg?.total_taxes_paid?.toLocaleString('en-IN')}</span>
                  </div>
                  {oldReg?.refund_due > 0 ? (
                    <div className="flex justify-between text-xs font-bold text-emerald-700 mt-1.5 pt-1.5 border-t border-slate-200">
                      <span>🎉 Estimated Refund Due:</span>
                      <span>₹{oldReg?.refund_due?.toLocaleString('en-IN')}</span>
                    </div>
                  ) : (
                    <div className="flex justify-between text-xs font-bold text-amber-700 mt-1.5 pt-1.5 border-t border-slate-200">
                      <span>Self-Assessment Tax Payable:</span>
                      <span>₹{oldReg?.net_tax_payable?.toLocaleString('en-IN')}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Slabs Accordion */}
            <div className="mt-4 pt-3 border-t border-slate-100">
              <button
                onClick={() => setShowSlabsOld(!showSlabsOld)}
                className="text-xs text-blue-600 hover:underline flex items-center gap-1 font-semibold"
              >
                {showSlabsOld ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                {showSlabsOld ? 'Hide Slab Details' : 'View Slab Breakdown'}
              </button>

              {showSlabsOld && oldReg?.slab_breakdown && (
                <div className="mt-3 space-y-1 text-[11px] bg-slate-50 p-2.5 rounded-lg border border-slate-200">
                  {oldReg.slab_breakdown.map((sb, idx) => (
                    <div key={idx} className="flex justify-between text-slate-600">
                      <span>{sb.slab_range} ({sb.tax_rate}%):</span>
                      <span className="font-semibold">₹{sb.tax_computed.toLocaleString('en-IN')}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: INTERACTIVE DEDUCTION SIMULATOR */}
      {activeTab === 'simulator' && (
        <div className="bg-white p-6 sm:p-8 rounded-2xl border border-slate-200 shadow-sm space-y-6">
          <div>
            <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
              <Calculator className="w-5 h-5 text-blue-600" />
              Adjust Deductions to See Live Impact
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Change numbers below to see if investing in NPS or increasing 80C changes your optimal tax regime.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
            <div>
              <label className="text-xs font-bold text-slate-700 block mb-1">Gross Salary (₹)</label>
              <input 
                type="number" 
                value={inputs.gross_salary}
                onChange={(e) => handleInputChange('gross_salary', e.target.value)}
                className="w-full text-xs p-2.5 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="text-xs font-bold text-slate-700 block mb-1">Section 80C (Max ₹1.5L)</label>
              <input 
                type="number" 
                max={150000}
                value={inputs.deduction_80c}
                onChange={(e) => handleInputChange('deduction_80c', e.target.value)}
                className="w-full text-xs p-2.5 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="text-xs font-bold text-slate-700 block mb-1">HRA Exempt u/s 10(13A)</label>
              <input 
                type="number" 
                value={inputs.hra_exemption}
                onChange={(e) => handleInputChange('hra_exemption', e.target.value)}
                className="w-full text-xs p-2.5 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="text-xs font-bold text-slate-700 block mb-1">Section 80D Health Insurance</label>
              <input 
                type="number" 
                value={inputs.deduction_80d}
                onChange={(e) => handleInputChange('deduction_80d', e.target.value)}
                className="w-full text-xs p-2.5 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="text-xs font-bold text-slate-700 block mb-1">Section 80CCD(1B) NPS (Max ₹50k)</label>
              <input 
                type="number" 
                max={50000}
                value={inputs.deduction_80ccd_1b}
                onChange={(e) => handleInputChange('deduction_80ccd_1b', e.target.value)}
                className="w-full text-xs p-2.5 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="text-xs font-bold text-slate-700 block mb-1">Home Loan Interest 24(b)</label>
              <input 
                type="number" 
                max={200000}
                value={inputs.home_loan_interest_24b}
                onChange={(e) => handleInputChange('home_loan_interest_24b', e.target.value)}
                className="w-full text-xs p-2.5 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Breakeven Insight Box */}
          {comparison?.deduction_gap_to_beat_new_regime > 0 && (
            <div className="p-4 rounded-xl bg-blue-50 border border-blue-200 text-xs text-blue-900 flex items-start gap-3">
              <Info className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
              <div>
                <strong>Breakeven Target:</strong> You need <strong>₹{comparison.breakeven_deductions_needed.toLocaleString('en-IN')}</strong> in total deductions before the Old Regime becomes more profitable than the New Regime.
                You are currently at <strong>₹{comparison.current_old_regime_deductions.toLocaleString('en-IN')}</strong> (Gap of ₹{comparison.deduction_gap_to_beat_new_regime.toLocaleString('en-IN')}).
              </div>
            </div>
          )}
        </div>
      )}

      {/* Key Portal Filing Instructions */}
      <div className="bg-white p-6 sm:p-8 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          Official Portal Filing Instructions
        </h4>

        <div className="space-y-2 text-xs text-slate-700">
          {comparison?.key_recommendations.map((rec, i) => (
            <div key={i} className="p-3 bg-slate-50 rounded-xl border border-slate-200">
              {rec}
            </div>
          ))}
          <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-200 text-emerald-900 font-medium">
            <strong>Portal Action:</strong> When you open the return filing form on <em>eportal.incometax.gov.in</em>, select <strong>{isNewWinner ? 'Opt in for Section 115BAC (New Regime - Default)' : 'Opt OUT of Section 115BAC to claim Old Regime'}</strong>.
          </div>
        </div>

        <div className="pt-4 flex justify-end">
          <button
            onClick={() => onProceed && onProceed(comparison)}
            className="inline-flex items-center gap-2 text-sm font-semibold px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white shadow transition"
          >
            Proceed to Official Portal Guide & Computation Sheet <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

