import os
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
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
    allow_origins=["*"],
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

# Locate frontend dist folder for unified production PWA serving
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist")

if os.path.exists(os.path.join(FRONTEND_DIST, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

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
def root(request: Request):
    accept = request.headers.get("accept", "")
    index_file = os.path.join(FRONTEND_DIST, "index.html")
    if "text/html" in accept and os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "message": "Welcome to TaxSahayak API",
        "docs": "/docs",
        "health": "/health",
    }

@app.get("/{full_path:path}")
def serve_spa_or_static(full_path: str, request: Request):
    # Guard internal routes
    if full_path.startswith("api/") or full_path == "health" or full_path.startswith("docs") or full_path == "openapi.json":
        return JSONResponse(status_code=404, content={"detail": "Not Found"})
    
    # Try serving static asset directly from frontend/dist (e.g., manifest, sw.js, icons)
    static_file = os.path.join(FRONTEND_DIST, full_path)
    if os.path.isfile(static_file):
        return FileResponse(static_file)
    
    # Fallback to SPA index.html for client-side navigation
    index_file = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
        
    return JSONResponse(status_code=404, content={"detail": "File not found"})
