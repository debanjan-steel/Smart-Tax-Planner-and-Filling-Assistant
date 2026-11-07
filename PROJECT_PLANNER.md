# TaxSahayak: Smart Tax Planner & Official Portal Filing Assistant

> 🌐 **Live Web Application (PWA)**: **[https://smart-tax-planner-and-filling-assistant.onrender.com/](https://smart-tax-planner-and-filling-assistant.onrender.com/)**  
> 📦 **GitHub Repository**: **[https://github.com/debanjan-steel/Smart-Tax-Planner-and-Filling-Assistant](https://github.com/debanjan-steel/Smart-Tax-Planner-and-Filling-Assistant)**

> **Project Overview**: A privacy-first Progressive Web App (PWA) designed to hold a taxpayer's hand through the official Income Tax Portal (`eportal.incometax.gov.in`). The assistant accurately diagnoses the required ITR form (ITR-1, 2, 3, or 4) to prevent Section 139(9) defective return notices, extracts and explains figures from tax documents (Form 16, AIS/TIS, 26AS), computes the optimal tax liability under Old vs New Tax Regimes (Section 115BAC), and provides a step-by-step portal filling guide with a ready-to-use Tax Computation Sheet.

---

## 📌 Status Legend
- `[DONE]` : Completed and verified
- `[IN PROGRESS]` : Currently active task being executed
- `[TODO]` : Planned for upcoming execution
- `[UNDER DISCUSSION]` : Requires user feedback, architecture alignment, or regulatory review

---

## 🧭 Project Status Dashboard

| Phase | Milestone / Focus | Status | Target Delivery |
| :--- | :--- | :--- | :--- |
| **Phase 0** | Workspace & Environment Initialization | `[DONE]` | Completed |
| **Phase 1** | Architecture, Security Model & Tech Stack Setup | `[DONE]` | Completed |
| **Phase 2** | ITR Eligibility Decision Engine (Form Finder) | `[DONE]` | Completed |
| **Phase 3** | Document Ingestion & Parser Pipeline (Form 16, AIS) | `[DONE]` | Completed |
| **Phase 4** | Tax Optimization Engine (Old vs New Regime) | `[DONE]` | Completed |
| **Phase 5** | Tax Computation Sheet & Portal Schedule Mapper | `[DONE]` | Completed |
| **Phase 6** | Interactive Official Portal Step-by-Step Filing Guide | `[DONE]` | Completed |
| **Phase 7** | PWA Capabilities (Offline, Installable, Service Worker) | `[DONE]` | Completed |
| **Phase 8** | Security Hardening & DPDP Act Compliance Audit | `[DONE]` | Completed |
| **Phase 9** | Cloud Deployment & Multi-Platform PWA Readiness | `[DONE]` | Completed |

---

## 🏗️ Detailed Phase Roadmap & Task Breakdown

### Phase 0: Workspace & Environment Setup `[DONE]`
- [x] `[DONE]` Target Python 3.13 and verify interpreter.
- [x] `[DONE]` Create local virtual environment (`.venv`).
- [x] `[DONE]` Configure `.vscode/settings.json` for automatic environment activation across terminals.
- [x] `[DONE]` Create `.python-version` (3.13) and `.gitignore`.

---

### Phase 1: Architecture, Security Model & Tech Stack Selection `[DONE]`
- [x] `[DONE]` Product Strategy Pivot: Repositioned as **Smart Tax Planner & Official Portal Filing Assistant** (zero statutory legal risk, zero credential handling).
- [x] `[DONE]` Established Tech Stack:
  - Backend: **FastAPI (Python 3.13)** with `pypdf`, `pdfplumber`, `pandas`, `pydantic`.
  - Frontend: **React / Vite + Tailwind CSS** with `vite-plugin-pwa` (Workbox Service Worker + Manifest).
- [x] `[DONE]` Implemented Ephemeral Zero-Storage security layer in [dpdp_compliance.py](file:///c:/Users/deban/OneDrive/Desktop/Self%20Projects/ITR%20App/backend/app/core/dpdp_compliance.py).
- [x] `[DONE]` Initialized backend API with passing pytest test suite (`backend/tests/test_health.py`).
- [x] `[DONE]` Initialized PWA frontend with responsive stepper and PWA build verified.

---

### Phase 2: ITR Eligibility Decision Engine (Form Finder) `[DONE]`
- [x] `[DONE]` Built CBDT rule-compliant decision engine in [form_finder.py](file:///c:/Users/deban/OneDrive/Desktop/Self%20Projects/ITR%20App/backend/app/services/form_finder.py) for ITR-1, ITR-2, ITR-3, and ITR-4.
- [x] `[DONE]` Implemented Section 139(9) Defective Return risk warning alerts (e.g. F&O or share trading in ITR-1).
- [x] `[DONE]` Integrated interactive **Required Documents Checklist** with portal download guides (Zerodha Console, AIS Portal, TRACES, NetBanking).
- [x] `[DONE]` Developed frontend wizard component in [FormFinderWizard.jsx](file:///c:/Users/deban/OneDrive/Desktop/Self%20Projects/ITR%20App/frontend/src/components/FormFinderWizard.jsx) with progress bar and legal citations.
- [x] `[DONE]` Created automated test suite in [test_questionnaire.py](file:///c:/Users/deban/OneDrive/Desktop/Self%20Projects/ITR%20App/backend/tests/test_questionnaire.py).

---

### Phase 3: Financial Document Ingestion & Parser Pipeline `[DONE]`
- [x] `[DONE]` **Dynamic Versioned Tax Rules Engine** in [rule_engine.py](file:///c:/Users/deban/OneDrive/Desktop/Self%20Projects/ITR%20App/backend/app/services/rule_engine.py):
  - Created JSON rule files for AY 2025-26 and AY 2024-25. Allows instant adaptation to future annual Union Budgets without code modifications.
  - Implemented hot-reloading endpoint (`/api/v1/rules/reload`).
- [x] `[DONE]` **Form 16 Parser (Part A & B)** in [doc_parser.py](file:///c:/Users/deban/OneDrive/Desktop/Self%20Projects/ITR%20App/backend/app/services/doc_parser.py):
  - In-memory PDF text extraction via `pdfplumber` & `pypdf`.
  - Extracts Employer TAN/PAN, Gross Salary u/s 17(1), HRA u/s 10(13A), Standard Deduction u/s 16(ia), Professional Tax, 80C, 80CCD(1B), 80D, and TDS deposited.
- [x] `[DONE]` **Annual Information Statement (AIS) Parser**:
  - In-memory parsing of official ITD AIS JSON and PDF statements.
  - Extracts Savings Interest (SFT-005), Term Deposit Interest (SFT-006), Dividends (SFT-015), and Securities Sales (SFT-012).
- [x] `[DONE]` **Cross-Verification & Notice Trap Auditor**:
  - Reconciles Form 16 against AIS to prevent Section 143(1) automated demand notices for undeclared bank interest.
- [x] `[DONE]` **Frontend Upload Pipeline** in [DocumentUploadPipeline.jsx](file:///c:/Users/deban/OneDrive/Desktop/Self%20Projects/ITR%20App/frontend/src/components/DocumentUploadPipeline.jsx).

---

### Phase 4: Tax Optimization Engine (Old vs New Regime) `[DONE]`
- [x] `[DONE]` Built Indian Income Tax calculation algorithms in [tax_engine.py](file:///c:/Users/deban/OneDrive/Desktop/Self%20Projects/ITR%20App/backend/app/services/tax_engine.py):
  - **New Tax Regime (Section 115BAC)**: Standard deduction (₹75,000 for AY 2025-26), progressive slabs (5% to 30%), Section 87A full rebate up to ₹7 Lakh, and 4% Health & Education cess.
  - **Old Tax Regime**: Standard deduction (₹50,000), Section 10 exemptions (HRA, LTA), Chapter VI-A deductions (80C, 80CCD(1B), 80D, 24(b)), Section 87A rebate up to ₹5 Lakh, and 4% cess.
- [x] `[DONE]` **Comparative Regime Optimizer**:
  - Identifies winning regime with exact Rupee tax savings calculation.
  - Computes the exact **Breakeven Deduction Target** (how much deduction is needed in Old Regime to match New Regime).
  - Calculates estimated **Tax Refund Due** vs **Self-Assessment Tax Payable** against TDS credits.
- [x] `[DONE]` **Interactive Deduction Simulator UI** in [TaxOptimizerEngine.jsx](file:///c:/Users/deban/OneDrive/Desktop/Self%20Projects/ITR%20App/frontend/src/components/TaxOptimizerEngine.jsx):
  - Side-by-side comparative cards with progressive slab breakdown accordion.
  - Real-time sliders/inputs to simulate investments in 80C, 80D, and NPS.
- [x] `[DONE]` Automated test suite in [test_tax_engine.py](file:///c:/Users/deban/OneDrive/Desktop/Self%20Projects/ITR%20App/backend/tests/test_tax_engine.py).

---

### Phase 5 & 6: Tax Computation Sheet, Portal Schedule Mapper & Step-by-Step Filing Guide `[DONE]`
- [x] `[DONE]` **Official Portal Schedule Mapping Engine** in [portal_mapper.py](file:///c:/Users/deban/OneDrive/Desktop/Self%20Projects/ITR%20App/backend/app/services/portal_mapper.py):
  - Maps calculated figures to exact portal box numbers: Schedule Salary (Line 1(a), 2, 4(a)), Schedule OS (Line 1(a)(i), 1(a)(ii)), Schedule VI-A (80C, 80D, 80CCD), Schedule TDS, and Part B - TTI.
- [x] `[DONE]` **Printable / Exportable Tax Computation Sheet**:
  - Generated professional HTML Statement of Tax Computation endpoint (`/api/v1/portal/computation-sheet-html`) ready to print or save as PDF.
- [x] `[DONE]` **Interactive Official Portal Filing Guide UI** in [OfficialPortalGuide.jsx](file:///c:/Users/deban/OneDrive/Desktop/Self%20Projects/ITR%20App/frontend/src/components/OfficialPortalGuide.jsx):
  - 6 interactive stages with checkable progress.
  - **1-Click Copy to Clipboard** buttons for every single schedule amount.
  - Explicit answer for Section 115BAC Opt-Out question (NO for New Regime, YES for Old Regime).
  - Direct launcher button to `https://eportal.incometax.gov.in`.
  - Aadhaar OTP e-verification guide.
- [x] `[DONE]` Automated test suite in [test_portal_mapper.py](file:///c:/Users/deban/OneDrive/Desktop/Self%20Projects/ITR%20App/backend/tests/test_portal_mapper.py).

---

### Phase 7: PWA Capabilities (Offline, Installable, Service Worker) `[DONE]`
- [x] `[DONE]` Web App Manifest (`manifest.webmanifest`) configured with `vite-plugin-pwa`.
- [x] `[DONE]` Workbox Service Worker generation configured (`dist/sw.js`).
- [x] `[DONE]` Immediate Service Worker registration in [main.jsx](file:///c:/Users/deban/OneDrive/Desktop/Self%20Projects/ITR%20App/frontend/src/main.jsx).

---

### Phase 8: Security Hardening & DPDP Act Compliance Audit `[DONE]`
- [x] `[DONE]` Zero-Storage Guarantee & DPDP Act compliance principles embedded.
- [x] `[DONE]` In-memory stream parsing (no files written to disk).
- [x] `[DONE]` PII masking for PAN, Aadhaar, and bank accounts.
- [x] `[DONE]` Zero-Credential policy: Portal passwords are never handled.

---

### Phase 9: Cloud Deployment & Multi-Platform PWA Readiness `[DONE]`
- [x] `[DONE]` Progressive Web App (PWA) selected as the optimal deployment format for unified Laptop + Android experience.
- [x] `[DONE]` Generated crisp, modern PWA app icons (`192x192` and `512x512` maskable PNGs) conforming to Google Chrome & Android Web App Manifest criteria.
- [x] `[DONE]` Configured full-stack unified production serving in [main.py](file:///c:/Users/deban/OneDrive/Desktop/Self%20Projects/ITR%20App/backend/app/main.py) to serve compiled `frontend/dist` with client-side SPA fallback and live `/api/v1` backend endpoints.
- [x] `[DONE]` Added multi-stage [Dockerfile](file:///c:/Users/deban/OneDrive/Desktop/Self%20Projects/ITR%20App/Dockerfile) (Node 20 Alpine builder + Python 3.13-slim runner) supporting cloud platforms (Render, Railway, Fly.io, Cloud Run).
- [x] `[DONE]` Created [render.yaml](file:///c:/Users/deban/OneDrive/Desktop/Self%20Projects/ITR%20App/render.yaml) for one-click deployment via Render Infrastructure-as-Code.
- [x] `[DONE]` Configured flexible `API_BASE` in [config.js](file:///c:/Users/deban/OneDrive/Desktop/Self%20Projects/ITR%20App/frontend/src/config.js) supporting both unified and decoupled deployments (e.g. Vercel + Render).
- [x] `[DONE]` 19/19 backend pytest tests verified passing; production frontend build verified.

---

## 💡 Notes & Discussion Log
- *2026-11-07*: All phases through Phase 9 completed! The complete TaxSahayak application is packaged and ready for deployment to free cloud tiers (Render / Railway / Vercel), providing an installable native-like app on both Android and Laptop.
