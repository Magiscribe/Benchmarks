"""
Pydantic models for API request/response schemas.
"""

from pydantic import BaseModel
from typing import List, Optional

class FilterOptions(BaseModel):
    """Available filter options from the dataset."""
    models: List[str]
    fonts: List[str]
    sizes: List[int]

class AccuracyRequest(BaseModel):
    """Request model for accuracy calculation with filters."""
    fonts: Optional[List[str]] = None
    sizes: Optional[List[int]] = None
    models: Optional[List[str]] = None

class AccuracyData(BaseModel):
    """Response model for accuracy data per model."""
    model: str
    accuracy: float
    total_correct: int
    total_attempts: int

class AccuracyResponse(BaseModel):
    """Response wrapper for accuracy data."""
    data: List[AccuracyData]
    filters_applied: AccuracyRequest
    total_models: int
