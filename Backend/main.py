"""
FastAPI application for benchmark data analysis using DSL.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import data

app = FastAPI(
    title="Benchmark Data API",
    description="API for analyzing LLM benchmark results using Domain Specific Language (DSL)",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include DSL-based data routes
app.include_router(data.router, prefix="/data", tags=["data"])

@app.get("/")
async def root():
    """Root endpoint providing API information."""
    return {
        "message": "Benchmark Data API with DSL Support",
        "version": "2.0.0",
        "features": [
            "Dynamic test type support",
            "DSL-based metric calculations", 
            "Configurable data filtering",
            "Multi-test-type support"
        ],
        "endpoints": {
            "/data/test-types": "Get available test types",
            "/data/models/{test_type}": "Get model results for a test type",
            "/data/tests/{test_type}": "Get individual test results",
            "/data/compare/{test_type}": "Compare models on a test type",
            "/data/metrics/execute": "Execute DSL metrics",
            "/data/metrics/available/{test_type}": "Get available metrics",
            "/data/filters/{test_type}": "Get filter options",
            "/data/config/{test_type}": "Get test configuration"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "benchmark-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
