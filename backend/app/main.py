
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from app.core.config import settings
from app.api.api_v1.api import api_router
from app.core.database import init_db

app = FastAPI(
    title="CKD Predictive Care System",
    description="AI-Powered system for Chronic Kidney Disease management",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Ensure database tables exist (including new AuditEvent)
try:
    init_db()
except Exception:
    pass

# Get the project root directory (two levels up from this file)
project_root = Path(__file__).parent.parent.parent
webapp_path = project_root / "webapp"

# Serve static files (CSS, JS, images) - mount before root route
if webapp_path.exists():
    # Mount static files directory
    static_path = webapp_path
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    
    # Serve the main HTML file for root route
    @app.get("/", response_class=FileResponse)
    async def read_root():
        index_file = webapp_path / "index.html"
        if index_file.exists():
            return str(index_file)
        return {"message": "Welcome to CKD Predictive Care System API"}

@app.get("/api")
async def api_info():
    return {"message": "Welcome to CKD Predictive Care System API", "docs": "/docs"}