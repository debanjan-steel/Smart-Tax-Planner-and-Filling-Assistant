import os
from pydantic import BaseModel

class Settings(BaseModel):
    APP_NAME: str = "TaxSahayak: Smart Tax Planner & Portal Filing Guide"
    APP_VERSION: str = "0.2.0"
    API_V1_PREFIX: str = "/api/v1"
    SUPPORTED_ASSESSMENT_YEARS: list[str] = ["2025-26", "2024-25"]
    DEFAULT_ASSESSMENT_YEAR: str = "2025-26"
    
    # DPDP Act 2023 & Privacy Policy
    EPHEMERAL_MODE: bool = True
    MAX_UPLOAD_SIZE_MB: int = 15
    ALLOWED_EXTENSIONS: list[str] = [".pdf", ".json", ".xlsx", ".csv"]

settings = Settings()
