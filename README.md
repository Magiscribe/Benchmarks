# LLM Benchmarks

A scalable benchmark suite for evaluating Large Language Models across multiple tasks with shared inference infrastructure.

## Architecture

```
Benchmarks/
├── .env                      # Shared environment configuration
├── requirements.txt          # Shared dependencies
├── Inference/               # Shared inference engine
│   ├── config.py           # Model definitions
│   ├── model_runner.py     # Core model execution
│   └── providers.py        # LLM provider implementations
├── Results/                 # Centralized benchmark results
│   └── {BenchmarkName}_model_results.csv
└── Tests/                   # Individual benchmark implementations
    ├── TEMPLATE_README.md   # Guide for creating new benchmarks
    └── Eye_Test/       # Vision benchmark for text recognition
        ├── main.py
        ├── test_config.py
        ├── responses/
        ├── assets/
        ├── system_messages/
        └── utils/
            ├── dataset_creator.py
            ├── image_generator.py
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

### Run LLM Eye Test
```bash
cd Tests/Eye_Test

# Generate test dataset (optional - already included)
python main.py --generate

# Evaluate a model
python main.py --evaluate --model claude-3-5-sonnet

# Results will be saved to ../../Results/Eye_Test_model_results.csv
```

## Supported Models

- **Anthropic**: claude-3-opus, claude-3-5-haiku, claude-3-7-sonnet, claude-4-sonnet, claude-4-opus
- **OpenAI**: gpt-4o, gpt-4.1, o4-mini
- **Google**: gemini-2.5-pro, gemini-2.5-flash
- **Groq**: llama-4-maverick, llama-4-scout

## Creating New Benchmarks

See `Tests/TEMPLATE_README.md` for a complete guide on implementing new benchmarks using the shared infrastructure.

## Results Format

All benchmarks export standardized CSV files to the `Results/` directory with benchmark-specific schemas optimized for analysis and comparison.
