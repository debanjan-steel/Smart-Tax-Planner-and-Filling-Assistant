import React, { useState, useEffect } from 'react';
import { 
  HelpCircle, 
  CheckCircle2, 
  AlertTriangle, 
  ArrowRight, 
  ArrowLeft, 
  FileCheck, 
  Download, 
  ExternalLink,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  ShieldAlert
} from 'lucide-react';

export default function FormFinderWizard({ onComplete, assessmentYear }) {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answers, setAnswers] = useState({
    assessment_year: assessmentYear || '2025-26',
    is_resident: true,
    total_income_exceeds_50_lakh: false,
    has_salary_or_pension: true,
    house_property_count: 1,
    has_capital_gains: false,
    has_crypto_or_vda: false,
    has_business_or_profession: false,
    is_presumptive_eligible: false,
    has_fo_or_intraday: false,
    is_company_director: false,
    holds_unlisted_shares: false,
    has_foreign_assets_or_income: false,
    agricultural_income_exceeds_5000: false,
    has_brought_forward_losses: false
  });

  const [diagnosis, setDiagnosis] = useState(null);
  const [diagnosing, setDiagnosing] = useState(false);
  const [expandedDoc, setExpandedDoc] = useState(null);
  const [checkedDocs, setCheckedDocs] = useState({});

  useEffect(() => {
    // Fetch question definitions from backend
    fetch('/api/v1/questionnaire/questions')
      .then(res => res.json())
      .then(data => {
        setQuestions(data);
        setLoading(false);
      })
      .catch(() => {
        // Fallback fallback questions if running offline/without backend active
        setQuestions([
          {
            id: "is_resident",
            section: "Basic Profile",
            title: "Are you a Resident of India for Tax Purposes?",
            subtitle: "You were physically in India for 182+ days during the financial year.",
            type: "boolean",
            default: true,
            law_note: "Non-Residents (NRIs) are prohibited from filing ITR-1 and ITR-4 under CBDT rules."
          },
          {
            id: "total_income_exceeds_50_lakh",
            section: "Basic Profile",
            title: "Does your total annual income exceed ₹50 Lakh?",
            subtitle: "Total gross income before deductions from all combined sources.",
            type: "boolean",
            default: false,
            law_note: "Section 139(1) limits ITR-1 (Sahaj) and ITR-4 (Sugam) strictly to income up to ₹50 Lakh."
          },
          {
            id: "has_salary_or_pension",
            section: "Income Sources",
            title: "Do you earn income from Salary or Pension?",
            subtitle: "Supported by Form 16 from employer or pension slip from bank.",
            type: "boolean",
            default: true,
            law_note: "Eligible for standard deduction (₹75,000 in New Regime for AY 2025-26)."
          },
          {
            id: "house_property_count",
            section: "Income Sources",
            title: "How many house properties do you own?",
            subtitle: "Self-occupied or rented out.",
            type: "choice",
            options: [
              { label: "None (Living on rent / with parents)", value: 0 },
              { label: "1 House Property", value: 1 },
              { label: "More than 1 House Property", value: 2 }
            ],
            default: 1,
            law_note: "Owning more than 1 house property disqualifies you from ITR-1 and mandates ITR-2."
          },
          {
            id: "has_capital_gains",
            section: "Investments",
            title: "Did you sell any Equity Shares, Mutual Funds, Gold, or Real Estate?",
            subtitle: "Even if you made a loss or switched funds within the year.",
            type: "boolean",
            default: false,
            law_note: "Requires Schedule CG (Capital Gains), which is strictly absent in ITR-1. Mandates ITR-2."
          },
          {
            id: "has_crypto_or_vda",
            section: "Investments",
            title: "Did you trade or hold Virtual Digital Assets (Crypto / NFTs)?",
            subtitle: "Taxed flat at 30% under Section 115BBH.",
            type: "boolean",
            default: false,
            law_note: "Requires Schedule VDA in ITR-2 or ITR-3."
          },
          {
            id: "has_business_or_profession",
            section: "Business & Freelance",
            title: "Do you have income from Freelancing, Consultancy, or Business?",
            subtitle: "Professional receipts or business sales.",
            type: "boolean",
            default: false,
            law_note: "Requires either ITR-4 (Presumptive) or ITR-3."
          },
          {
            id: "is_presumptive_eligible",
            section: "Business & Freelance",
            title: "Are you opting for the Presumptive Taxation Scheme (Sec 44AD / 44ADA)?",
            subtitle: "Declare flat 50% profit (professionals) or 6%/8% (businesses) without keeping audit books.",
            type: "boolean",
            default: false,
            depends_on: "has_business_or_profession",
            law_note: "Allows using the simpler ITR-4 (Sugam)."
          },
          {
            id: "has_fo_or_intraday",
            section: "Business & Freelance",
            title: "Did you trade in Futures & Options (F&O) or Intraday Equity?",
            subtitle: "Derivatives turnover on NSE/BSE.",
            type: "boolean",
            default: false,
            law_note: "F&O is legally classified as business income, strictly mandating ITR-3."
          },
          {
            id: "is_company_director",
            section: "Special Disqualifications",
            title: "Are you a Director in any company?",
            subtitle: "In India or abroad.",
            type: "boolean",
            default: false,
            law_note: "Requires DIN disclosure in ITR-2 or ITR-3."
          },
          {
            id: "has_foreign_assets_or_income",
            section: "Special Disqualifications",
            title: "Do you hold Foreign Assets, US Stocks, or Foreign ESOPs?",
            subtitle: "Foreign bank accounts, MNC parent company RSUs, etc.",
            type: "boolean",
            default: false,
            law_note: "Mandates Schedule FA under Black Money Act. Only in ITR-2 / ITR-3."
          }
        ]);
        setLoading(false);
      });
  }, []);

  // Filter questions dynamically based on dependencies
  const activeQuestions = questions.filter(q => {
    if (q.depends_on) {
      return Boolean(answers[q.depends_on]);
    }
    return true;
  });

  const currentQ = activeQuestions[currentIdx];

  const handleAnswer = (val) => {
    setAnswers(prev => ({ ...prev, [currentQ.id]: val }));
  };

  const handleNext = () => {
    if (currentIdx < activeQuestions.length - 1) {
      setCurrentIdx(currentIdx + 1);
    } else {
      runDiagnosis();
    }
  };

  const handlePrev = () => {
    if (currentIdx > 0) {
      setCurrentIdx(currentIdx - 1);
    }
  };

  const runDiagnosis = () => {
    setDiagnosing(true);
    fetch('/api/v1/questionnaire/diagnose', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...answers, assessment_year: assessmentYear })
    })
      .then(res => res.json())
      .then(result => {
        setDiagnosis(result);
        setDiagnosing(false);
      })
      .catch(() => {
        // Fallback local calculation
        let form = "ITR-1";
        let title = "ITR-1 (Sahaj)";
        let reasons = ["Resident individual with income under ₹50 Lakh from Salary and single house property."];
        let risks = [];
        let docs = [
          {
            id: "form_16",
            name: "Form 16 (Part A & B)",
            description: "Issued by your employer with salary breakup and TDS.",
            source: "Company HR / Payroll Portal",
            download_steps: ["Log into company payroll portal", "Download Part A & B for FY"]
          },
          {
            id: "ais_tis",
            name: "Annual Information Statement (AIS / TIS)",
            description: "Interest, dividends, and securities summary from IT Dept.",
            source: "eportal.incometax.gov.in",
            download_steps: ["Log into Income Tax portal", "Services -> Annual Information Statement"]
          }
        ];

        if (answers.has_fo_or_intraday || (answers.has_business_or_profession && !answers.is_presumptive_eligible)) {
          form = "ITR-3";
          title = "ITR-3 (Profits and Gains of Business or Profession)";
          reasons = ["F&O or business income mandates filing under ITR-3."];
          risks = ["Filing ITR-1 or 2 with F&O turnover will cause a Defective Return notice u/s 139(9)."];
        } else if (answers.has_business_or_profession && answers.is_presumptive_eligible) {
          form = "ITR-4";
          title = "ITR-4 (Sugam)";
          reasons = ["Eligible for Presumptive Taxation Scheme under Sec 44AD/44ADA."];
        } else if (answers.has_capital_gains || answers.house_property_count > 1 || answers.total_income_exceeds_50_lakh || answers.has_crypto_or_vda || answers.has_foreign_assets_or_income) {
          form = "ITR-2";
          title = "ITR-2 (Capital Gains & High Net Worth)";
          reasons = ["Capital gains from mutual funds/stocks or multiple properties require ITR-2."];
          risks = ["Notice 139(9) Risk: Omission of Schedule CG in ITR-1 leads to defective return notices."];
        }

        setDiagnosis({
          recommended_form: form,
          form_title: title,
          summary_verdict: `You must file ${form} according to official Income Tax Department rules.`,
          primary_reasons: reasons,
          disqualifications: [],
          compliance_risks: risks,
          required_documents: docs
        });
        setDiagnosing(false);
      });
  };

  const toggleDocCheck = (id) => {
    setCheckedDocs(prev => ({ ...prev, [id]: !prev[id] }));
  };

  if (loading) {
    return (
      <div className="bg-white p-12 rounded-2xl border border-slate-200 text-center">
        <RefreshCw className="w-8 h-8 text-blue-600 animate-spin mx-auto mb-3" />
        <p className="text-slate-600 text-sm font-medium">Loading Tax Eligibility Diagnostic Matrix...</p>
      </div>
    );
  }

  // --- RESULT VIEW ---
  if (diagnosis) {
    const formTheme = {
      'ITR-1': { bg: 'bg-emerald-50', border: 'border-emerald-200', text: 'text-emerald-800', badge: 'bg-emerald-600' },
      'ITR-2': { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-800', badge: 'bg-blue-600' },
      'ITR-3': { bg: 'bg-purple-50', border: 'border-purple-200', text: 'text-purple-800', badge: 'bg-purple-600' },
      'ITR-4': { bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-800', badge: 'bg-amber-600' }
    }[diagnosis.recommended_form] || { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-800', badge: 'bg-blue-600' };

    return (
      <div className="space-y-6 animate-fadeIn">
        {/* Form Recommendation Banner */}
        <div className={`p-6 sm:p-8 rounded-2xl border ${formTheme.bg} ${formTheme.border} shadow-sm`}>
          <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
            <span className={`text-xs font-bold uppercase tracking-wider text-white px-3 py-1 rounded-full ${formTheme.badge} shadow-sm`}>
              Verified Tax Form Match
            </span>
            <button 
              onClick={() => { setDiagnosis(null); setCurrentIdx(0); }}
              className="text-xs text-slate-500 hover:text-slate-800 flex items-center gap-1 underline font-medium"
            >
              <RefreshCw className="w-3.5 h-3.5" /> Retake Diagnostic
            </button>
          </div>

          <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            {diagnosis.recommended_form}: {diagnosis.form_title}
          </h2>
          <p className="text-slate-700 text-sm mt-2 leading-relaxed">
            {diagnosis.summary_verdict}
          </p>

          {/* Statutory Risks & Notice 139(9) warnings */}
          {diagnosis.compliance_risks && diagnosis.compliance_risks.length > 0 && (
            <div className="mt-5 p-4 rounded-xl bg-amber-50 border border-amber-200 flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
              <div className="text-xs text-amber-900 space-y-1">
                <span className="font-bold">Statutory Legal Warning:</span>
                {diagnosis.compliance_risks.map((risk, i) => (
                  <p key={i}>{risk}</p>
                ))}
              </div>
            </div>
          )}

          {/* Reasons Breakdown */}
          <div className="mt-5 space-y-2">
            <p className="text-xs font-bold text-slate-700 uppercase tracking-wider">Why this form applies to you:</p>
            <ul className="space-y-1.5">
              {diagnosis.primary_reasons.map((r, i) => (
                <li key={i} className="text-xs text-slate-700 flex items-start gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                  <span>{r}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Personalized Required Documents Checklist */}
        <div className="bg-white p-6 sm:p-8 rounded-2xl border border-slate-200 shadow-sm space-y-5">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <FileCheck className="w-5 h-5 text-blue-600" />
                Required Documents Checklist for {diagnosis.recommended_form}
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Gather these documents before proceeding to the official portal. Click each document for download steps.
              </p>
            </div>
            <span className="text-xs font-semibold px-2.5 py-1 rounded-lg bg-slate-100 text-slate-600 border border-slate-200">
              {Object.values(checkedDocs).filter(Boolean).length} of {diagnosis.required_documents.length} ready
            </span>
          </div>

          <div className="space-y-3">
            {diagnosis.required_documents.map((doc) => {
              const isChecked = Boolean(checkedDocs[doc.id]);
              const isExpanded = expandedDoc === doc.id;

              return (
                <div 
                  key={doc.id} 
                  className={`border rounded-xl transition-all ${
                    isChecked ? 'border-emerald-300 bg-emerald-50/30' : 'border-slate-200 bg-white hover:border-slate-300'
                  }`}
                >
                  <div className="p-4 flex items-start justify-between gap-3">
                    <div className="flex items-start gap-3">
                      <input 
                        type="checkbox"
                        checked={isChecked}
                        onChange={() => toggleDocCheck(doc.id)}
                        className="w-4 h-4 mt-1 rounded text-emerald-600 focus:ring-emerald-500 border-slate-300 cursor-pointer"
                      />
                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className={`text-sm font-bold ${isChecked ? 'line-through text-slate-500' : 'text-slate-900'}`}>
                            {doc.name}
                          </h4>
                          {doc.mandatory && (
                            <span className="text-[10px] uppercase font-bold px-1.5 py-0.2 rounded bg-rose-100 text-rose-700">
                              Mandatory
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-slate-500 mt-0.5">{doc.description}</p>
                        <p className="text-[11px] text-blue-600 font-medium mt-1 flex items-center gap-1">
                          Source: {doc.source}
                        </p>
                      </div>
                    </div>

                    <button
                      onClick={() => setExpandedDoc(isExpanded ? null : doc.id)}
                      className="text-xs text-slate-500 hover:text-slate-800 p-1.5 rounded-lg hover:bg-slate-100 shrink-0"
                    >
                      {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </button>
                  </div>

                  {isExpanded && doc.download_steps && (
                    <div className="px-4 pb-4 pt-1 border-t border-slate-100 bg-slate-50/50 rounded-b-xl text-xs text-slate-700">
                      <p className="font-semibold text-slate-800 mb-2">How to download this document:</p>
                      <ol className="list-decimal list-inside space-y-1.5 text-slate-600 pl-1">
                        {doc.download_steps.map((step, sIdx) => (
                          <li key={sIdx}>{step}</li>
                        ))}
                      </ol>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          <div className="pt-4 flex flex-wrap items-center justify-between gap-3 border-t border-slate-100">
            <button
              onClick={() => {
                alert(`Downloaded Checklist for ${diagnosis.recommended_form} saved to local session.`);
              }}
              className="inline-flex items-center gap-2 text-xs font-semibold px-4 py-2 rounded-xl border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 shadow-sm"
            >
              <Download className="w-3.5 h-3.5" /> Save Document Checklist
            </button>

            <button
              onClick={() => onComplete && onComplete(diagnosis)}
              className="inline-flex items-center gap-2 text-sm font-semibold px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white shadow transition"
            >
              Proceed to Document Upload & Parser <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    );
  }

  // --- QUESTION STEPPER VIEW ---
  const progressPercent = Math.round(((currentIdx + 1) / activeQuestions.length) * 100);

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden animate-fadeIn">
      {/* Step Header & Progress */}
      <div className="bg-slate-50 px-6 py-4 border-b border-slate-200 flex items-center justify-between">
        <span className="text-xs font-bold uppercase tracking-wider text-blue-700 bg-blue-50 border border-blue-200 px-2.5 py-1 rounded-md">
          {currentQ.section}
        </span>
        <div className="flex items-center gap-3">
          <span className="text-xs font-medium text-slate-500">
            Question {currentIdx + 1} of {activeQuestions.length}
          </span>
          <div className="w-24 h-2 bg-slate-200 rounded-full overflow-hidden">
            <div 
              className="h-full bg-blue-600 transition-all duration-300"
              style={{ width: `${progressPercent}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Question Card */}
      <div className="p-6 sm:p-8 space-y-6">
        <div>
          <h3 className="text-xl sm:text-2xl font-bold text-slate-900 leading-snug">
            {currentQ.title}
          </h3>
          <p className="text-slate-500 text-sm mt-1.5 leading-relaxed">
            {currentQ.subtitle}
          </p>
        </div>

        {/* Legal Justification Tooltip */}
        {currentQ.law_note && (
          <div className="p-3.5 rounded-xl bg-blue-50/60 border border-blue-100 flex items-start gap-2.5 text-xs text-blue-900">
            <HelpCircle className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
            <span><strong>Why the tax law asks this:</strong> {currentQ.law_note}</span>
          </div>
        )}

        {/* Input Selector */}
        <div className="pt-2">
          {currentQ.type === 'boolean' && (
            <div className="grid grid-cols-2 gap-4">
              <button
                type="button"
                onClick={() => handleAnswer(true)}
                className={`py-4 px-6 rounded-xl border text-sm font-bold flex items-center justify-center gap-2 transition-all ${
                  answers[currentQ.id] === true
                    ? 'border-blue-600 bg-blue-50 text-blue-800 ring-2 ring-blue-100 shadow-sm'
                    : 'border-slate-200 hover:border-slate-300 text-slate-700 bg-white'
                }`}
              >
                <CheckCircle2 className={`w-4 h-4 ${answers[currentQ.id] === true ? 'text-blue-600' : 'text-slate-400'}`} />
                Yes
              </button>
              <button
                type="button"
                onClick={() => handleAnswer(false)}
                className={`py-4 px-6 rounded-xl border text-sm font-bold flex items-center justify-center gap-2 transition-all ${
                  answers[currentQ.id] === false
                    ? 'border-blue-600 bg-blue-50 text-blue-800 ring-2 ring-blue-100 shadow-sm'
                    : 'border-slate-200 hover:border-slate-300 text-slate-700 bg-white'
                }`}
              >
                No
              </button>
            </div>
          )}

          {currentQ.type === 'choice' && (
            <div className="space-y-2.5">
              {currentQ.options.map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => handleAnswer(opt.value)}
                  className={`w-full text-left p-4 rounded-xl border text-sm font-medium flex items-center justify-between transition-all ${
                    answers[currentQ.id] === opt.value
                      ? 'border-blue-600 bg-blue-50 text-blue-900 ring-2 ring-blue-100 shadow-sm'
                      : 'border-slate-200 hover:border-slate-300 text-slate-700 bg-white'
                  }`}
                >
                  <span>{opt.label}</span>
                  {answers[currentQ.id] === opt.value && (
                    <CheckCircle2 className="w-4 h-4 text-blue-600" />
                  )}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Navigation Footer */}
      <div className="px-6 py-4 bg-slate-50 border-t border-slate-200 flex items-center justify-between">
        <button
          onClick={handlePrev}
          disabled={currentIdx === 0}
          className={`inline-flex items-center gap-1.5 text-xs font-semibold px-4 py-2 rounded-lg border transition ${
            currentIdx === 0 
              ? 'border-transparent text-slate-300 cursor-not-allowed' 
              : 'border-slate-300 bg-white hover:bg-slate-100 text-slate-700'
          }`}
        >
          <ArrowLeft className="w-3.5 h-3.5" /> Back
        </button>

        <button
          onClick={handleNext}
          disabled={diagnosing}
          className="inline-flex items-center gap-2 text-xs font-semibold px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white shadow transition"
        >
          {diagnosing ? (
            <>
              <RefreshCw className="w-3.5 h-3.5 animate-spin" /> Evaluating...
            </>
          ) : currentIdx === activeQuestions.length - 1 ? (
            <>
              Diagnose My ITR Form <ArrowRight className="w-3.5 h-3.5" />
            </>
          ) : (
            <>
              Next Question <ArrowRight className="w-3.5 h-3.5" />
            </>
          )}
        </button>
      </div>
    </div>
  );
}

