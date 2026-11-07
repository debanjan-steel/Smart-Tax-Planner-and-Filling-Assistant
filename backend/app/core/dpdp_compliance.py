"""
DPDP Act 2023 (Digital Personal Data Protection Act, India) Compliance Safeguards.

Key Principles Enforced:
1. Zero-Credential Architecture: Never accept, store, or log Income Tax e-filing portal passwords.
2. In-Memory Ephemeral Processing: Tax documents (Form 16, AIS, 26AS) are processed strictly in RAM.
3. No Permanent Storage of Sensitive Financial PII (PAN, Aadhaar, Bank Details) without explicit user consent.
4. Immediate Purge: Extracted data structures are returned to the client and cleared from backend memory.
"""

import re
from typing import Optional

def mask_pan(pan: Optional[str]) -> str:
    """Masks PAN (e.g. ABCDE1234F -> ABCXXXX34F) for logging/preview."""
    if not pan or len(pan) != 10:
        return "XXXXX0000X"
    return f"{pan[:3]}XXXX{pan[7:]}"

def mask_aadhaar(aadhaar: Optional[str]) -> str:
    """Masks Aadhaar (e.g. 1234 5678 9012 -> XXXXXXXX9012) compliant with UIDAI guidelines."""
    if not aadhaar:
        return "XXXXXXXX0000"
    cleaned = re.sub(r"\D", "", aadhaar)
    if len(cleaned) == 12:
        return f"XXXXXXXX{cleaned[-4:]}"
    return "XXXXXXXX0000"

def mask_bank_account(account_no: Optional[str]) -> str:
    """Masks bank account number, displaying only the last 4 digits."""
    if not account_no:
        return "XXXX0000"
    cleaned = str(account_no).strip()
    if len(cleaned) <= 4:
        return cleaned
    return f"{'X' * (len(cleaned) - 4)}{cleaned[-4:]}"

