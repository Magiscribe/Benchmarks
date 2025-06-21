"""
Minimal API routes for test type selection.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from ..models.schemas import ResultsRequest, ResultsResponse
from services.data_service import data_service
from services.visualization_service import visualization_service

router = APIRouter()


@router.get("/benchmarks")
async def get_benchmarks():
    """Get all available benchmarks."""
    try:
        return data_service.get_benchmarks()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/benchmarks/{benchmark_id}/models")
async def get_available_models(benchmark_id: str):
    """Get all available models for a specific benchmark."""
    try:
        return data_service.get_available_models(benchmark_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/benchmarks/{benchmark_id}/metrics")
async def get_available_metrics(benchmark_id: str):
    """Get all available metrics for a specific benchmark."""
    try:
        return data_service.get_benchmark_metrics(benchmark_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/benchmarks/{benchmark_id}/filters")
async def get_available_filters(benchmark_id: str):
    """Get all available filters for a specific benchmark."""
    try:
        return data_service.get_benchmark_filters(benchmark_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/benchmarks/{benchmark_id}/metrics/{metric_id}", response_model=ResultsResponse)
async def get_results(benchmark_id: str, metric_id: str, request: ResultsRequest, group_by: Optional[str] = Query(None)):
    """Get filtered results for a specific benchmark and metric."""
    try:
        # Parse group_by query parameter if provided
        group_by_columns = None
        if group_by:
            group_by_columns = [col.strip() for col in group_by.split(',')]
        return data_service.get_benchmark_results(benchmark_id, metric_id, request, group_by=group_by_columns)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/benchmarks/{benchmark_id}/visualizations/{model}/{asset_id}")
async def get_visualization(benchmark_id: str, model: str, asset_id: str):
    """Generate visualization overlay for a specific benchmark, model, and asset."""
    try:
        return visualization_service.generate_visualization(benchmark_id, model, asset_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/benchmarks/{benchmark_id}/assets")
async def get_available_assets(benchmark_id: str):
    """Get all available asset IDs for a specific benchmark."""
    try:
        return data_service.get_available_assets(benchmark_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


