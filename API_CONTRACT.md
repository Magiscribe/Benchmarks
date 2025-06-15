# Magiscribe Benchmarks API Contract

## API Endpoints

### 1. Get Available Benchmarks
**Endpoint**: `GET /benchmarks`  
**Description**: Retrieves all available benchmarks and descriptions.

**Response**:
```json
[
  {
    "id": "Eye_Test",
    "name": "Eye Test",
    "description": "LLM performance on character recognition at different font sizes",
  },
  {
    "id": "Coordinate_Grid", 
    "name": "Coordinate Grid",
    "description": "LLM performance on identifying coordinates in a grid",
  }
]
```
---
### 2. Get Available Models
**Endpoint**: `GET /benchmarks/{benchmark_id}/models`  
**Description**: Retrieves all available models for a specific benchmark from the results CSV.

**Path Parameters**:
- `benchmark_id` (string): The benchmark id (e.g., "Eye_Test", "Coordinate_Grid")

**Response**:
```json
[
  "claude-3-5-haiku",
  "claude-3-5-sonnet", 
  "gpt-4o",
  "gemini-2.5-pro"
]
```
---
### 3. Get Available Filters
**Endpoint**: `GET /benchmarks/{benchmark_id}/filters`  
**Description**: Retrieves key-value pairs for everything we could filter/group by for a specific benchmark.

**Path Parameters**:
- `benchmark_id` (string): The benchmark name

**Response**:
```json
{
  "font": ["Arial", "Comic Sans MS", "Courier New", "Times New Roman", "Verdana"],
  "size": ["8", "10", "12", "14", "16", "18", "20", "24", "28", "32", "36", "48"],
  "character": ["A", "B", "C", "a", "b", "c", "0", "1", "2"]
}
```
---
### 4. Get Available Metrics
**Endpoint**: `GET /benchmarks/{benchmark_id}/metrics`  
**Description**: Retrieves all available metrics for a specific benchmark from the DSL configuration.

**Path Parameters**:
- `benchmark_id` (string): The benchmark name

**Response**:
```json
[
  {
    "id": "accuracy",
    "name": "Overall Accuracy",
    "description": "Percentage of correct character recognitions"
  },
  {
    "id": "attemptRate",
    "name": "Attempt Rate", 
    "description": "Average number of attempts per character"
  }
]
```
---
### 5. Get Available Assets
**Endpoint**: `GET /benchmarks/{benchmark_id}/assets`  
**Description**: Retrieves all available asset IDs for a specific benchmark by scanning the assets directory.

**Path Parameters**:
- `benchmark_id` (string): The benchmark id (e.g., "Eye_Test", "Coordinate_Grid") without the .png file extension

**Response**:
```json
[
  "1001",
  "1002", 
  "1003",
  "1004",
  "1005"
]
```
---
### 6. Get Results
**Endpoint**: `POST /benchmarks/{benchmark_id}/metrics/{metric_id}`  
**Description**: Retrieves filtered results grouped by model with metric calculation.

**Path Parameters**:
- `benchmark_id` (string): The benchmark name
- `metric_id` (string): The metric name to calculate

**Query Parameters**
- `group_by` (string, optional): Categorical variable to group by

**Request Body**:
```json
{
  "models": [
    "claude-3-5-haiku",
    "gpt-4o"
  ],
  "filters": {
    "font": ["Arial", "Times New Roman"],
    "size": ["12", "14", "16"]
  }
}
```

**Response**:
```json
{
  "results": [
    {
      "model": "claude-3-5-haiku",
      "groupings": ["Arial"],
      "value": 0.7823,
    },
    {
      "model": "claude-3-5-haiku",
      "groupings": ["Times New Roman"],
      "value": 0.5423,
    },
    {
      "model": "gpt-4o",
      "groupings": ["Arial"],
      "value": 0.831,
    },
    {
      "model": "gpt-4o",
      "groupings": ["Times New Roman"],
      "value": 0.423,
    },
  ],
  "metric": "accuracy"
}
```
---
## Typical Data Flow

1. **Initialize**: Load benchmarks via `/benchmarks`
2. **Configure**: 
   - Select benchmark
   - Fetch models via `/benchmarks/{benchmark_id}/models` 
   - Fetch metrics via `/benchmarks/{benchmark_id}/metrics`
   - Fetch filters via `/benchmarks/{benchmark_id}/filters`
   - Fetch assets via `/benchmarks/{benchmark_id}/assets`
3. **Execute**: Submit requests to `/benchmarks/{benchmark_id}/metrics/{metric_id}` for each selected metric
4. **Display**: Render results in tables and charts


## API Endpoints Summary

### Core Data Endpoints
- `GET /benchmarks` - Get all available benchmarks
- `GET /benchmarks/{benchmark_id}/models` - Get available models for a given benchmark
- `GET /benchmarks/{benchmark_id}/filters` - Key value pairs for everything we could filter/group by
- `GET /benchmarks/{benchmark_id}/metrics` - Get available metrics for a given benchmark
- `GET /benchmarks/{benchmark_id}/assets` - Get available asset IDs for a given benchmark

### Results Endpoints
- `POST /benchmarks/{benchmark_id}/metrics/{metric_id}?group_by={categorical_variable}` - Get metric results with filtering and grouping (group_by is optional)
---