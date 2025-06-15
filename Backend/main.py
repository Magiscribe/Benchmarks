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
        ],        "endpoints": {
            "/data/available-tests": "Get all available test types with configurations",
            "/data/available-models/{test_type}": "Get all available models for a test type",
            "/data/available-filters/{test_type}": "Get available filters for a test type",
            "/data/available-filter-values/{test_type}/{filter_name}": "Get unique values for a filter",
            "/data/available-metrics/{test_type}": "Get available metrics for a test type",
            "/data/available-parameters/{test_type}/{metric_name}": "Get parameters for a metric",
            "/data/results/{test_type}/{metric}": "Get filtered results with metric calculation"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "benchmark-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
