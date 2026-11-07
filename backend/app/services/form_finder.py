from typing import List
from backend.app.models.questionnaire import TaxpayerProfile, FormDiagnosisResponse, DocumentRequirement

def diagnose_itr_form(profile: TaxpayerProfile) -> FormDiagnosisResponse:
    """
    Evaluates taxpayer profile against Income Tax Department (CBDT) rules
    to determine the correct ITR form: ITR-1 (Sahaj), ITR-2, ITR-3, or ITR-4 (Sugam).
    """
    primary_reasons: List[str] = []
    disqualifications: List[str] = []
    compliance_risks: List[str] = []
    required_docs: List[DocumentRequirement] = []

    # Universal Essential Documents (Every Taxpayer)
    required_docs.append(DocumentRequirement(
        id="ais_tis",
        name="Annual Information Statement (AIS) & Taxpayer Information Summary (TIS)",
        description="Comprehensive summary of all financial transactions reported to the IT Dept (Savings interest, FDs, dividends, securities).",
        source="Official Income Tax e-Filing Portal",
        download_steps=[
            "Log in to https://eportal.incometax.gov.in with PAN & password.",
            "In top navigation bar, go to 'Services' -> 'Annual Information Statement (AIS)'.",
            "Click on 'AIS' tab and download both AIS (PDF/JSON) and TIS (PDF).",
            "Password to open PDF is your PAN (lowercase) + Date of Birth (DDMMYYYY)."
        ],
        mandatory=True,
        applicable_reasons=["Mandatory for all taxpayers to cross-check pre-filled IT portal data"]
    ))

    required_docs.append(DocumentRequirement(
        id="form_26as",
        name="Form 26AS (Tax Credit Statement)",
        description="Consolidated statement of TDS deducted, TCS collected, and advance tax / self-assessment tax paid.",
        source="TRACES / Income Tax Portal",
        download_steps=[
            "Log in to https://eportal.incometax.gov.in.",
            "Go to 'e-File' -> 'Income Tax Returns' -> 'View Form 26AS'.",
            "Confirm redirect to TRACES portal.",
            "Select Assessment Year and format 'HTML' -> click 'Export as PDF'."
        ],
        mandatory=True,
        applicable_reasons=["Required to verify that all TDS deducted has been credited by employers/banks"]
    ))

    if profile.has_salary_or_pension:
        required_docs.append(DocumentRequirement(
            id="form_16",
            name="Form 16 (Part A and Part B)",
            description="Certificate issued by employer showing total salary paid, standard deduction, exemptions u/s 10, Chapter VI-A deductions, and TDS deducted.",
            source="Employer HR Portal / Payroll Department",
            download_steps=[
                "Log in to your company HR / payroll portal (e.g. Darwinbox, Keka, ZingHR).",
                "Navigate to Tax / Form 16 section for the relevant Financial Year.",
                "Download both Part A (TRACES certified TDS) and Part B (salary breakup)."
            ],
            mandatory=True,
            applicable_reasons=["Essential for accurate reporting under Schedule Salary / Pension"]
        ))

    # Bank Statements for Interest
    required_docs.append(DocumentRequirement(
        id="bank_interest_cert",
        name="Bank Interest Certificates & Bank Statements",
        description="Interest certificates for all Savings Bank Accounts and Fixed Deposits for the Financial Year (April 1 to March 31).",
        source="NetBanking of your respective banks",
        download_steps=[
            "Log in to your Bank NetBanking (HDFC, ICICI, SBI, Axis, etc.).",
            "Search for 'Interest Certificate' or 'Tax Certificate' for the Financial Year.",
            "Download PDF certificates for both Savings Account Interest and Term/FD Interest."
        ],
        mandatory=True,
        applicable_reasons=["Required for reporting income under 'Income from Other Sources'"]
    ))

    # --- DECISION TREE LOGIC ---

    # Rule Set 1: Check for ITR-3 Triggers (Business / Profession / F&O Trading)
    # F&O and Intraday are classified as business income under Income Tax Act
    if profile.has_fo_or_intraday:
        form = "ITR-3"
        form_title = "ITR-3 (Profits and Gains of Business or Profession)"
        primary_reasons.append("Futures & Options (F&O) and Intraday equity trading are legally treated as non-speculative and speculative business turnover, mandating ITR-3.")
        compliance_risks.append("Notice 139(9) Risk: Reporting F&O trading in ITR-1 or ITR-2 will cause your return to be declared defective.")
        
        required_docs.append(DocumentRequirement(
            id="broker_tax_pnl",
            name="Broker Tax P&L Statement (F&O & Intraday Turnover)",
            description="Consolidated statement of realized trading profit/loss, turnover, and charges.",
            source="Broker Backoffice (Zerodha Console, Groww, Upstox, Angel One)",
            download_steps=[
                "Log in to your broker console (e.g. Zerodha Console -> Reports -> Tax P&L).",
                "Select the Financial Year.",
                "Download the Tax P&L Excel/PDF showing Turnover, Speculative P&L, and Non-speculative F&O P&L."
            ],
            mandatory=True,
            applicable_reasons=["Required to fill Schedule BP (Business & Profession) and Schedule Turnover"]
        ))
        
        summary = "You must file ITR-3 because trading in F&O or Intraday is categorized as business income under Indian tax laws."
        return FormDiagnosisResponse(
            recommended_form=form,
            form_title=form_title,
            summary_verdict=summary,
            primary_reasons=primary_reasons,
            disqualifications=disqualifications,
            compliance_risks=compliance_risks,
            required_documents=required_docs
        )

    # Business / Profession without Presumptive Tax -> ITR-3
    if profile.has_business_or_profession and not profile.is_presumptive_eligible:
        form = "ITR-3"
        form_title = "ITR-3 (Profits and Gains of Business or Profession)"
        primary_reasons.append("Income from business or independent profession without opting for presumptive taxation requires maintenance of books and filing under ITR-3.")
        
        required_docs.append(DocumentRequirement(
            id="financial_statements",
            name="Profit & Loss Account and Balance Sheet",
            description="Summary of gross business receipts, allowable expenses, net profit, assets, and liabilities.",
            source="Accounting Software / Bookkeeper",
            download_steps=[
                "Export Balance Sheet and P&L statement for the FY (April 1 to March 31).",
                "Ensure gross receipts tally with 26AS / AIS TDS credits."
            ],
            mandatory=True,
            applicable_reasons=["Required to complete Schedule P&L and Balance Sheet in ITR-3"]
        ))

        summary = "You must file ITR-3 because you have regular business or professional income without the presumptive scheme."
        return FormDiagnosisResponse(
            recommended_form=form,
            form_title=form_title,
            summary_verdict=summary,
            primary_reasons=primary_reasons,
            disqualifications=disqualifications,
            compliance_risks=compliance_risks,
            required_documents=required_docs
        )

    # Rule Set 2: Check for ITR-4 (Sugam) Eligibility (Presumptive Taxation u/s 44AD / 44ADA)
    if profile.has_business_or_profession and profile.is_presumptive_eligible:
        # Check disqualifications for ITR-4:
        itr4_disqualified = False
        if profile.total_income_exceeds_50_lakh:
            itr4_disqualified = True
            disqualifications.append("Total income exceeds ₹50 Lakh, which exceeds the limit for ITR-4.")
        if profile.has_capital_gains:
            itr4_disqualified = True
            disqualifications.append("Capital gains from selling shares, mutual funds, or property cannot be filed in ITR-4.")
        if profile.has_crypto_or_vda:
            itr4_disqualified = True
            disqualifications.append("Crypto / VDA income cannot be reported in ITR-4.")
        if profile.house_property_count > 1:
            itr4_disqualified = True
            disqualifications.append("Owning more than one house property is not permitted in ITR-4.")
        if profile.is_company_director:
            itr4_disqualified = True
            disqualifications.append("Holding directorship in a company is not allowed in ITR-4.")
        if profile.holds_unlisted_shares:
            itr4_disqualified = True
            disqualifications.append("Holding unlisted equity shares is not allowed in ITR-4.")
        if profile.has_foreign_assets_or_income:
            itr4_disqualified = True
            disqualifications.append("Holding foreign assets or earning foreign income disqualifies you from ITR-4.")
        if not profile.is_resident:
            itr4_disqualified = True
            disqualifications.append("Non-Residents (NRI) cannot file ITR-4.")

        if not itr4_disqualified:
            form = "ITR-4"
            form_title = "ITR-4 (Sugam) — Presumptive Taxation"
            primary_reasons.append("Eligible for Presumptive Taxation Scheme under Section 44ADA (freelancers/professionals) or Section 44AD (small businesses).")
            primary_reasons.append("Total income is within ₹50 Lakh with no disqualifying capital gains or foreign assets.")
            
            required_docs.append(DocumentRequirement(
                id="gross_receipts_summary",
                name="Bank Statements & Gross Receipts Summary (44AD / 44ADA)",
                description="Total gross professional receipts or business turnover received during the FY.",
                source="Bank Account Statements & Invoices",
                download_steps=[
                    "Calculate total professional fees received in all bank accounts from April 1 to March 31.",
                    "Presumptive profit declared must be at least 50% for 44ADA (professionals) or 6%/8% for 44AD (businesses)."
                ],
                mandatory=True,
                applicable_reasons=["Required for Section 44ADA / 44AD presumptive calculation"]
            ))

            summary = "You qualify for the simplified ITR-4 (Sugam) under the Presumptive Taxation Scheme, avoiding the need to maintain extensive audit books."
            return FormDiagnosisResponse(
                recommended_form=form,
                form_title=form_title,
                summary_verdict=summary,
                primary_reasons=primary_reasons,
                disqualifications=disqualifications,
                compliance_risks=compliance_risks,
                required_documents=required_docs
            )
        else:
            # Disqualified from ITR-4 with business income -> Must file ITR-3
            form = "ITR-3"
            form_title = "ITR-3 (Profits and Gains of Business or Profession)"
            primary_reasons.append("You have business/professional income, but specific disqualifying conditions prevent using ITR-4 Sugam.")
            summary = "You must file ITR-3 because your profile exceeds ITR-4 limits or contains capital gains / foreign assets."
            return FormDiagnosisResponse(
                recommended_form=form,
                form_title=form_title,
                summary_verdict=summary,
                primary_reasons=primary_reasons,
                disqualifications=disqualifications,
                compliance_risks=compliance_risks,
                required_documents=required_docs
            )

    # Rule Set 3: Check for ITR-1 (Sahaj) vs ITR-2 (No business income)
    itr1_disqualifications: List[str] = []

    if not profile.is_resident:
        itr1_disqualifications.append("Non-Resident Indians (NRIs) and Not Ordinarily Residents (RNOR) cannot file ITR-1.")
    if profile.total_income_exceeds_50_lakh:
        itr1_disqualifications.append("Total income exceeds ₹50 Lakh (Section 139(1) limit for ITR-1).")
    if profile.has_capital_gains:
        itr1_disqualifications.append("Sold equity shares, mutual funds, gold, or property resulting in Capital Gains (STCG/LTCG).")
    if profile.has_crypto_or_vda:
        itr1_disqualifications.append("Traded or held Virtual Digital Assets (Crypto / NFTs) taxable u/s 115BBH.")
    if profile.house_property_count > 1:
        itr1_disqualifications.append(f"Owns {profile.house_property_count} house properties (ITR-1 is strictly limited to 1 property).")
    if profile.is_company_director:
        itr1_disqualifications.append("Directorship in an Indian or foreign company mandates reporting in ITR-2.")
    if profile.holds_unlisted_shares:
        itr1_disqualifications.append("Holding unlisted equity shares requires detailed reporting in ITR-2.")
    if profile.has_foreign_assets_or_income:
        itr1_disqualifications.append("Foreign assets (Schedule FA), foreign bank accounts, or foreign ESOPs mandate ITR-2.")
    if profile.agricultural_income_exceeds_5000:
        itr1_disqualifications.append("Agricultural income exceeds ₹5,000 (limit for ITR-1).")
    if profile.has_brought_forward_losses:
        itr1_disqualifications.append("Carrying forward losses or claiming brought-forward losses cannot be done in ITR-1.")

    if not itr1_disqualifications:
        # Perfectly qualified for ITR-1 (Sahaj)
        form = "ITR-1"
        form_title = "ITR-1 (Sahaj) — Salaried & Pensioners"
        primary_reasons.append("Resident individual with total income under ₹50 Lakh.")
        primary_reasons.append("Income from salary/pension, single house property, and other sources (bank interest, dividends).")
        primary_reasons.append("No capital gains, no business income, and no foreign assets.")
        summary = "You qualify for ITR-1 (Sahaj), the simplest and fastest Income Tax Return form."
    else:
        # Disqualified from ITR-1 -> Must file ITR-2
        form = "ITR-2"
        form_title = "ITR-2 — Capital Gains, High Net Worth & Multi-Property"
        primary_reasons.append("You do not have business or profession income, but you have transactions that exceed ITR-1 eligibility.")
        disqualifications.extend(itr1_disqualifications)
        compliance_risks.append("Notice 139(9) Risk: Filing ITR-1 when you have mutual fund or stock sales is the #1 cause of defective return notices from CPC Bangalore.")
        summary = "You must file ITR-2 because your income includes capital gains, multiple properties, or exceeds ₹50 Lakh."

        # Add capital gains documents if applicable
        if profile.has_capital_gains or profile.has_crypto_or_vda:
            required_docs.append(DocumentRequirement(
                id="broker_capital_gains",
                name="Capital Gains Tax Statement (Mutual Funds & Stocks)",
                description="Detailed schedule of Long-Term (Sec 112A) and Short-Term (Sec 111A) Capital Gains, purchase dates, and grandfathering values.",
                source="Broker portals (Zerodha Console, Groww, CAMS/KFintech)",
                download_steps=[
                    "For Mutual Funds: Log in to CAMS (camsonline.com) or KFintech and request consolidated Capital Gains Statement.",
                    "For Stocks: Log in to your broker (e.g. Zerodha -> Console -> Reports -> Tax P&L) and download Capital Gains PDF/Excel for the FY.",
                    "Ensure quarterly breakdown is present for Schedule CG."
                ],
                mandatory=True,
                applicable_reasons=["Mandatory for Schedule CG (Capital Gains) in ITR-2"]
            ))

    return FormDiagnosisResponse(
        recommended_form=form,
        form_title=form_title,
        summary_verdict=summary,
        primary_reasons=primary_reasons,
        disqualifications=disqualifications,
        compliance_risks=compliance_risks,
        required_documents=required_docs
    )

