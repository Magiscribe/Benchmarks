"""
Minimal API routes for test type selection.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from ..models.schemas import TestTypeInfo, ResultsRequest, ResultsResponse
from services.data_service import data_service

router = APIRouter()


@router.get("/available-tests", response_model=List[TestTypeInfo])
async def get_available_tests():
    """Get all available test types with their configurations."""
    try:
        return data_service.get_available_test_types()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/available-models/{test_type}")
async def get_available_models(test_type: str):
    """Get all available models for a specific test type."""
    try:
        return data_service.get_available_models(test_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/available-filters/{test_type}")
async def get_available_filters(test_type: str):
    """Get all available filters (identifier and categorical columns) for a specific test type."""
    try:
        return data_service.get_available_filters(test_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/available-filter-values/{test_type}/{filter_name}")
async def get_available_filter_values(test_type: str, filter_name: str):
    """Get all unique values for a specific filter in a test type."""
    try:
        return data_service.get_available_filter_values(test_type, filter_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/available-metrics/{test_type}")
async def get_available_metrics(test_type: str):
    """Get all available metrics for a specific test type."""
    try:
        return data_service.get_available_metrics(test_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/available-parameters/{test_type}/{metric_name}")
async def get_available_parameters(test_type: str, metric_name: str):
    """Get all available parameters for a specific metric in a test type."""
    try:
        return data_service.get_available_parameters(test_type, metric_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/results/{test_type}/{metric}", response_model=ResultsResponse)
async def get_results(test_type: str, metric: str, request: ResultsRequest, group_by: Optional[str] = Query(None)):
    """Get filtered results grouped by model with metric calculation."""
    try:
        # Parse group_by query parameter if provided
        group_by_columns = None
        if group_by:
            group_by_columns = [col.strip() for col in group_by.split(',')]
        return data_service.get_results(test_type, metric, request, group_by=group_by_columns)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


