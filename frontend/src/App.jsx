import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  FileText, 
  Calculator, 
  UploadCloud, 
  HelpCircle, 
  CheckCircle2, 
  ArrowRight, 
  Sparkles,
  Lock,
  Download,
  AlertTriangle,
  RefreshCw
} from 'lucide-react';
import FormFinderWizard from './components/FormFinderWizard';
import DocumentUploadPipeline from './components/DocumentUploadPipeline';
import TaxOptimizerEngine from './components/TaxOptimizerEngine';
import OfficialPortalGuide from './components/OfficialPortalGuide';

export default function App() {
  const [assessmentYear, setAssessmentYear] = useState('2025-26');
  const [activeStep, setActiveStep] = useState(1);
  const [apiStatus, setApiStatus] = useState({ online: false, checking: true });
  const [diagnosedResult, setDiagnosedResult] = useState(null);
  const [financialData, setFinancialData] = useState(null);
  const [optimizedTax, setOptimizedTax] = useState(null);

  useEffect(() => {
    // Check backend health
    fetch('/health')
      .then(res => res.json())
      .then(data => {
        if (data.status === 'healthy') {
          setApiStatus({ online: true, checking: false });
        }
      })
      .catch(() => {
        // Fallback for standalone frontend dev
        fetch('http://127.0.0.1:8000/health')
          .then(res => res.json())
          .then(data => {
            if (data.status === 'healthy') setApiStatus({ online: true, checking: false });
          })
          .catch(() => setApiStatus({ online: false, checking: false }));
      });
  }, []);

  const steps = [
    { id: 1, title: 'Form Finder', desc: diagnosedResult ? diagnosedResult.recommended_form : 'Identify ITR Form', icon: HelpCircle },
    { id: 2, title: 'Documents', desc: financialData ? 'Extracted & Audited' : 'Form 16 & AIS', icon: UploadCloud },
    { id: 3, title: 'Tax Engine', desc: optimizedTax ? `${optimizedTax.recommended_regime} Regime` : 'Old vs New', icon: Calculator },
    { id: 4, title: 'Portal Guide', desc: 'Step-by-Step Filing', icon: Download },
  ];

  const handleFormDiagnosed = (result) => {
    setDiagnosedResult(result);
    setActiveStep(2);
  };

  const handleDocumentsParsed = (data) => {
    setFinancialData(data);
    setActiveStep(3);
  };

  const handleTaxOptimized = (taxResult) => {
    setOptimizedTax(taxResult);
    setActiveStep(4);
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
      {/* Top DPDP Act Compliance & Security Banner */}
      <div className="bg-emerald-800 text-white text-xs py-2 px-4 flex flex-wrap items-center justify-between gap-2 shadow-inner">
        <div className="flex items-center gap-2 font-medium">
          <ShieldCheck className="w-4 h-4 text-emerald-300" />
          <span>DPDP Act 2023 Compliant: Zero-Storage Guarantee — Your financial data & documents never leave your session.</span>
        </div>
        <div className="flex items-center gap-3 text-emerald-100">
          <span className="flex items-center gap-1">
            <Lock className="w-3.5 h-3.5" /> No Portal Passwords Requested
          </span>
          <span className="hidden sm:inline">•</span>
          <span className="flex items-center gap-1.5">
            <span className={`w-2 h-2 rounded-full ${apiStatus.online ? 'bg-emerald-400' : 'bg-amber-400 animate-pulse'}`}></span>
            Backend: {apiStatus.online ? 'Ready (Python 3.13)' : 'Starting...'}
          </span>
        </div>
      </div>

      {/* Main Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 h-18 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-700 to-indigo-600 flex items-center justify-center text-white shadow-md">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h1 className="font-bold text-lg text-slate-900 flex items-center gap-2">
                TaxSahayak <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-100 text-blue-800 border border-blue-200">Smart Guide</span>
              </h1>
              <p className="text-xs text-slate-500">Official Portal Filing & Tax Planner Assistant</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-right hidden sm:block">
              <label htmlFor="ay-select" className="text-[11px] font-semibold text-slate-500 block uppercase tracking-wider">Assessment Year</label>
              <select 
                id="ay-select"
                value={assessmentYear} 
                onChange={(e) => setAssessmentYear(e.target.value)}
                className="text-xs font-semibold bg-slate-100 border border-slate-300 rounded-lg px-2 py-1 text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="2025-26">AY 2025-26 (FY 2024-25)</option>
                <option value="2024-25">AY 2024-25 (FY 2023-24)</option>
              </select>
            </div>
          </div>
        </div>
      </header>

      {/* Stepper Navigation */}
      <div className="bg-white border-b border-slate-200 py-3">
        <div className="max-w-4xl mx-auto px-4">
          <div className="grid grid-cols-4 gap-2">
            {steps.map((step) => {
              const Icon = step.icon;
              const isDone = step.id < activeStep;
              const isCurrent = step.id === activeStep;
              return (
                <button
                  key={step.id}
                  onClick={() => setActiveStep(step.id)}
                  className={`text-left p-2.5 rounded-xl transition-all border flex items-center gap-3 ${
                    isCurrent 
                      ? 'bg-blue-50/80 border-blue-400 ring-2 ring-blue-100' 
                      : isDone 
                      ? 'bg-slate-50 border-emerald-300 text-slate-700' 
                      : 'border-transparent text-slate-400 hover:bg-slate-50'
                  }`}
                >
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                    isCurrent 
                      ? 'bg-blue-600 text-white shadow-sm' 
                      : isDone 
                      ? 'bg-emerald-600 text-white' 
                      : 'bg-slate-200 text-slate-500'
                  }`}>
                    {isDone ? <CheckCircle2 className="w-4 h-4" /> : <Icon className="w-4 h-4" />}
                  </div>
                  <div className="hidden md:block overflow-hidden">
                    <p className={`text-xs font-bold truncate ${isCurrent ? 'text-blue-900' : 'text-slate-800'}`}>
                      {step.title}
                    </p>
                    <p className="text-[10px] text-slate-500 truncate">{step.desc}</p>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Main Content Body */}
      <main className="max-w-4xl mx-auto px-4 py-8 flex-1 w-full">
        {/* Step 1: Form Finder Wizard */}
        {activeStep === 1 && (
          <FormFinderWizard 
            assessmentYear={assessmentYear}
            onComplete={handleFormDiagnosed}
          />
        )}

        {/* Step 2: Document Ingestion Pipeline */}
        {activeStep === 2 && (
          <div className="space-y-6">
            {diagnosedResult && (
              <div className="p-4 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-between gap-3">
                <div className="flex items-center gap-2.5">
                  <span className="text-xs font-bold px-2 py-0.5 rounded bg-blue-600 text-white">
                    {diagnosedResult.recommended_form}
                  </span>
                  <p className="text-xs text-blue-900 font-medium">
                    Diagnosed Form: <strong>{diagnosedResult.form_title}</strong>
                  </p>
                </div>
                <button 
                  onClick={() => setActiveStep(1)}
                  className="text-xs text-blue-700 hover:underline font-semibold"
                >
                  Change Answers
                </button>
              </div>
            )}

            <DocumentUploadPipeline 
              diagnosedForm={diagnosedResult}
              onProceed={handleDocumentsParsed}
            />
          </div>
        )}

        {/* Step 3: Tax Optimization Engine */}
        {activeStep === 3 && (
          <TaxOptimizerEngine 
            financialData={financialData}
            assessmentYear={assessmentYear}
            onProceed={handleTaxOptimized}
          />
        )}

        {/* Step 4: Official Portal Guide & Computation Sheet */}
        {activeStep === 4 && (
          <OfficialPortalGuide 
            taxComparison={optimizedTax}
            formDiagnosis={diagnosedResult}
            financialData={financialData}
            assessmentYear={assessmentYear}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-6 text-center text-xs text-slate-500">
        <p>© 2026 TaxSahayak • Privacy-First Progressive Web App for Indian Taxpayers</p>
        <p className="mt-1 text-[11px] text-slate-400">
          Operates in Ephemeral Zero-Storage mode under the Digital Personal Data Protection (DPDP) Act 2023. Not official legal advice.
        </p>
      </footer>
    </div>
  );
}
