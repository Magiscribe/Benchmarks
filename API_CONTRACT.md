# Magiscribe Benchmarks API Contract

## Overview
This API contract documents the REST API endpoints for the Magiscribe Benchmarks system. The backend is built with FastAPI and provides endpoints for test configuration, model data, and metric calculations using a Domain Specific Language (DSL) for dynamic metric execution.

**Base URL**: `http://localhost:8000/data`  
**Content-Type**: `application/json`  
**CORS**: Enabled for all origins

---

## API Endpoints

### 1. Get Available Test Types
**Endpoint**: `GET /available-tests`  
**Description**: Retrieves all available test types with their configurations.

**Response**:
```json
[
  {
    "name": "Eye_Test",
    "displayName": "Eye_Test",
    "description": "LLM performance on character recognition at different font sizes",
    "available": true,
    "metrics": null
  },
  {
    "name": "Coordinate_Grid", 
    "displayName": "Coordinate_Grid",
    "description": "LLM performance on identifying coordinates in a grid",
    "available": true,
    "metrics": null
  }
]
```

**Response Schema**:
```typescript
interface TestTypeInfo {
  name: string;
  displayName: string;
  description: string;
  available: boolean;
  metrics?: string[] | null;
}
```

---

### 2. Get Available Models
**Endpoint**: `GET /available-models/{test_type}`  
**Description**: Retrieves all available models for a specific test type from the results CSV.

**Path Parameters**:
- `test_type` (string): The test type name (e.g., "Eye_Test", "Coordinate_Grid")

**Response**:
```json
[
  "claude-3-5-haiku",
  "claude-3-5-sonnet", 
  "gpt-4o",
  "gemini-2.5-pro"
]
```

**Response Schema**: `string[]`

---

### 3. Get Available Filters
**Endpoint**: `GET /available-filters/{test_type}`  
**Description**: Retrieves all available filters (identifier and categorical columns) for a specific test type.

**Path Parameters**:
- `test_type` (string): The test type name

**Response**:
```json
[
  {
    "name": "font",
    "type": "categorical",
    "description": "Font family used for the character"
  },
  {
    "name": "size", 
    "type": "categorical",
    "description": "Font size in points"
  },
  {
    "name": "character",
    "type": "categorical", 
    "description": "The character being recognized"
  }
]
```

**Response Schema**:
```typescript
interface FilterColumn {
  name: string;
  type: 'identifier' | 'categorical';
  description: string;
}
```

---

### 4. Get Available Filter Values
**Endpoint**: `GET /available-filter-values/{test_type}/{filter_name}`  
**Description**: Retrieves all unique values for a specific filter in a test type.

**Path Parameters**:
- `test_type` (string): The test type name
- `filter_name` (string): The filter column name

**Response**:
```json
[
  "Arial",
  "Comic Sans MS", 
  "Courier New",
  "Times New Roman",
  "Verdana"
]
```

**Response Schema**: `string[]`

---

### 5. Get Available Metrics
**Endpoint**: `GET /available-metrics/{test_type}`  
**Description**: Retrieves all available metrics for a specific test type from the DSL configuration.

**Path Parameters**:
- `test_type` (string): The test type name

**Response**:
```json
[
  {
    "name": "accuracy",
    "displayName": "Overall Accuracy",
    "description": "Percentage of correct character recognitions"
  },
  {
    "name": "attemptRate",
    "displayName": "Attempt Rate", 
    "description": "Average number of attempts per character"
  },
  {
    "name": "successRate",
    "displayName": "Success Rate Above Threshold",
    "description": "Percentage of characters recognized correctly above specified threshold"
  }
]
```

**Response Schema**:
```typescript
interface Metric {
  name: string;
  displayName: string;
  description: string;
}
```

---

### 6. Get Available Parameters
**Endpoint**: `GET /available-parameters/{test_type}/{metric_name}`  
**Description**: Retrieves all available parameters for a specific metric in a test type.

**Path Parameters**:
- `test_type` (string): The test type name
- `metric_name` (string): The metric name

**Response**:
```json
[
  {
    "name": "threshold",
    "type": "number",
    "default": 0.5,
    "description": "Accuracy threshold (0.0-1.0) above which characters are considered successful"
  }
]
```

**Response Schema**:
```typescript
interface MetricParameter {
  name: string;
  type: string;
  default: any;
  description: string;
}
```

---

### 7. Get Results (Basic)
**Endpoint**: `POST /results/{test_type}/{metric}?group_by=categorical_factor`  
**Description**: Retrieves filtered results grouped by model with metric calculation.

**Path Parameters**:
- `test_type` (string): The test type name
- `metric` (string): The metric name to calculate

**Query Parameters**
- `group_by` (string) Categorical variable to group by

**Request Body**:
```json
{
  "selected_models": [
    "claude-3-5-haiku",
    "gpt-4o"
  ],
  "selected_filters": {
    "font": ["Arial", "Times New Roman"],
    "size": ["12", "14", "16"]
  },
  "parameter_values": {
    "threshold": 0.7
  }
}
```

**Request Schema**:
```typescript
interface ResultsRequest {
  selected_models: string[];
  selected_filters?: Record<string, string[]>;
  parameter_values?: Record<string, any>;
}
```

**Response**:
```json
{
  "results": [
    {
      "model": "claude-3-5-haiku",
      "group_values": {},
      "data": {
        "metric_value": 0.7823,
        "sample_count": 1247
      }
    },
    {
      "model": "gpt-4o",
      "group_values": {},
      "data": {
        "metric_value": 0.8156,
        "sample_count": 1247
      }
    }
  ],
  "test_type": "Eye_Test",
  "metric": "accuracy",
  "group_by": null
}
```

**Response Schema**:
```typescript
interface ModelResult {
  metric_value: number;
  sample_count: number;
}

interface GroupedResult {
  model: string;
  group_values: Record<string, string>;
  data: ModelResult;
}

interface ResultsResponse {
  results: GroupedResult[];
  test_type: string;
  metric: string;
  group_by?: string[] | null;
}
```

---

## Data Models

### Test Type Structure
Each test type has a `csv_format.json` configuration file that defines:
- **testType**: Display name for the test
- **description**: Human-readable description
- **columns**: Column definitions with types (entity, categorical, identifier, quantitative)
- **metrics**: DSL-based metric definitions with calculation steps

### Column Types
- **entity**: Primary grouping column (e.g., model names)
- **categorical**: Discrete values for filtering/grouping (e.g., font, size)
- **identifier**: Unique identifiers (e.g., grid_id, square_id)  
- **quantitative**: Numeric values for calculations (e.g., correct, total, error_X, error_Y)

### Available Test Types

#### Eye_Test
- **Purpose**: Text recognition benchmark across different fonts
- **Data Structure**: 
  - `model`: LLM model name
  - `font`: Font family (Arial, Times New Roman, Comic Sans MS, Courier New, Verdana)
  - `size`: Font size in points (8, 10, 12, 14, 16, 18, 20, 24, 28, 32, 36, 48)
  - `character`: Character being recognized (A-Z, a-z, 0-9)
  - `correct`: Number of correct recognitions
  - `total`: Total number of attempts
- **Key Metrics**: accuracy, attemptRate, perfectCharacters, failureRate, successRate

#### Coordinate_Grid
- **Purpose**: Spatial reasoning benchmark for coordinate identification
- **Data Structure**:
  - `model`: LLM model name
  - `grid_id`: Unique grid identifier
  - `square_id`: Position within grid
  - `error_X`: Horizontal error in pixels
  - `error_Y`: Vertical error in pixels
- **Key Metrics**: avgDistance, avgXError, avgYError, maxDistance, accuracyWithinThreshold, stdDevDistance

---

## Frontend Integration

### Hook Usage Patterns

The frontend uses React hooks to manage API interactions:

1. **useDashboardData**: Fetches test types and manages selection
2. **useModels**: Manages available models for selected test type
3. **useMetrics**: Handles metric selection and parameter configuration
4. **useFilters**: Manages filter options and selections
5. **useGroupBy**: Handles grouping column selection
6. **useResults**: Orchestrates multi-metric result fetching

### Typical Data Flow

1. **Initialize**: Load test types via `/available-tests`
2. **Configure**: 
   - Select test type
   - Fetch models via `/available-models/{test_type}`
   - Fetch metrics via `/available-metrics/{test_type}`
   - Fetch filters via `/available-filters/{test_type}`
   - Fetch filter values via `/available-filter-values/{test_type}/{filter_name}`
3. **Execute**: Submit requests to `/results/{test_type}/{metric}` for each selected metric
4. **Display**: Render results in tables and charts

### Multi-Metric Support

The frontend handles multiple metrics by:
- Making parallel requests for each selected metric
- Combining results into a `MultiMetricResults` object
- Displaying unified tables with all metric columns

---

## Error Handling

### HTTP Status Codes
- **200**: Success
- **500**: Internal server error with error message in response body

### Error Response Format
```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Scenarios
- Missing CSV results file for test type
- Invalid test type name
- Metric calculation errors
- DSL execution failures
- Missing configuration files

---

## Performance Considerations

### Caching Strategy
- Test type configurations are loaded once per test type
- Filter values are cached per test type
- CSV data is loaded on-demand for each request

### Optimization Opportunities
- Implement response caching for frequently accessed data
- Add pagination for large result sets
- Consider database storage for better query performance

---

## Authentication & Security

Currently, the API:
- Uses CORS with wildcard origin (`*`) - should be configured for production
- No authentication required
- No rate limiting implemented

For production deployment, consider:
- JWT or OAuth2 authentication
- Rate limiting per client
- CORS configuration for specific domains
- Input validation and sanitization

---

This API contract provides a complete interface for the Magiscribe Benchmarks system, supporting dynamic test type discovery, flexible filtering, and DSL-based metric calculations with comprehensive frontend integration.
