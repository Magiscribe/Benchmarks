"""
Pydantic schemas for the benchmark data API.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union


# DSL Operation Models
class DSLOperation(BaseModel):
    """Represents a single DSL operation."""
    op: str
    col: Optional[str] = None
    cols: Optional[List[str]] = None
    as_: Optional[str] = Field(None, alias="as")
    condition: Optional[str] = None
    exp: Optional[Union[int, float]] = None
    value: Optional[str] = None

    class Config:
        populate_by_name = True


class DSLMetric(BaseModel):
    """Represents a metric definition."""
    name: str
    displayName: str
    description: str
    steps: List[DSLOperation]
    parameters: Optional[List[Dict[str, Any]]] = None


class DSLFormat(BaseModel):
    """Represents the complete csv_format.json structure."""
    testType: str
    description: str
    columns: List[Dict[str, Any]]
    metrics: List[DSLMetric]


# Request/Response Models
class DSLRequest(BaseModel):
    """Request to execute DSL operations."""
    test_type: str
    metric_name: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None


class DSLExecutionRequest(BaseModel):
    """Request to execute specific DSL metrics."""
    test_type: str
    metrics: Optional[List[str]] = None  # If None, execute all metrics
    metric_parameters: Optional[Dict[str, Dict[str, Any]]] = None
    data_filters: Optional[Dict[str, Any]] = None


class MetricExecutionResult(BaseModel):
    """Result of executing a single metric."""
    name: str
    displayName: str
    description: str
    value: Optional[Any] = None
    error: Optional[str] = None


class DSLExecutionResponse(BaseModel):
    """Response from DSL execution."""
    test_type: str
    total_rows: int
    filtered_rows: int
    metrics: Dict[str, MetricExecutionResult]
    execution_time_ms: Optional[float] = None


# Data Models
class DataPoint(BaseModel):
    """Represents a single data point."""
    id: str
    values: Dict[str, Any]


class MetricResult(BaseModel):
    """Represents calculated metrics for a model."""
    accuracy: float
    totalTests: int
    additionalMetrics: Dict[str, Any] = {}


class ModelResult(BaseModel):
    """Represents results for a single model."""
    model: str
    accuracy: float
    totalTests: int
    dataPoints: List[DataPoint]
    metrics: Optional[Dict[str, Any]] = {}


class TestResult(BaseModel):
    """Represents a single test result."""
    id: str
    model: str
    accuracy: float
    metadata: Dict[str, Any]
    metrics: Optional[Dict[str, Any]] = {}


class ModelComparison(BaseModel):
    """Represents a comparison between models."""
    models: List[str]
    metrics: Dict[str, MetricResult]
    summary: str


class TestTypeInfo(BaseModel):
    """Information about a test type."""
    name: str
    displayName: str
    description: str
    available: bool
    metrics: Optional[List[str]] = None


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    details: Optional[str] = None


# Filter Models
class FilterOptions(BaseModel):
    """Available filter options for a test type."""
    models: List[str] = []
    fonts: Optional[List[str]] = None
    sizes: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    difficulties: Optional[List[str]] = None
    # Add more filter fields as needed for different test types


class TestDataRequest(BaseModel):
    """Request for test data with optional filters."""
    test_type: str
    models: Optional[List[str]] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    filters: Optional[Dict[str, Any]] = None


# Pagination Models
class PaginatedResponse(BaseModel):
    """Base paginated response."""
    total: int
    page: int
    per_page: int
    pages: int


class PaginatedModelResults(PaginatedResponse):
    """Paginated model results."""
    data: List[ModelResult]


class PaginatedTestResults(PaginatedResponse):
    """Paginated test results."""
    data: List[TestResult]


# Legacy schemas for backward compatibility (will be deprecated)
class AccuracyRequest(BaseModel):
    """Legacy: Request for accuracy calculation."""
    fonts: Optional[List[str]] = None
    sizes: Optional[List[str]] = None
    models: Optional[List[str]] = None


class AccuracyData(BaseModel):
    """Legacy: Accuracy data for a model."""
    model: str
    accuracy: float
    total_correct: int
    total_attempts: int
