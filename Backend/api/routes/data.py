"""
API routes for data endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from services.data_service import data_service
from api.models.schemas import FilterOptions, AccuracyRequest, AccuracyResponse

router = APIRouter()

@router.get("/filters", response_model=FilterOptions)
async def get_filter_options():
    """
    Get available filter options from the dataset.
    
    Returns:
        FilterOptions: Unique models, fonts, and sizes available
    """
    try:
        return data_service.get_filter_options()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get filter options: {str(e)}")

@router.post("/accuracy", response_model=AccuracyResponse)
async def calculate_accuracy(request: AccuracyRequest):
    """
    Calculate accuracy data based on filter criteria.
    
    Args:
        request: Filter criteria (fonts, sizes, models)
        
    Returns:
        AccuracyResponse: Accuracy results with metadata
    """
    try:
        accuracy_data = data_service.calculate_accuracy(request)
        
        return AccuracyResponse(
            data=accuracy_data,
            filters_applied=request,
            total_models=len(accuracy_data)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate accuracy: {str(e)}")

@router.get("/raw")
async def get_raw_data(limit: Optional[int] = Query(None, description="Limit number of rows returned")):
    """
    Get raw CSV data for debugging purposes.
    
    Args:
        limit: Optional limit on number of rows
        
    Returns:
        Dict: Raw data and metadata
    """
    try:
        return data_service.get_raw_data(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get raw data: {str(e)}")

@router.get("/stats")
async def get_data_stats():
    """
    Get basic statistics about the dataset.
    
    Returns:
        Dict: Dataset statistics
    """
    try:
        filter_options = data_service.get_filter_options()
        raw_info = data_service.get_raw_data(limit=1)
        
        return {
            "total_rows": raw_info["total_rows"],
            "columns": raw_info["columns"],
            "unique_models": len(filter_options.models),
            "unique_fonts": len(filter_options.fonts),
            "unique_sizes": len(filter_options.sizes),
            "models": filter_options.models,
            "fonts": filter_options.fonts,
            "sizes": filter_options.sizes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
