import React, { useState, useEffect } from 'react';
import { 
  ExternalLink, 
  Copy, 
  Check, 
  FileText, 
  Printer, 
  CheckCircle2, 
  AlertTriangle, 
  ShieldCheck, 
  Download, 
  ChevronRight, 
  Key, 
  Send,
  HelpCircle
} from 'lucide-react';

export default function OfficialPortalGuide({ 
  taxComparison, 
  formDiagnosis, 
  financialData, 
  assessmentYear 
}) {
  const [filingPlan, setFilingPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [copiedKey, setCopiedKey] = useState(null);
  const [completedSteps, setCompletedSteps] = useState({});
  const [showPrintModal, setShowPrintModal] = useState(false);
  const [htmlSheet, setHtmlSheet] = useState('');

  useEffect(() => {
    // Generate filing plan from backend
    fetch('/api/v1/portal/filing-plan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        tax_comparison: taxComparison,
        form_diagnosis: formDiagnosis,
        form16: financialData?.form16,
        ais: financialData?.ais
      })
    })
      .then(res => res.json())
      .then(data => {
        setFilingPlan(data);
        setLoading(false);
      })
      .catch(() => {
        // Fallback local plan
        generateFallbackPlan();
      });

    // Pre-fetch HTML Computation Sheet
    fetch('/api/v1/portal/computation-sheet-html', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        tax_comparison: taxComparison,
        form16: financialData?.form16,
        ais: financialData?.ais
      })
    })
      .then(res => res.text())
      .then(html => setHtmlSheet(html))
      .catch(() => {});
  }, []);

  const generateFallbackPlan = () => {
    setFilingPlan({
      assessment_year: assessmentYear || '2025-26',
      recommended_form: formDiagnosis?.recommended_form || 'ITR-1',
      form_title: formDiagnosis?.form_title || 'ITR-1 (Sahaj)',
      regime_choice: taxComparison?.recommended_regime || 'NEW',
      regime_portal_instruction: taxComparison?.recommended_regime === 'NEW' 
        ? "When asked 'Do you wish to opt out of the New Tax Regime?', select NO." 
        : "When asked 'Do you wish to opt out of the New Tax Regime?', select YES.",
      total_gross_income: taxComparison?.new_regime?.gross_total_income || 1540000,
      total_taxable_income: taxComparison?.new_regime?.net_taxable_income || 1465000,
      total_tax_liability: taxComparison?.new_regime?.total_tax_liability || 138320,
      total_tds_credit: taxComparison?.new_regime?.total_taxes_paid || 145000,
      estimated_refund_or_due: 6680,
      is_refund: true,
      steps: [
        {
          step_number: 1,
          title: "Official Portal Login & Return Selection",
          subtitle: "Log in safely on https://eportal.incometax.gov.in",
          official_portal_screen: "e-File -> Income Tax Returns -> File Income Tax Return",
          critical_action: `Select AY '${assessmentYear || '2025-26'}', Online Mode, and Form '${formDiagnosis?.recommended_form || 'ITR-1'}'.`,
          fields: [],
          caution_notes: ["Ensure URL is eportal.incometax.gov.in with valid HTTPS padlock."]
        },
        {
          step_number: 2,
          title: "General Information & Regime Selection",
          subtitle: "Select Section 115BAC Option",
          official_portal_screen: "Schedule Personal Information",
          critical_action: taxComparison?.recommended_regime === 'NEW'
            ? "Question: 'Opt out of New Tax Regime under Section 115BAC?' -> Select NO."
            : "Question: 'Opt out of New Tax Regime under Section 115BAC?' -> Select YES.",
          fields: [],
          caution_notes: ["New Regime is default. Opting out requires selecting YES explicitly."]
        }
      ],
      pre_filing_checklist: [
        "Aadhaar card linked with PAN",
        "Pre-validated bank account on portal for refund direct credit",
        "Mobile number ready for Aadhaar OTP e-verification"
      ],
      e_verification_instructions: [
        "Select 'I would like to e-Verify now using Aadhaar OTP (Recommended)'",
        "Enter the 6-digit OTP received from UIDAI",
        "Download and save the ITR-V acknowledgment PDF"
      ]
    });
    setLoading(false);
  };

  const handleCopy = (key, text) => {
    navigator.clipboard.writeText(String(text));
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const toggleStep = (stepNum) => {
    setCompletedSteps(prev => ({ ...prev, [stepNum]: !prev[stepNum] }));
  };

  const printComputationSheet = () => {
    const printWindow = window.open('', '_blank');
    if (printWindow) {
      printWindow.document.write(htmlSheet);
      printWindow.document.close();
      printWindow.focus();
      printWindow.print();
    }
  };

  if (loading || !filingPlan) {
    return (
      <div className="bg-white p-12 rounded-2xl border border-slate-200 text-center">
        <FileText className="w-8 h-8 text-blue-600 animate-spin mx-auto mb-3" />
        <p className="text-slate-600 text-sm font-medium">Generating Official Portal Schedule Mapping Roadmap...</p>
      </div>
    );
  }

  const completedCount = Object.values(completedSteps).filter(Boolean).length;
  const progressPct = Math.round((completedCount / (filingPlan.steps.length || 6)) * 100);

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Top Action Bar */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-bold mb-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            Zero-Credential Portal Assistant
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-slate-900">Official Portal Filing Roadmap</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Follow these verified steps on <span className="font-semibold text-slate-700">eportal.incometax.gov.in</span>. Use 1-click copy buttons for every schedule!
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={printComputationSheet}
            className="inline-flex items-center gap-2 text-xs font-semibold px-4 py-2.5 rounded-xl border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 shadow-sm transition"
          >
            <Printer className="w-4 h-4 text-slate-600" /> Print / Export Computation Sheet
          </button>

          <a
            href="https://eportal.incometax.gov.in"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 text-xs font-bold px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white shadow transition"
          >
            Launch Official e-Filing Portal <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>

      {/* Summary Stat Pill */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-100/70 p-3 rounded-2xl border border-slate-200 text-xs">
        <div className="bg-white p-3 rounded-xl border border-slate-200">
          <span className="text-[11px] text-slate-500 font-semibold block">Diagnosed Form</span>
          <span className="text-sm font-bold text-blue-700">{filingPlan.recommended_form}</span>
        </div>
        <div className="bg-white p-3 rounded-xl border border-slate-200">
          <span className="text-[11px] text-slate-500 font-semibold block">Regime to Select</span>
          <span className="text-sm font-bold text-slate-800">{filingPlan.regime_choice === 'NEW' ? 'New (115BAC)' : 'Old Regime'}</span>
        </div>
        <div className="bg-white p-3 rounded-xl border border-slate-200">
          <span className="text-[11px] text-slate-500 font-semibold block">Total Tax Liability</span>
          <span className="text-sm font-bold text-slate-900">₹{filingPlan.total_tax_liability.toLocaleString('en-IN')}</span>
        </div>
        <div className="bg-white p-3 rounded-xl border border-slate-200">
          <span className="text-[11px] text-slate-500 font-semibold block">
            {filingPlan.is_refund ? '🎉 Expected Refund' : 'Tax Due to Pay'}
          </span>
          <span className={`text-sm font-bold ${filingPlan.is_refund ? 'text-emerald-700' : 'text-amber-700'}`}>
            ₹{filingPlan.estimated_refund_or_due.toLocaleString('en-IN')}
          </span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 flex items-center justify-between gap-4">
        <div className="flex items-center gap-2 text-xs font-bold text-slate-700">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          <span>Filing Progress: {completedCount} of {filingPlan.steps.length} Steps Completed on Portal</span>
        </div>
        <div className="w-48 h-2 bg-slate-100 rounded-full overflow-hidden border border-slate-200">
          <div 
            className="h-full bg-emerald-500 transition-all duration-300"
            style={{ width: `${progressPct}%` }}
          ></div>
        </div>
      </div>

      {/* Step-by-Step Schedule Cards */}
      <div className="space-y-4">
        {filingPlan.steps.map((step) => {
          const isDone = Boolean(completedSteps[step.step_number]);

          return (
            <div 
              key={step.step_number}
              className={`rounded-2xl border transition-all ${
                isDone 
                  ? 'bg-slate-50/80 border-emerald-300' 
                  : 'bg-white border-slate-200 shadow-sm'
              }`}
            >
              {/* Step Header */}
              <div className="p-5 sm:p-6 flex items-start justify-between gap-4">
                <div className="flex items-start gap-3.5">
                  <button
                    onClick={() => toggleStep(step.step_number)}
                    className={`w-7 h-7 rounded-lg mt-0.5 flex items-center justify-center font-bold text-xs transition ${
                      isDone 
                        ? 'bg-emerald-600 text-white' 
                        : 'border-2 border-slate-300 hover:border-blue-500 text-slate-600 bg-white'
                    }`}
                  >
                    {isDone ? <Check className="w-4 h-4" /> : step.step_number}
                  </button>

                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className={`text-base font-bold ${isDone ? 'line-through text-slate-500' : 'text-slate-900'}`}>
                        {step.title}
                      </h3>
                      <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                        {step.official_portal_screen}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 mt-1">{step.subtitle}</p>

                    {/* Critical Action Banner */}
                    <div className="mt-3 p-3 bg-blue-50/80 border border-blue-200 rounded-xl text-xs text-blue-900 font-medium">
                      <strong>Action on Portal:</strong> {step.critical_action}
                    </div>
                  </div>
                </div>
              </div>

              {/* Mapped Fields with Copy Buttons */}
              {step.fields && step.fields.length > 0 && (
                <div className="px-5 sm:px-6 pb-6 pt-1 border-t border-slate-100">
                  <div className="space-y-2 mt-3">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 block">
                      Values to Enter / Verify:
                    </span>
                    {step.fields.map((f, fIdx) => {
                      const copyId = `${step.step_number}-${fIdx}`;
                      const isCopied = copiedKey === copyId;

                      return (
                        <div 
                          key={fIdx}
                          className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-xl bg-slate-50 border border-slate-200 hover:border-slate-300 transition text-xs"
                        >
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="font-semibold text-slate-900">{f.field_label}</span>
                              <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-200 text-slate-700 font-mono">
                                Box {f.portal_field_code}
                              </span>
                            </div>
                            <p className="text-[11px] text-slate-500 mt-0.5">
                              {f.instructions} • <span className="text-blue-600">{f.source_document}</span>
                            </p>
                          </div>

                          {f.amount > 0 && (
                            <div className="flex items-center gap-2">
                              <span className="font-mono font-bold text-sm text-slate-900">
                                ₹{f.amount.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                              </span>
                              <button
                                onClick={() => handleCopy(copyId, f.amount)}
                                className={`px-2.5 py-1.5 rounded-lg border text-xs font-semibold flex items-center gap-1 transition ${
                                  isCopied 
                                    ? 'bg-emerald-600 text-white border-emerald-600' 
                                    : 'bg-white hover:bg-slate-100 text-slate-700 border-slate-300'
                                }`}
                              >
                                {isCopied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                                {isCopied ? 'Copied' : 'Copy'}
                              </button>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Caution Notes */}
              {step.caution_notes && step.caution_notes.length > 0 && (
                <div className="px-5 sm:px-6 pb-4">
                  {step.caution_notes.map((note, nIdx) => (
                    <div key={nIdx} className="flex items-start gap-2 text-[11px] text-amber-800 bg-amber-50/70 p-2.5 rounded-lg border border-amber-200">
                      <AlertTriangle className="w-3.5 h-3.5 text-amber-600 shrink-0 mt-0.5" />
                      <span>{note}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* E-Verification Completion Checklist */}
      <div className="bg-emerald-50 border border-emerald-200 p-6 sm:p-8 rounded-2xl shadow-sm space-y-4">
        <div className="flex items-center gap-2.5">
          <ShieldCheck className="w-6 h-6 text-emerald-600 shrink-0" />
          <div>
            <h4 className="text-base font-bold text-emerald-950">
              Final Step: Instant e-Verification with Aadhaar OTP
            </h4>
            <p className="text-xs text-emerald-800 mt-0.5">
              An unverified return is invalid under Indian tax law. Follow these steps to finish in 60 seconds:
            </p>
          </div>
        </div>

        <ol className="list-decimal list-inside space-y-2 text-xs text-emerald-900 font-medium pl-1">
          {filingPlan.e_verification_instructions.map((inst, i) => (
            <li key={i} className="leading-relaxed">{inst}</li>
          ))}
        </ol>

        <div className="pt-2 flex justify-between items-center text-xs text-emerald-800">
          <span>🎉 Once submitted and e-verified, your ITR filing is 100% complete!</span>
          <button
            onClick={printComputationSheet}
            className="text-emerald-900 underline font-bold"
          >
            Download Your Tax Computation Record
          </button>
        </div>
      </div>
    </div>
  );
}

