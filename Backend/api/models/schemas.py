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


# Enhanced Filter Models
class FilterCondition(BaseModel):
    """Represents a single filter condition."""
    column: str
    operator: str  # 'eq', 'in', 'gt', 'gte', 'lt', 'lte', 'between', 'contains', 'not_in'
    value: Union[str, int, float, List[Any], Dict[str, Any]]
    
    class Config:
        extra = "forbid"


class FilterGroup(BaseModel):
    """Represents a group of filter conditions with logical operator."""
    operator: str = "AND"  # 'AND', 'OR'
    conditions: List[FilterCondition]
    
    class Config:
        extra = "forbid"


class AdvancedFilter(BaseModel):
    """Advanced filtering with support for complex conditions."""
    groups: List[FilterGroup] = []
    
    def is_empty(self) -> bool:
        """Check if filter has any conditions."""
        return not any(group.conditions for group in self.groups)
    
    class Config:
        extra = "forbid"


class FilterMetadata(BaseModel):
    """Metadata about filterable columns for a test type."""
    column: str
    type: str  # 'entity', 'categorical', 'identifier', 'quantitative'
    displayName: str
    description: str
    operators: List[str]  # Available operators for this column type
    values: Optional[List[Any]] = None  # Available values for categorical/entity columns
    range: Optional[Dict[str, float]] = None  # Min/max for quantitative columns
    
    class Config:
        extra = "forbid"


class FilterCapabilities(BaseModel):
    """Complete filter capabilities for a test type."""
    test_type: str
    columns: List[FilterMetadata]
    
    class Config:
        extra = "forbid"


class FilteredDataRequest(BaseModel):
    """Request for data with advanced filtering."""
    test_type: str
    filters: Optional[AdvancedFilter] = None
    group_by: Optional[List[str]] = None  # Columns to group by
    metrics: Optional[List[str]] = None  # Metrics to calculate
    metric_parameters: Optional[Dict[str, Dict[str, Any]]] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    
    class Config:
        extra = "forbid"


# Results Request/Response Models
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


class ResultsResponse(BaseModel):
    """Response containing results grouped by model."""
    results: Dict[str, ModelResult] = Field(..., description="Model name to result mapping")
    test_type: str = Field(..., description="Test type used")
    metric: str = Field(..., description="Metric calculated")
    
    class Config:
        extra = "forbid"
