import io
import re
import json
from typing import Optional, List, Dict, Any
from pypdf import PdfReader
import pdfplumber

from backend.app.models.documents import (
    Form16Parsed, 
    Form16SalaryBreakup, 
    Form16Deductions, 
    AISParsed, 
    AISFinancialItem,
    ReconciliationReport,
    DiscrepancyNotice
)
from backend.app.core.dpdp_compliance import mask_pan

def clean_amount(val_str: Any) -> float:
    """Parses Indian comma-separated currency string (e.g. '12,50,000.00' or '₹ 85,000') into float."""
    if val_str is None:
        return 0.0
    if isinstance(val_str, (int, float)):
        return float(val_str)
    cleaned = re.sub(r"[^\d.-]", "", str(val_str))
    try:
        return float(cleaned) if cleaned else 0.0
    except ValueError:
        return 0.0

def extract_text_from_pdf(file_bytes: bytes, password: Optional[str] = None) -> str:
    """Extracts text from PDF bytes in-memory using pdfplumber with pypdf fallback."""
    full_text = []
    stream = io.BytesIO(file_bytes)
    
    try:
        with pdfplumber.open(stream, password=password or "") as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text.append(text)
    except Exception:
        # Fallback to pypdf
        stream.seek(0)
        reader = PdfReader(stream)
        if reader.is_encrypted and password:
            reader.decrypt(password)
        for page in reader.pages:
            t = page.extract_text()
            if t:
                full_text.append(t)
                
    return "\n".join(full_text)

def parse_form16_text(text: str) -> Form16Parsed:
    """
    Parses TRACES-compliant Form 16 text using resilient pattern matching
    for Section 17 salary, Section 10 exemptions, and Chapter VI-A deductions.
    """
    notes: List[str] = []
    
    # Extract PAN and TAN
    pan_matches = re.findall(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", text)
    tan_matches = re.findall(r"\b[A-Z]{4}[0-9]{5}[A-Z]\b", text)
    
    employer_tan = tan_matches[0] if tan_matches else "XXXX00000X"
    employer_pan = pan_matches[0] if len(pan_matches) > 0 else "XXXXX0000X"
    employee_pan = pan_matches[1] if len(pan_matches) > 1 else (pan_matches[0] if pan_matches else "XXXXX0000X")
    
    # Extract Assessment Year
    ay_match = re.search(r"Assessment\s+Year\s*[:\-]?\s*([0-9]{4}\s*[-–]\s*[0-9]{2,4})", text, re.I)
    assessment_year = "2025-26"
    if ay_match:
        raw_ay = ay_match.group(1).replace(" ", "")
        if "-" in raw_ay and len(raw_ay) == 7:
            assessment_year = raw_ay

    # Extract Salary Breakdown
    gross_17_1 = 0.0
    sec_17_1_match = re.search(r"(?:Salary\s+as\s+per\s+provisions\s+contained\s+in\s+section\s+17\(1\)|Gross\s+Salary[^\n\d]*)\s*[:\-]?\s*(?:Rs\.?)?\s*([\d,]+\.?\d*)", text, re.I)
    if sec_17_1_match:
        gross_17_1 = clean_amount(sec_17_1_match.group(1))

    # Exemptions u/s 10 (e.g. HRA u/s 10(13A))
    hra_amt = 0.0
    hra_match = re.search(r"(?:House\s+Rent\s+Allowance|HRA)[^\n]*?(?:Rs\.?|INR|[:\-])\s*([\d,]+\.?\d*)", text, re.I)
    if hra_match:
        hra_amt = clean_amount(hra_match.group(1))

    total_exempt_10 = hra_amt
    exempt_10_match = re.search(r"(?:Total\s+(?:amount\s+of\s+any\s+other\s+)?exemption\s+under\s+section\s+10)[^\n]*?(?:Rs\.?|INR|[:\-])\s*([\d,]+\.?\d*)", text, re.I)
    if exempt_10_match:
        parsed_exempt = clean_amount(exempt_10_match.group(1))
        if parsed_exempt > 0:
            total_exempt_10 = parsed_exempt

    # Standard Deduction u/s 16(ia)
    std_ded = 50000.0
    std_match = re.search(r"Standard\s+deduction\s+under\s+section\s+16\(ia\)[^\n]*?(?:Rs\.?|INR|[:\-])\s*([\d,]+\.?\d*)", text, re.I)
    if std_match:
        std_ded = clean_amount(std_match.group(1))

    # Professional Tax u/s 16(iii)
    prof_tax = 0.0
    pt_match = re.search(r"(?:Tax\s+on\s+employment|Professional\s+Tax)[^\n]*?(?:Rs\.?|INR|[:\-])\s*([\d,]+\.?\d*)", text, re.I)
    if pt_match:
        prof_tax = clean_amount(pt_match.group(1))

    # Income chargeable under Salaries
    income_salaries = max(0.0, gross_17_1 - total_exempt_10 - std_ded - prof_tax)

    # Chapter VI-A Deductions
    ded_80c = 0.0
    m_80c = re.search(r"(?:80C|Deduction\s+under\s+section\s+80C)[^\n\d]*\s*[:\-]?\s*([\d,]+\.?\d*)", text, re.I)
    if m_80c:
        ded_80c = min(150000.0, clean_amount(m_80c.group(1)))

    ded_80ccd = 0.0
    m_80ccd = re.search(r"(?:80CCD\(1B\)|NPS)[^\n\d]*\s*[:\-]?\s*([\d,]+\.?\d*)", text, re.I)
    if m_80ccd:
        ded_80ccd = min(50000.0, clean_amount(m_80ccd.group(1)))

    ded_80d = 0.0
    m_80d = re.search(r"(?:80D|Health\s+Insurance)[^\n\d]*\s*[:\-]?\s*([\d,]+\.?\d*)", text, re.I)
    if m_80d:
        ded_80d = clean_amount(m_80d.group(1))

    ded_24b = 0.0
    m_24b = re.search(r"(?:24\(b\)|Interest\s+on\s+housing\s+loan)[^\n\d]*\s*[:\-]?\s*([\d,]+\.?\d*)", text, re.I)
    if m_24b:
        ded_24b = clean_amount(m_24b.group(1))

    total_via = ded_80c + ded_80ccd + ded_80d

    # Total Taxable Income
    taxable_inc = max(0.0, income_salaries - total_via - ded_24b)
    
    # TDS Deducted
    tds_amt = 0.0
    tds_match = re.search(r"(?:Total\s+tax\s+deducted\s+and\s+deposited|Tax\s+payable|TDS\s+deposited)[^\n\d]*\s*[:\-]?\s*([\d,]+\.?\d*)", text, re.I)
    if tds_match:
        tds_amt = clean_amount(tds_match.group(1))

    notes.append(f"Parsed Form 16 for AY {assessment_year}. Detected Gross Salary: ₹{gross_17_1:,.2f}.")

    return Form16Parsed(
        employer_name="Parsed Employer from Form 16",
        employer_tan=employer_tan,
        employer_pan=employer_pan,
        employee_pan=employee_pan,
        assessment_year=assessment_year,
        financial_year="2024-25" if "2025-26" in assessment_year else "2023-24",
        salary_breakup=Form16SalaryBreakup(
            gross_salary_sec17_1=gross_17_1,
            total_gross_salary=gross_17_1,
            hra_exempt_sec10_13a=hra_amt,
            total_exemptions_sec10=total_exempt_10,
            net_salary=gross_17_1 - total_exempt_10,
            standard_deduction_sec16_ia=std_ded,
            professional_tax_sec16_iii=prof_tax,
            income_chargeable_salaries=income_salaries
        ),
        deductions=Form16Deductions(
            section_80c=ded_80c,
            section_80ccd_1b=ded_80ccd,
            section_80d_health_insurance=ded_80d,
            section_24b_house_loan_interest=ded_24b,
            total_chapter_via_deductions=total_via
        ),
        gross_total_income=income_salaries,
        total_taxable_income=taxable_inc,
        total_tds_deducted=tds_amt,
        confidence_score=0.92 if gross_17_1 > 0 else 0.60,
        extraction_notes=notes
    )

def parse_ais_data(raw_content: bytes, filename: str = "", password: Optional[str] = None) -> AISParsed:
    """
    Parses Annual Information Statement (AIS) from either official JSON or PDF.
    Extracts Savings Interest (SFT-005), Term Deposit Interest (SFT-006),
    Dividends (SFT-015), and Securities Sale Turnover (SFT-012).
    """
    items: List[AISFinancialItem] = []
    total_savings = 0.0
    total_fd = 0.0
    total_dividend = 0.0
    total_securities = 0.0
    total_tds = 0.0
    notes: List[str] = []
    pan = "XXXXX0000X"

    # Try parsing as JSON first
    is_json = False
    try:
        data = json.loads(raw_content.decode("utf-8"))
        is_json = True
    except Exception:
        pass

    if is_json:
        notes.append("Parsed structured AIS JSON successfully.")
        # Traverse ITD AIS JSON structure
        # Official AIS has sftDtls, tdsDtls, etc.
        sft_entries = data.get("sftDtls", []) or data.get("sft", []) or []
        for entry in sft_entries:
            code = entry.get("infoCode", "") or entry.get("sftCode", "")
            desc = entry.get("infoDesc", "") or entry.get("description", "Financial Transaction")
            reporter = entry.get("reportedBy", "") or entry.get("source", "Financial Institution")
            val = clean_amount(entry.get("infoVal", 0) or entry.get("amount", 0))

            if "interest" in desc.lower() or code in ["SFT-005", "SFT-006"]:
                if "saving" in desc.lower() or code == "SFT-005":
                    total_savings += val
                    cat = "Savings Bank Interest"
                else:
                    total_fd += val
                    cat = "Fixed Deposit (FD) Interest"
            elif "dividend" in desc.lower() or code == "SFT-015":
                total_dividend += val
                cat = "Dividend Income"
            elif "securities" in desc.lower() or "mutual fund" in desc.lower() or code == "SFT-012":
                total_securities += val
                cat = "Securities Sale Turnover"
            else:
                cat = "Other Specified Financial Transaction"

            items.append(AISFinancialItem(
                category=cat,
                sft_code=code,
                description=desc,
                reported_by=reporter,
                amount=val
            ))

        tds_entries = data.get("tdsDtls", []) or data.get("tds", []) or []
        for t in tds_entries:
            amt = clean_amount(t.get("tdsDedAmt", 0) or t.get("taxDeducted", 0))
            total_tds += amt
    else:
        # Parse from PDF text
        text = extract_text_from_pdf(raw_content, password=password)
        notes.append("Extracted AIS from PDF text stream.")
        
        # Regex for PAN
        pans = re.findall(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", text)
        if pans:
            pan = pans[0]

        # Extract Savings Interest entries
        for match in re.finditer(r"(?:Interest\s+from\s+savings\s+bank|Savings\s+Bank\s+Interest)[^\n\d]*\s*[:\-]?\s*([\d,]+\.?\d*)", text, re.I):
            val = clean_amount(match.group(1))
            total_savings += val
            items.append(AISFinancialItem(
                category="Savings Bank Interest",
                description="Savings Bank Interest reported in AIS",
                reported_by="Bank",
                amount=val
            ))

        # Extract Time Deposit / FD Interest
        for match in re.finditer(r"(?:Interest\s+from\s+deposit|Time\s+Deposit\s+Interest|FD\s+Interest)[^\n\d]*\s*[:\-]?\s*([\d,]+\.?\d*)", text, re.I):
            val = clean_amount(match.group(1))
            total_fd += val
            items.append(AISFinancialItem(
                category="Fixed Deposit (FD) Interest",
                description="Term Deposit Interest reported in AIS",
                reported_by="Bank",
                amount=val
            ))

        # Extract Dividends
        for match in re.finditer(r"(?:Dividend\s+Income|Dividend)[^\n\d]*\s*[:\-]?\s*([\d,]+\.?\d*)", text, re.I):
            val = clean_amount(match.group(1))
            total_dividend += val
            items.append(AISFinancialItem(
                category="Dividend Income",
                description="Dividend from companies/mutual funds",
                reported_by="Registrar / Depository",
                amount=val
            ))

    return AISParsed(
        taxpayer_pan=pan,
        total_savings_interest=total_savings,
        total_fd_interest=total_fd,
        total_dividend_income=total_dividend,
        total_securities_sale_turnover=total_securities,
        total_tds_reported_ais=total_tds,
        items=items,
        high_value_transactions_count=len([i for i in items if i.amount >= 1000000]),
        extraction_notes=notes
    )

def reconcile_documents(form16: Optional[Form16Parsed], ais: Optional[AISParsed]) -> ReconciliationReport:
    """
    Performs cross-verification and discrepancy detection between Form 16 and AIS.
    Flags potential Section 143(1) and 139(9) defective notice triggers.
    """
    discrepancies: List[DiscrepancyNotice] = []
    total_income = 0.0
    total_tds = 0.0

    if form16:
        total_income += form16.gross_total_income
        total_tds += form16.total_tds_deducted

    if ais:
        total_other_income = ais.total_savings_interest + ais.total_fd_interest + ais.total_dividend_income
        total_income += total_other_income

        # Discrepancy Check 1: Undeclared Interest Income
        if total_other_income > 0:
            discrepancies.append(DiscrepancyNotice(
                severity="HIGH",
                title="AIS Reports ₹{:,.2f} in Interest & Dividends".format(total_other_income),
                message="The Income Tax Department already has automated records of your Savings Interest (₹{:,.2f}), FD Interest (₹{:,.2f}), and Dividends (₹{:,.2f}).".format(
                    ais.total_savings_interest, ais.total_fd_interest, ais.total_dividend_income
                ),
                legal_impact="Omitting bank interest reported in AIS is the #1 trigger for automated demand intimations under Section 143(1)(a).",
                recommended_action="Ensure this total (₹{:,.2f}) is included under 'Schedule Other Sources' on the e-filing portal.".format(total_other_income)
            ))

        # Discrepancy Check 2: Securities / Mutual Fund Selling
        if ais.total_securities_sale_turnover > 0:
            discrepancies.append(DiscrepancyNotice(
                severity="WARNING",
                title="Securities Sale of ₹{:,.2f} Detected in AIS".format(ais.total_securities_sale_turnover),
                message="AIS reports mutual fund redemptions or stock sales. Capital gains must be calculated.",
                legal_impact="Requires filing ITR-2 instead of ITR-1. Filing ITR-1 will result in a Section 139(9) defective return notice.",
                recommended_action="Obtain the consolidated Capital Gains statement from CAMS / KFintech or your broker (Zerodha/Groww)."
            ))

        # Discrepancy Check 3: TDS Cross-Verification
        if form16 and ais.total_tds_reported_ais > 0:
            if abs(form16.total_tds_deducted - ais.total_tds_reported_ais) > 500:
                discrepancies.append(DiscrepancyNotice(
                    severity="WARNING",
                    title="TDS Mismatch between Form 16 and AIS",
                    message="Form 16 shows ₹{:,.2f} TDS, while AIS reflects ₹{:,.2f} TDS.".format(
                        form16.total_tds_deducted, ais.total_tds_reported_ais
                    ),
                    legal_impact="The IT Department allows tax credit strictly based on what is reflected in 26AS/AIS, not Form 16.",
                    recommended_action="Verify Form 26AS to confirm that your employer has deposited the tax and filed quarterly TDS returns."
                ))

    return ReconciliationReport(
        form16_summary=form16,
        ais_summary=ais,
        total_estimated_gross_income=total_income,
        total_tds_available=total_tds,
        discrepancies=discrepancies
    )
