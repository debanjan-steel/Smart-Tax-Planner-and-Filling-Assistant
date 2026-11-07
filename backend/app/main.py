from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.api.questionnaire import router as questionnaire_router
from backend.app.api.documents import router as documents_router
from backend.app.api.rules import router as rules_router
from backend.app.api.tax_calculator import router as tax_router
from backend.app.api.portal import router as portal_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for TaxSahayak: Smart Tax Planner & Official Portal Filing Assistant.",
)

# CORS configuration to allow local PWA development and production clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(questionnaire_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(rules_router, prefix="/api/v1")
app.include_router(tax_router, prefix="/api/v1")
app.include_router(portal_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "supported_years": settings.SUPPORTED_ASSESSMENT_YEARS,
        "ephemeral_mode": settings.EPHEMERAL_MODE,
    }

@app.get("/")
def root():
    return {
        "message": "Welcome to TaxSahayak API",
        "docs": "/docs",
        "health": "/health",
    }
