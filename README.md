# Smart Tax Planner and Filing Assistant (TaxSahayak 🇮🇳)

[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/Frontend-React%2019-61dafb.svg)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Styling-Tailwind%20CSS-38bdf8.svg)](https://tailwindcss.com/)
[![PWA Ready](https://img.shields.io/badge/PWA-Workbox%20Service%20Worker-purple.svg)](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
[![Tests Passing](https://img.shields.io/badge/Tests-19%2F19%20Passing-brightgreen.svg)](https://pytest.org/)
[![DPDP Act 2023](https://img.shields.io/badge/Compliance-DPDP%20Act%202023-emerald.svg)](#privacy--dpdp-act-2023-compliance)

> A privacy-first Progressive Web App (PWA) designed to hold a taxpayer's hand through the official Government of India e-Filing portal ([eportal.incometax.gov.in](https://eportal.incometax.gov.in)). Diagnoses the required ITR form (ITR-1, 2, 3, or 4) to avoid Section 139(9) defective return notices, extracts and reconciles Form 16 & AIS data, computes the optimal tax regime (New vs Old), and provides a step-by-step portal filing guide with 1-click copyable figures.

---

## 🏛️ Architecture Overview

```
                                TaxSahayak PWA Workflow
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  1. Form Finder  │ ──> │ 2. Doc Ingestion │ ──> │  3. Tax Engine   │ ──> │ 4. Portal Guide  │
│  Decision Engine │     │  & Reconciliation│     │  Regime Optimizer│     │  Schedule Mapper │
└──────────────────┘     └──────────────────┘     └──────────────────┘     └──────────────────┘
  • ITR-1 (Sahaj)          • Form 16 PDF Parser     • New Regime (115BAC)    • 6-Step Walkthrough
  • ITR-2 (Cap Gains)      • AIS JSON & PDF Parser  • Old Regime Deductions  • 1-Click Copy Values
  • ITR-3 (Business/F&O)   • Notice Trap Auditor    • Breakeven Target Calc  • Sec 115BAC Opt-Out
  • ITR-4 (Sugam)          • In-Memory Processing   • Live Slabs Breakdown   • Aadhaar e-Verify
```

---

## 🌟 Key Capabilities

### 1. ITR Eligibility Decision Engine (Phase 2)
- Evaluates residency, income sources, capital gains, foreign assets, directorships, and F&O turnover against CBDT rules.
- Diagnoses the exact form required: **ITR-1 (Sahaj)**, **ITR-2**, **ITR-3**, or **ITR-4 (Sugam)**.
- Warns against **Section 139(9) Defective Return traps** (e.g. reporting mutual fund sales or F&O turnover in ITR-1).
- Generates a customized **Required Documents Checklist** with download instructions for Zerodha Console, Groww, AIS portal, TRACES, and NetBanking.

### 2. In-Memory Document Ingestion & Parser Pipeline (Phase 3)
- **Form 16 Parser**: In-memory PDF text extraction via `pdfplumber` and `pypdf`. Extracts Employer TAN/PAN, Gross Salary u/s 17(1), HRA u/s 10(13A), Standard Deduction u/s 16(ia), Professional Tax, 80C, 80CCD(1B), 80D, and TDS deposited.
- **AIS & TIS Parser**: In-memory parsing of official ITD AIS JSON and PDF statements for Savings Interest (SFT-005), Term Deposit Interest (SFT-006), Dividends (SFT-015), and Securities Sales (SFT-012).
- **Notice Trap Auditor**: Cross-verifies Form 16 against AIS to prevent **Section 143(1)(a)** automated demand notices for undeclared bank interest.
- **1-Click Sample Data Loaders**: Test the complete flow instantly without needing personal tax documents.

### 3. Dynamic Versioned Tax Rules Engine
- Tax rules, slab brackets, and rebate caps are stored in declarative JSON configuration files ([`tax_rules_ay_2025_26.json`](backend/app/rules/tax_rules_ay_2025_26.json)).
- Incorporates the **Finance (No. 2) Act, 2024** provisions (revised standard deduction of ₹75,000 in New Regime, revised 5%–30% slab brackets).
- **Future-Proof**: When the next Union Budget is announced, adding a new rule file dynamically updates calculations without code modifications.

### 4. Tax Optimization Engine (Old vs New Regime) (Phase 4)
- Side-by-side comparative computation: **New Tax Regime (Section 115BAC - Default)** vs **Old Tax Regime**.
- Incorporates **Section 87A rebate** (zero tax liability up to ₹7,00,000 taxable income in New Regime).
- Computes **Breakeven Deduction Target** (how much deduction is needed in Old Regime to match New Regime).
- Interactive **Deduction Simulator** tab: live sliders to test investments in NPS, 80C, or 80D.
- Compares tax liability against TDS credits to show **Estimated Refund Due** or **Self-Assessment Tax Due**.

### 5. Official Portal Schedule Mapper & Filing Guide (Phase 5 & 6)
- Maps every calculated figure directly to official portal schedules: **Schedule Salary (Box 1(a), 2, 4(a))**, **Schedule OS (Box 1(a)(i), 1(a)(ii))**, **Schedule VI-A**, **Schedule TDS**, and **Part B - TTI**.
- **1-Click Copy to Clipboard** buttons next to each calculated figure for effortless pasting.
- Answers the critical Section 115BAC Opt-Out question explicitly (**NO** for New Regime, **YES** for Old Regime).
- Generates an itemized, print-ready **Statement of Tax Computation** HTML/PDF.
- Step-by-step **Aadhaar OTP e-Verification** guide.

---

## 🔒 Privacy & DPDP Act 2023 Compliance

- **Zero-Storage Guarantee**: All document parsing and tax calculations occur ephemerally in RAM or within the local browser session. No financial numbers, PAN, or documents are stored in any database.
- **Zero-Credential Policy**: The app never asks for or persists Income Tax portal credentials. Users log in directly on the official government website.
- **PII Masking**: PAN, Aadhaar, and bank account numbers are masked by default.

---

## 📂 Project Structure

```
Smart-Tax-Planner-and-Filling-Assistant/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI REST endpoints
│   │   │   ├── questionnaire.py  # Form Finder endpoints
│   │   │   ├── documents.py      # Form 16 & AIS in-memory parsers
│   │   │   ├── tax_calculator.py # Tax optimization endpoints
│   │   │   ├── portal.py         # Schedule mapper & computation sheet
│   │   │   └── rules.py          # Dynamic rule engine endpoints
│   │   ├── core/            # DPDP compliance & PII masking
│   │   ├── models/          # Pydantic data schemas
│   │   ├── rules/           # Versioned AY tax rule JSON files
│   │   ├── services/        # Form finder, doc parser, tax engine, portal mapper
│   │   ├── config.py        # Application configuration
│   │   └── main.py          # FastAPI application entry point
│   └── tests/               # Pytest automated test suites (19 tests)
├── frontend/
│   ├── public/              # Web manifest & PWA assets
│   ├── src/
│   │   ├── components/      # UI components (FormFinder, DocUpload, TaxOptimizer, PortalGuide)
│   │   ├── App.jsx          # Main application with 4-step stepper
│   │   ├── main.jsx         # Entry point with Service Worker registration
│   │   └── index.css        # Tailwind CSS v4 styling
│   ├── package.json
│   └── vite.config.js       # Vite configuration with PWA plugin
├── .vscode/                 # IDE configuration for Python 3.13 venv
├── .gitignore
├── .python-version          # Python 3.13
├── PROJECT_PLANNER.md       # Dynamic project tracker with phase markers
├── requirements.txt         # Python backend dependencies
├── start-dev.ps1            # One-click dev launch script
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.13 (`.venv`)
- Node.js v18+ & npm

### 1. One-Click Launch (PowerShell)
```powershell
.\start-dev.ps1
```

### 2. Manual Startup
**Backend**:
```powershell
.\.venv\Scripts\Activate.ps1
uvicorn backend.app.main:app --reload --port 8000
```
- API Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- Interactive API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

**Frontend**:
```powershell
cd frontend
npm run dev
```
- Web Application: [http://localhost:5173](http://localhost:5173)

### 3. Run Automated Tests
```powershell
.\.venv\Scripts\pytest -v
```
All 19 unit tests verify Form Finder decision paths, TRACES Form 16 extraction, AIS parsing, tax computation slabs, and portal schedule mapping.

---

## 📜 Compliance & Legal Disclaimer
*TaxSahayak is an educational and tax preparation planning assistant. It operates in full compliance with India's Digital Personal Data Protection (DPDP) Act 2023. It does not provide certified chartered accountancy or legal advice. Taxpayers must verify all values before final submission on the official Income Tax portal.*
