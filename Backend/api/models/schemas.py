"""
Minimal Pydantic schemas for the benchmark data API.
Only contains schemas that are actually used by routes, data_service, and dsl_executor.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union


class ResultsRequest(BaseModel):
    """Request for filtered results with metric calculation - API CONTRACT FORMAT."""
    models: List[str] = Field(..., description="List of model names to include")
    filters: Dict[str, List[str]] = Field(default_factory=dict, description="Filter name to selected values mapping")

    class Config:
        extra = "forbid"


class ResultItem(BaseModel):
    """Single result item in API contract format."""
    model: str = Field(..., description="Model name")
    groupings: List[str] = Field(..., description="Group values in order")
    value: float = Field(..., description="Calculated metric value")

    class Config:
        extra = "forbid"


class ResultsResponse(BaseModel):
    """Response containing results in API contract format."""
    results: List[ResultItem] = Field(..., description="List of results")
    metric: str = Field(..., description="Metric calculated")
    
    class Config:
        extra = "forbid"
