# LLM Benchmarks

A scalable benchmark suite for evaluating Large Language Models across multiple tasks with shared inference infrastructure.

## Architecture

```
Benchmarks/
├── requirements.txt          # Shared dependencies
├── Inference/               # Shared inference engine
│   ├── available_models.py  # Model definitions and registry
│   ├── config.py           # Configuration settings
│   ├── model_runner.py     # Core model execution
│   └── providers.py        # LLM provider implementations
├── Results/                 # Centralized benchmark results
│   ├── Eye_Test_model_results.csv
│   └── Coordinate_Grid_model_results.csv
└── Tests/                   # Individual benchmark implementations
    ├── TEMPLATE_README.md   # Guide for creating new benchmarks
    ├── Eye_Test/           # Vision benchmark for text recognition
    │   ├── main.py
    │   ├── test_config.py
    │   ├── dataset.json
    │   ├── responses/      # Model response files
    │   ├── assets/         # Generated test images
    │   ├── system_messages/
    │   └── utils/          # Benchmark-specific utilities
    │       ├── dataset_creator.py
    │       ├── asset_generator.py
    │       ├── model_evaluator.py
    │       └── synthesize_model_results.py
    └── Coordinate_Grid/     # Vision benchmark for spatial reasoning
        ├── main.py
        ├── test_config.py
        ├── dataset.json
        ├── responses/      # Model response files
        ├── assets/         # Generated test images
        ├── system_messages/
        └── utils/          # Benchmark-specific utilities
            ├── dataset_creator.py
            ├── asset_generator.py
            ├── model_evaluator.py
            └── synthesize_model_results.py
```

## Features

- **🔄 Shared Infrastructure**: Reusable model execution across benchmarks
- **🎯 Multiple Providers**: Support for Anthropic, OpenAI, Google, Groq
- **📊 Centralized Results**: Standardized CSV exports for analysis
- **🎛️ Flexible Configuration**: Environment-based and benchmark-specific settings
- **💬 Custom Prompts**: Benchmark-specific system messages
- **🔁 Resume Capability**: Re-run vs analyze existing results

## Quick Start

### Setup
```bash
cd Benchmarks
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
cp .env.template .env
# Edit .env with your API keys
```

### Run Benchmarks

#### Eye Test (Text Recognition)
```bash
cd Tests/Eye_Test

# Generate test dataset (optional - already included)
python main.py --generate

# Evaluate a model
python main.py --evaluate --model claude-3-5-sonnet

# Raw responses will be saved to ./responses 
# Synthesized results will be saved to ../../Results/Eye_Test_model_results.csv
```

#### Coordinate Grid (Spatial Reasoning)
```bash
cd Tests/Coordinate_Grid

# Generate test dataset (optional - already included)
python main.py --generate

# Evaluate a model
python main.py --evaluate --model gpt-4o

# Raw responses will be saved to ./responses 
# Synthesized results will be be saved to ../../Results/Coordinate_Grid_model_results.csv
```

## Supported Models

- **Anthropic**: claude-3-opus, claude-3-5-haiku, claude-3-5-sonnet, claude-3-7-sonnet, claude-4-sonnet, claude-4-opus
- **OpenAI**: gpt-4o, gpt-4.1, o4-mini, o3
- **Google**: gemini-2.5-pro, gemini-2.5-flash
- **Groq**: llama-4-maverick, llama-4-scout

## Benchmarks

### Eye Test
Vision benchmark that evaluates text recognition capabilities across different fonts. Models are shown images containing text in various typefaces (Arial, Times New Roman, Comic Sans, Courier, Verdana) and must accurately transcribe the displayed text.

### Coordinate Grid
Spatial reasoning benchmark that tests coordinate system understanding. Models analyze images containing black squares on white backgrounds and must identify the precise coordinates of each square using a bottom-left origin coordinate system.

## Benchmark Structure

Each benchmark follows a consistent 4-file utility pattern:
- `dataset_creator.py` - Generates test datasets and metadata
- `asset_generator.py` - Creates benchmark-specific test images  
- `model_evaluator.py` - Evaluates model responses against ground truth
- `synthesize_model_results.py` - Exports results to centralized CSV files

## Creating New Benchmarks

See `Tests/TEMPLATE_README.md` for a complete guide on implementing new benchmarks using the shared infrastructure.

## Results Format

All benchmarks export standardized CSV files to the `Results/` directory with benchmark-specific schemas optimized for analysis and comparison.
