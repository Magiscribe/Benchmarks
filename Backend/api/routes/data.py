"""
API routes for benchmark data operations using DSL.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from ..models.schemas import (
    ModelResult, TestResult, ModelComparison, TestTypeInfo,
    DSLExecutionRequest, DSLExecutionResponse, MetricExecutionResult,
    FilterOptions, FilterCapabilities, FilteredDataRequest, AdvancedFilter
)
from services.data_service import data_service
import time

router = APIRouter()


@router.get("/test-types", response_model=List[TestTypeInfo])
async def get_test_types():
    """Get all available test types with their configurations."""
    try:
        return data_service.get_available_test_types()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/{test_type}", response_model=List[ModelResult])
async def get_model_results(test_type: str):
    """Get results grouped by model for a specific test type."""
    try:
        results = data_service.get_model_results(test_type)
        if not results:
            raise HTTPException(status_code=404, detail=f"No results found for test type: {test_type}")
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tests/{test_type}", response_model=List[TestResult])
async def get_test_results(test_type: str, limit: Optional[int] = Query(None, description="Limit number of results")):
    """Get individual test results for a specific test type."""
    try:
        results = data_service.get_test_results(test_type)
        if not results:
            raise HTTPException(status_code=404, detail=f"No results found for test type: {test_type}")
        
        if limit:
            results = results[:limit]
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare/{test_type}", response_model=ModelComparison)
async def compare_models(test_type: str, models: List[str]):
    """Compare specific models on a test type."""
    try:
        if not models:
            raise HTTPException(status_code=400, detail="No models specified for comparison")
        
        comparison = data_service.get_model_comparison(test_type, models)
        return comparison
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/metrics/execute", response_model=DSLExecutionResponse)
async def execute_metrics(request: DSLExecutionRequest):
    """Execute DSL metrics for a test type with optional filters and parameters."""
    try:
        start_time = time.time()
        
        # Load the data
        df = data_service.load_test_results(request.test_type)
        if df is None:
            raise HTTPException(status_code=404, detail=f"No data found for test type: {request.test_type}")
        
        original_rows = len(df)
        
        # Apply legacy data filters if provided (for backward compatibility)
        if request.data_filters:
            for column, values in request.data_filters.items():
                if column in df.columns:
                    df = df[df[column].isin(values)]
        
        filtered_rows = len(df)
        
        # Load format config
        format_config = data_service.load_format_config(request.test_type)
        if not format_config:
            raise HTTPException(status_code=404, detail=f"No configuration found for test type: {request.test_type}")
        
        # Filter metrics if specific ones are requested
        metrics_to_execute = format_config.metrics
        if request.metrics:
            metrics_to_execute = [m for m in format_config.metrics if m.name in request.metrics]
        
        # Execute metrics
        metric_results = {}
        for metric in metrics_to_execute:
            try:
                # Get parameters for this metric
                params = {}
                if request.metric_parameters and metric.name in request.metric_parameters:
                    params = request.metric_parameters[metric.name]
                
                # Execute the metric
                result = data_service.dsl_executor.execute_metric(df, metric, params)
                
                metric_results[metric.name] = MetricExecutionResult(
                    name=metric.name,
                    displayName=metric.displayName,
                    description=metric.description,
                    value=result
                )
            except Exception as e:
                metric_results[metric.name] = MetricExecutionResult(
                    name=metric.name,
                    displayName=metric.displayName,
                    description=metric.description,
                    error=str(e)
                )
        
        execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return DSLExecutionResponse(
            test_type=request.test_type,
            total_rows=original_rows,
            filtered_rows=filtered_rows,
            metrics=metric_results,
            execution_time_ms=execution_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/available/{test_type}")
async def get_available_metrics(test_type: str):
    """Get available metrics for a test type."""
    try:
        format_config = data_service.load_format_config(test_type)
        if not format_config:
            raise HTTPException(status_code=404, detail=f"No configuration found for test type: {test_type}")
        
        metrics_info = []
        for metric in format_config.metrics:
            metrics_info.append({
                "name": metric.name,
                "displayName": metric.displayName,
                "description": metric.description,
                "parameters": metric.parameters or []
            })
        
        return {
            "test_type": test_type,
            "metrics": metrics_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/filters/{test_type}", response_model=FilterOptions)
async def get_filter_options(test_type: str):
    """Get available filter options for a test type."""
    try:
        df = data_service.load_test_results(test_type)
        if df is None:
            raise HTTPException(status_code=404, detail=f"No data found for test type: {test_type}")
        
        # Get format config to understand column types
        format_config = data_service.load_format_config(test_type)
        
        filter_options = FilterOptions()
        
        # Always include models
        if 'model' in df.columns:
            filter_options.models = sorted(df['model'].unique().tolist())
        
        # Add other categorical columns based on the test type
        if format_config:
            for column_def in format_config.columns:
                col_name = column_def.get('name')
                col_type = column_def.get('type')
                
                if col_name in df.columns and col_type == 'categorical':
                    unique_values = sorted(df[col_name].unique().tolist())
                    
                    if col_name == 'font':
                        filter_options.fonts = unique_values
                    elif col_name == 'size':
                        filter_options.sizes = [str(v) for v in unique_values]
                    elif col_name == 'category':
                        filter_options.categories = unique_values
                    elif col_name == 'difficulty':
                        filter_options.difficulties = unique_values
        
        return filter_options
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config/{test_type}")
async def get_test_config(test_type: str):
    """Get the complete configuration for a test type."""
    try:        
        format_config = data_service.load_format_config(test_type)
        if not format_config:
            raise HTTPException(status_code=404, detail=f"No configuration found for test type: {test_type}")
        
        return format_config.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# New Advanced Filtering Endpoints

@router.get("/filter-capabilities/{test_type}", response_model=FilterCapabilities)
async def get_filter_capabilities(test_type: str):
    """Get comprehensive filter capabilities for a test type."""
    try:
        capabilities = data_service.get_filter_capabilities(test_type)
        if not capabilities:
            raise HTTPException(status_code=404, detail=f"No filter capabilities found for test type: {test_type}")
        
        return capabilities
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data/filtered", response_model=DSLExecutionResponse)
async def get_filtered_data_with_metrics(request: FilteredDataRequest):
    """Get filtered data with DSL metrics execution. Filtering happens BEFORE DSL execution."""
    try:
        start_time = time.time()
        
        # Step 1: Load raw data
        df = data_service.load_test_results(request.test_type)
        if df is None:
            raise HTTPException(status_code=404, detail=f"No data found for test type: {request.test_type}")
        
        original_rows = len(df)
        
        # Step 2: Apply filters as preprocessing (completely separate from DSL)
        if request.filters:
            df = data_service.apply_filters(df, request.filters)
        
        filtered_rows = len(df)
        
        # Step 3: Load format config for DSL execution
        format_config = data_service.load_format_config(request.test_type)
        if not format_config:
            raise HTTPException(status_code=404, detail=f"No configuration found for test type: {request.test_type}")
        
        # Step 4: Execute DSL metrics on the filtered data
        metrics_to_execute = format_config.metrics
        if request.metrics:
            metrics_to_execute = [m for m in format_config.metrics if m.name in request.metrics]
        
        metric_results = {}
        for metric in metrics_to_execute:
            try:
                # Get parameters for this metric
                params = {}
                if request.metric_parameters and metric.name in request.metric_parameters:
                    params = request.metric_parameters[metric.name]
                
                # Execute the metric on filtered data (DSL knows nothing about filtering)
                result = data_service.dsl_executor.execute_metric(df, metric, params)
                
                metric_results[metric.name] = MetricExecutionResult(
                    name=metric.name,
                    displayName=metric.displayName,
                    description=metric.description,
                    value=result
                )
            except Exception as e:
                metric_results[metric.name] = MetricExecutionResult(
                    name=metric.name,
                    displayName=metric.displayName,
                    description=metric.description,
                    error=str(e)
                )
        
        execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return DSLExecutionResponse(
            test_type=request.test_type,
            total_rows=original_rows,
            filtered_rows=filtered_rows,
            metrics=metric_results,
            execution_time_ms=execution_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data/preview")
async def preview_filtered_data(request: FilteredDataRequest):
    """Preview filtered data without executing metrics."""
    try:
        # Load raw data
        df = data_service.load_test_results(request.test_type)
        if df is None:
            raise HTTPException(status_code=404, detail=f"No data found for test type: {request.test_type}")
        
        original_rows = len(df)
        
        # Apply filters
        if request.filters:
            df = data_service.apply_filters(df, request.filters)
        
        filtered_rows = len(df)
        
        # Apply limit/offset for preview
        if request.offset:
            df = df.iloc[request.offset:]
        if request.limit:
            df = df.head(request.limit)
        
        # Convert to dict for JSON response
        preview_data = df.to_dict('records')
        
        return {
            "test_type": request.test_type,
            "total_rows": original_rows,
            "filtered_rows": filtered_rows,
            "preview_rows": len(preview_data),
            "data": preview_data,
            "columns": list(df.columns)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
