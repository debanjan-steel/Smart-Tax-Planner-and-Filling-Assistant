from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from backend.app.models.documents import Form16Parsed, AISParsed, ReconciliationReport
from backend.app.services.doc_parser import (
    extract_text_from_pdf, 
    parse_form16_text, 
    parse_ais_data, 
    reconcile_documents
)

router = APIRouter(prefix="/documents", tags=["Tax Document Ingestion & Parsers"])

@router.post("/parse-form16", response_model=Form16Parsed)
async def parse_form16(
    file: UploadFile = File(...),
    password: Optional[str] = Form(None)
):
    """
    Parses Form 16 PDF in RAM without disk storage (DPDP Act 2023 compliant).
    Extracts Employer TAN, gross salary u/s 17(1), exemptions u/s 10,
    standard deduction, Chapter VI-A deductions, and TDS deposited.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Form 16 must be a PDF file.")
        
    content = await file.read()
    try:
        text = extract_text_from_pdf(content, password=password)
        if not text.strip():
            raise HTTPException(
                status_code=422, 
                detail="Could not extract text. If the PDF is password-protected, please provide your PAN or password."
            )
        return parse_form16_text(text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing Form 16: {str(e)}")

@router.post("/parse-ais", response_model=AISParsed)
async def parse_ais(
    file: UploadFile = File(...),
    password: Optional[str] = Form(None)
):
    """
    Parses Annual Information Statement (AIS) from official JSON or PDF in RAM.
    Extracts Savings Interest (SFT-005), Term Deposits (SFT-006),
    Dividends (SFT-015), and Securities Sale Turnover (SFT-012).
    """
    filename = file.filename.lower()
    if not (filename.endswith(".pdf") or filename.endswith(".json")):
        raise HTTPException(status_code=400, detail="AIS must be a JSON or PDF file.")

    content = await file.read()
    try:
        return parse_ais_data(content, filename=filename, password=password)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing AIS: {str(e)}")

@router.post("/reconcile", response_model=ReconciliationReport)
def reconcile(report_input: dict):
    """
    Cross-checks Form 16 and AIS data to detect discrepancy traps before portal filing.
    """
    form16_dict = report_input.get("form16")
    ais_dict = report_input.get("ais")
    
    form16 = Form16Parsed(**form16_dict) if form16_dict else None
    ais = AISParsed(**ais_dict) if ais_dict else None
    
    return reconcile_documents(form16, ais)

