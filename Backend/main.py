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

# Include benchmark routes
app.include_router(data.router, tags=["benchmarks"])

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
            "/benchmarks": "Get all benchmarks",
            "/benchmarks/{benchmark_id}/models": "Get all available models for a benchmark",
            "/benchmarks/{benchmark_id}/assets": "Get available asset IDs for a benchmark",
            "/benchmarks/{benchmark_id}/metrics": "Get available metrics for a benchmark",
            "/benchmarks/{benchmark_id}/filters": "Get available filters for a benchmark",
            "/benchmarks/{benchmark_id}/metrics/{metric_id}": "Get filtered results with metric calculation",
            "/benchmarks/{benchmark_id}/visualizations/{model}/{asset_id}": "Get visualization overlay for specific benchmark asset"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "benchmark-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
