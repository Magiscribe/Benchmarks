"""
API routes for DSL-based metric calculations.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from services.enhanced_data_service import enhanced_data_service
from api.models.schemas import (
    MetricRequest, MetricsResponse, AvailableTestsResponse
)

router = APIRouter()

@router.get("/tests", response_model=AvailableTestsResponse)
async def get_available_tests():
    """
    Get information about all available test types and their metrics.
    
    Returns:
        AvailableTestsResponse: Available tests with their configurations
    """
    try:
        return enhanced_data_service.get_available_tests()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get available tests: {str(e)}")

@router.post("/metrics", response_model=MetricsResponse)
async def calculate_metrics(request: MetricRequest):
    """
    Calculate metrics using DSL for a specific test type.
    
    Args:
        request: Metric calculation request with test type, filters, and parameters
        
    Returns:
        MetricsResponse: Calculated metrics with metadata
    """
    try:
        return enhanced_data_service.calculate_metrics(request)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate metrics: {str(e)}")

@router.get("/tests/{test_type}/filters")
async def get_test_filter_options(test_type: str):
    """
    Get available filter options for a specific test type.
    
    Args:
        test_type: The type of test (e.g., "Eye_Test", "Coordinate_Grid")
        
    Returns:
        Dict: Available filter values for each column
    """
    try:
        return enhanced_data_service.get_filter_options_for_test(test_type)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get filter options: {str(e)}")

@router.get("/tests/{test_type}/raw")
async def get_test_raw_data(
    test_type: str, 
    limit: Optional[int] = Query(None, description="Limit number of rows returned")
):
    """
    Get raw CSV data for a specific test type.
    
    Args:
        test_type: The type of test
        limit: Optional limit on number of rows
        
    Returns:
        Dict: Raw data and metadata
    """
    try:
        return enhanced_data_service.get_raw_data(limit, test_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get raw data: {str(e)}")

@router.get("/tests/{test_type}/metrics/{metric_name}")
async def calculate_single_metric(
    test_type: str,
    metric_name: str,
    filters: Optional[str] = Query(None, description="JSON string of filters"),
    parameters: Optional[str] = Query(None, description="JSON string of parameters")
):
    """
    Calculate a single metric for a test type.
    
    Args:
        test_type: The type of test
        metric_name: Name of the metric to calculate
        filters: Optional JSON string of filters
        parameters: Optional JSON string of parameters for the metric
        
    Returns:
        Dict: Single metric result
    """
    try:
        import json
        
        # Parse optional JSON parameters
        parsed_filters = json.loads(filters) if filters else None
        parsed_parameters = json.loads(parameters) if parameters else None
        
        # Create request for single metric
        request = MetricRequest(
            test_type=test_type,
            metric_names=[metric_name],
            filters=parsed_filters,
            parameters={metric_name: parsed_parameters} if parsed_parameters else None
        )
        
        response = enhanced_data_service.calculate_metrics(request)
        
        # Return just the single metric result
        if response.metrics:
            return response.metrics[0].dict()
        else:
            raise HTTPException(status_code=404, detail=f"Metric '{metric_name}' not found")
            
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON in parameters: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate metric: {str(e)}")
