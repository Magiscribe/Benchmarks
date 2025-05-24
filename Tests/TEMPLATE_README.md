# Creating a New Benchmark

This template shows how to create a new benchmark following the established architecture.

## Directory Structure
```
Tests/YourBenchmarkName/
├── main.py                    # Entry point with CLI interface
├── test_config.py            # Benchmark-specific configuration
├── dataset.json              # Generated dataset
├── responses/                # Model response files
├── assets/                   # Generated test data (images, etc.)
├── system_messages/          # LLM prompts
│   ├── model.txt            # Main model evaluation prompt
│   └── dataset_creator.txt  # Dataset generation prompt (if using LLM)
└── utils/                    # Utility modules
    ├── __init__.py
    ├── dataset_creator.py      # Dataset generation logic
    ├── [benchmark_specific].py  # Core benchmark logic
    ├── model_evaluator.py      # Evaluation metrics and logic
    └── synthesize_model_results.py  # Export results to centralized CSV
```

## Key Implementation Points

### 1. Import Shared Infrastructure
```python
# Add the Inference directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'Inference'))
from available_models import AVAILABLE_MODELS, MODELS
from model_runner import ModelRunner
```

### 2. Environment Loading
```python
# Load environment variables from root directory
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
env_path = os.path.join(root_dir, '.env')
load_dotenv(env_path)
```

### 3. System Messages
```python
# Pass system messages directory to ModelRunner
system_messages_dir = os.path.join(os.path.dirname(__file__), "system_messages")
runner = ModelRunner(model_name=model_id, api_key=args.api_key, system_messages_dir=system_messages_dir)
```

### 4. Centralized Results Export
```python
# Export to centralized Results folder
results_dir = os.path.join('..', '..', 'Results')
os.makedirs(results_dir, exist_ok=True)
output_file = os.path.join(results_dir, 'YourBenchmarkName_model_results.csv')
```

## Configuration Guidelines

- **Shared configs** go in `Inference/config.py` (models, providers)
- **Test-specific configs** go in `Tests/YourBenchmark/test_config.py`
- **Environment variables** go in root `.env` file
- **System prompts** go in `Tests/YourBenchmark/system_messages/`
