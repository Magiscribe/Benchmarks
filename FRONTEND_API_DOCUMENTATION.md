# Frontend API Documentation
## Magiscribe Benchmarks - Dynamic Chart Interface

### Overview
This document provides complete API documentation for implementing a dynamic, interactive charting interface for LLM benchmark data analysis. The backend provides DSL-based metric calculations with advanced filtering capabilities.

---

## Base Configuration
- **Base URL**: `http://localhost:8000/api/data`
- **Content-Type**: `application/json`
- **CORS**: Enabled for all origins

---

## Core Data Flow for Charts

### 1. Initialize Chart Interface
```
GET /test-types → Get available test types
GET /filter-capabilities/{test_type} → Get filterable columns
GET /config/{test_type} → Get test configuration and available metrics
```

### 2. Build Dynamic Filters
```
POST /data/preview → Preview filtered data (for validation)
```

### 3. Execute Metrics for Charts
```
POST /data/filtered → Get filtered data with calculated metrics
```

---

## API Endpoints Reference

### Test Types Management

#### `GET /test-types`
**Purpose**: Get all available benchmark test types
**Response**:
```json
[
  {
    "name": "Eye_Test",
    "displayName": "Eye Test",
    "description": "LLM performance on character recognition at different font sizes",
    "available": true
  },
  {
    "name": "Coordinate_Grid", 
    "displayName": "Coordinate Grid",
    "description": "LLM performance on identifying coordinates in a grid",
    "available": true
  }
]
```

#### `GET /config/{test_type}`
**Purpose**: Get complete test configuration including available metrics
**Response**:
```json
{
  "testType": "Eye_Test",
  "description": "LLM performance on character recognition at different font sizes",
  "columns": [
    {
      "name": "model",
      "type": "entity",
      "description": "The LLM model being tested"
    },
    {
      "name": "font",
      "type": "categorical", 
      "description": "Font family used for the character"
    }
  ],
  "metrics": [
    {
      "name": "accuracy",
      "displayName": "Overall Accuracy",
      "description": "Percentage of correct character recognitions",
      "parameters": []
    }
  ]
}
```

### Filter System (For Multi-Select Controls)

#### `GET /filter-capabilities/{test_type}`
**Purpose**: Get comprehensive filter metadata for building UI controls
**Response**:
```json
{
  "test_type": "Eye_Test",
  "columns": [
    {
      "column": "model",
      "type": "entity",
      "displayName": "Model",
      "description": "The LLM model being tested",
      "operators": ["equals", "not_equals", "in", "not_in"],
      "values": ["claude-3-5-sonnet", "gpt-4", "gemini-pro"]
    },
    {
      "column": "font",
      "type": "categorical",
      "displayName": "Font Family",
      "description": "Font family used for the character", 
      "operators": ["equals", "not_equals", "in", "not_in"],
      "values": ["Arial", "Times New Roman", "Courier"]
    },
    {
      "column": "size",
      "type": "categorical",
      "displayName": "Font Size",
      "description": "Font size in points",
      "operators": ["equals", "not_equals", "in", "not_in"],
      "values": ["8", "10", "12", "14", "16", "18", "20"]
    }
  ]
}
```

### Data Retrieval for Charts

#### `POST /data/filtered`
**Purpose**: Get filtered data with calculated metrics for charting
**Request Body**:
```json
{
  "test_type": "Eye_Test",
  "filters": {
    "groups": [
      {
        "operator": "AND",
        "conditions": [
          {
            "column": "model",
            "operator": "in", 
            "values": ["claude-3-5-sonnet", "gpt-4"]
          },
          {
            "column": "font",
            "operator": "in",
            "values": ["Arial", "Times New Roman"]
          }
        ]
      }
    ]
  },
  "metrics": ["accuracy", "attemptRate"],
  "metric_parameters": {
    "accuracy": {"precision": 3}
  }
}
```

**Response**:
```json
{
  "test_type": "Eye_Test",
  "total_rows": 1200,
  "filtered_rows": 480,
  "execution_time_ms": 45.2,
  "metrics": {
    "accuracy": {
      "name": "accuracy",
      "displayName": "Overall Accuracy", 
      "description": "Percentage of correct character recognitions",
      "value": 0.847
    },
    "attemptRate": {
      "name": "attemptRate",
      "displayName": "Attempt Rate",
      "description": "Average number of attempts per character",
      "value": 2.3
    }
  }
}
```

#### `POST /data/preview`
**Purpose**: Preview filtered data without executing metrics (useful for data exploration)
**Request Body**: Same as `/data/filtered` but without `metrics` field
**Response**:
```json
{
  "test_type": "Eye_Test",
  "total_rows": 1200,
  "filtered_rows": 480,
  "preview_rows": 100,
  "columns": ["model", "font", "size", "character", "correct", "total"],
  "data": [
    {
      "model": "claude-3-5-sonnet",
      "font": "Arial",
      "size": "12",
      "character": "A",
      "correct": 8,
      "total": 10
    }
  ]
}
```

---

## Chart Implementation Patterns

### Pattern 1: Model Comparison Charts
**Use Case**: Compare different models on the same metrics
```javascript
// 1. Get available models from filter capabilities
const capabilities = await fetch('/filter-capabilities/Eye_Test');
const models = capabilities.columns.find(col => col.column === 'model').values;

// 2. For each selected model, get metrics
const chartData = await Promise.all(
  selectedModels.map(async model => {
    const response = await fetch('/data/filtered', {
      method: 'POST',
      body: JSON.stringify({
        test_type: 'Eye_Test',
        filters: {
          groups: [{
            operator: 'AND',
            conditions: [{ column: 'model', operator: 'equals', values: [model] }]
          }]
        },
        metrics: ['accuracy', 'attemptRate']
      })
    });
    return { model, metrics: response.metrics };
  })
);
```

### Pattern 2: Category Breakdown Charts
**Use Case**: Show metric performance across categories (fonts, sizes, etc.)
```javascript
// Get breakdown by font for selected models
const response = await fetch('/data/filtered', {
  method: 'POST', 
  body: JSON.stringify({
    test_type: 'Eye_Test',
    filters: {
      groups: [{
        operator: 'AND',
        conditions: [
          { column: 'model', operator: 'in', values: selectedModels },
          { column: 'font', operator: 'in', values: selectedFonts }
        ]
      }]
    },
    metrics: ['accuracy']
  })
});

// For category breakdown, you'll need to make separate requests per category
// or use the preview endpoint to get raw data for client-side grouping
```

### Pattern 3: Heatmap Data
**Use Case**: Character recognition accuracy heatmap (model vs character)
```javascript
// Get raw data for heatmap processing
const response = await fetch('/data/preview', {
  method: 'POST',
  body: JSON.stringify({
    test_type: 'Eye_Test',
    filters: { /* your filters */ },
    limit: 10000  // Get enough data for heatmap
  })
});

// Process client-side for heatmap:
// - Group by model and character
// - Calculate accuracy per cell
// - Format for heatmap library
```

---

## Filter Object Structure

### Complete Filter Example
```json
{
  "groups": [
    {
      "operator": "AND",  // or "OR"
      "conditions": [
        {
          "column": "model",
          "operator": "in",
          "values": ["claude-3-5-sonnet", "gpt-4"]
        },
        {
          "column": "font", 
          "operator": "not_equals",
          "values": ["Comic Sans"]
        }
      ]
    },
    {
      "operator": "OR",
      "conditions": [
        {
          "column": "size",
          "operator": "greater_than",
          "values": ["14"]
        },
        {
          "column": "character",
          "operator": "in", 
          "values": ["A", "B", "C"]
        }
      ]
    }
  ]
}
```

### Available Operators by Column Type
- **categorical/entity**: `equals`, `not_equals`, `in`, `not_in`
- **quantitative**: `equals`, `not_equals`, `greater_than`, `less_than`, `greater_than_or_equal`, `less_than_or_equal`, `between`
- **identifier**: `equals`, `not_equals`, `in`, `not_in`

---

## Test Type Specific Information

### Eye_Test
**Columns**: model, font, size, character, correct, total
**Key Metrics**: accuracy, attemptRate, fontAccuracy, sizeAccuracy
**Chart Ideas**: 
- Model comparison bar chart
- Font performance line chart
- Size vs accuracy scatter plot
- Character recognition heatmap

### Coordinate_Grid  
**Columns**: model, grid_id, square_id, error_X, error_Y
**Key Metrics**: avgDistance, avgXError, avgYError, precisionRadius
**Chart Ideas**:
- Distance error distribution histogram
- X/Y error scatter plot  
- Model accuracy comparison
- Precision vs recall analysis

---

## Performance Considerations

### Caching Strategy
- Cache filter capabilities (rarely change)
- Cache test configurations (static)
- Consider caching metric results for common filter combinations

### Request Optimization
- Use `/data/preview` for data exploration before heavy metric calculations
- Batch requests when possible
- Implement debouncing for real-time filter updates

### Data Limits
- Preview endpoint has configurable limits
- Large datasets may need pagination
- Consider client-side data processing for complex visualizations

---

## Error Handling

### Common Error Responses
```json
{
  "detail": "No data found for test type: InvalidTest"
}
```

### Status Codes
- `200`: Success
- `400`: Invalid request (bad filters, missing parameters)
- `404`: Test type not found or no data available
- `500`: Server error (DSL execution failure, file system issues)

---

