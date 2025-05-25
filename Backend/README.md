# LLM Eye Test Backend

Beautiful FastAPI backend for serving LLM eye test benchmark data to the frontend.

## Features

🚀 **FastAPI** - Modern, fast web framework  
📊 **Pandas** - Dynamic CSV data processing  
🔄 **Auto-discovery** - No hardcoded filter values  
🎯 **Accuracy calculation** - Aggregated performance metrics  
⚡ **CORS enabled** - Ready for frontend integration  

## Structure

```
Backend/
├── main.py                 # FastAPI app entry point
├── api/
│   ├── routes/
│   │   └── data.py        # Data API endpoints
│   └── models/
│       └── schemas.py     # Pydantic models
└── services/
    └── data_service.py    # CSV processing logic
```

## API Endpoints

### `GET /api/filters`
Returns dynamically discovered filter options:
```json
{
  "models": ["claude-3-5-haiku"],
  "fonts": ["Arial", "Comic Sans"],
  "sizes": [8, 9, 10, 11, 12, 14, 16, 20, 24]
}
```

### `POST /api/accuracy`
Calculate accuracy based on filters:
```json
{
  "data": [
    {
      "model": "claude-3-5-haiku",
      "accuracy": 0.6234,
      "total_correct": 234,
      "total_attempts": 375
    }
  ],
  "filters_applied": {
    "fonts": ["Arial"],
    "sizes": [14, 16, 20]
  },
  "total_models": 1
}
```

### `GET /api/stats`
Dataset overview and statistics

### `GET /api/raw?limit=10`
Raw CSV data for debugging

## Quick Start

1. **Install dependencies (from root):**
   ```bash
   cd /path/to/Benchmarks
   pip install -r requirements.txt
   ```

2. **Run the server:**
   ```bash
   cd Backend
   python main.py
   ```

3. **Test the API:**
   - Health check: http://localhost:8000/health
   - Interactive docs: http://localhost:8000/docs
   - Get filters: http://localhost:8000/api/filters

## Data Processing

- **Dynamic loading** from `../Results/LLM_Eye_Test_model_results.csv`
- **Automatic adaptation** to new models/fonts/sizes
- **Efficient grouping** and accuracy calculations
- **Flexible filtering** by any combination of criteria

The backend automatically discovers all unique values in your CSV, so adding new models or test conditions requires no code changes!
