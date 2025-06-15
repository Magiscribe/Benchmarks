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
            "/benchmarks": "Get all benchmarks",
            "/models/{test_type}": "Get all available models for a benchmark type", # /eye_test/models
            "/assets/{test_type}": "Get available asset IDs for a benchmark type",
            "/filters/{test_type}": "Get available filters for a benchmark type",
            "/filter-values/{test_type}/{filter_name}": "Get unique values for a filter",
            "/metrics/{test_type}": "Get available metrics for a benchmark type",
            "/parameters/{test_type}/{metric_name}": "Get parameters for a metric",
            "/results/{test_type}/{metric}": "Get filtered results with metric calculation",
            "/visualizations/{test_type}/{model}/{asset_id}": "Get visualization overlay for specific benchmark asset"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "benchmark-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
