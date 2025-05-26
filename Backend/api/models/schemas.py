"""
Minimal Pydantic schemas for the benchmark data API.
Only contains schemas that are actually used by routes, data_service, and dsl_executor.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union


class TestTypeInfo(BaseModel):
    """Information about a test type."""
    name: str
    displayName: str
    description: str
    available: bool
    metrics: Optional[List[str]] = None


class ResultsRequest(BaseModel):
    """Request for filtered results with metric calculation."""
    selected_models: List[str] = Field(..., description="List of model names to include")
    selected_filters: Dict[str, List[str]] = Field(default_factory=dict, description="Filter name to selected values mapping")
    parameter_values: Dict[str, Union[str, int, float, bool]] = Field(default_factory=dict, description="Parameter name to value mapping")

    class Config:
        extra = "forbid"


class ModelResult(BaseModel):
    """Result for a single model."""
    metric_value: float = Field(..., description="Calculated metric value")
    sample_count: int = Field(..., description="Number of samples used in calculation")
    
    class Config:
        extra = "forbid"


class GroupedResult(BaseModel):
    """Result for a model with group values."""
    model: str = Field(..., description="Model name")
    group_values: Dict[str, str] = Field(..., description="Group column to value mapping")
    data: ModelResult = Field(..., description="Metric result data")
    
    class Config:
        extra = "forbid"


class ResultsResponse(BaseModel):
    """Response containing results grouped by model."""
    results: List[GroupedResult] = Field(..., description="List of model results with group values")
    test_type: str = Field(..., description="Test type used")
    metric: str = Field(..., description="Metric calculated")
    group_by: Optional[List[str]] = Field(default=None, description="List of columns used for grouping")
    
    class Config:
        extra = "forbid"
