from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.auth.router import router as auth_router
from app.interview.router import router as interview_router
from app.profile.router import router as profile_router
from app.matching.router import router as matching_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Wavelength API...")
    yield
    # Shutdown
    print("Shutting down Wavelength API...")

app = FastAPI(
    title="Wavelength API",
    description="AI-powered matchmaking platform",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "0.1.0"}

# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(interview_router, prefix="/api/v1/interview", tags=["interview"])
app.include_router(profile_router, prefix="/api/v1/profile", tags=["profile"])
app.include_router(matching_router, prefix="/api/v1/matching", tags=["matching"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
