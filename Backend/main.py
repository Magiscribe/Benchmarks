"""
FastAPI backend for LLM Eye Test data visualization.
Provides dynamic data analysis endpoints for the frontend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import data
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="LLM Eye Test API",
    description="Backend API for visualizing LLM performance on eye test benchmarks",
    version="1.0.0"
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default + common React ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(data.router, prefix="/api", tags=["data"])

@app.get("/")
async def root():
    """Root endpoint for API health check."""
    return {"message": "LLM Eye Test API is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "api": "LLM Eye Test API", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
