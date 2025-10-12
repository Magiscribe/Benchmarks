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

#### AITA Conversation (Persuasion & Social Reasoning)
```bash
cd Tests/AITA_Conversation

# Run a 3-model debate on a scenario
python main.py --run-conversation --scenario-id aita_001 --models gpt-5 gpt-5-mini gpt-5-nano

# Run all scenarios with same models
python main.py --run-all --models claude-4-sonnet gpt-4o gemini-2.5-pro

# Evaluate all conversations and generate results CSV
python main.py --evaluate
```

## Supported Models

### Latest Models (Updated October 2025)

- **Anthropic**: 
  - **NEW**: claude-4.5-sonnet (best for complex agents/coding), claude-4.1-opus (advanced reasoning)
  - Legacy: claude-3-opus, claude-3-5-haiku, claude-3-5-sonnet, claude-3-7-sonnet, claude-4-sonnet, claude-4-opus

- **OpenAI**: 
  - **NEW**: gpt-5 (flagship $1.25/$10), gpt-5-mini (fast $0.25/$2), gpt-5-nano (fastest $0.05/$0.40), gpt-5-thinking-mini, gpt-4o-mini
  - Existing: gpt-4o, o4-mini

- **Google**: 
  - **NEW**: gemini-2.5-flash-lite (ultra fast), gemini-2.0-flash, gemini-2.0-flash-lite
  - Existing: gemini-2.5-pro, gemini-2.5-flash

- **Groq**: llama-4-maverick, llama-4-scout

- **xAI Grok**:
  - **NEW**: grok-4 (flagship $3/$15), grok-4-fast-reasoning ($0.20/$0.50), grok-4-fast-non-reasoning ($0.20/$0.50)
  - **NEW**: grok-3 ($3/$15), grok-3-mini ($0.30/$0.50), grok-code-fast-1 ($0.20/$1.50)
  - **Note**: Vision support only available on grok-4 family models

*Pricing format: input/output per 1M tokens*

## Benchmarks

### Eye Test
Tests vision models' ability to read progressively smaller text across five fonts, from 24pt down to 8pt font. Models are shown synthetic eye charts containing random uppercase and lowercase letters in Arial, Times New Roman, Comic Sans, Courier, and Verdana fonts.

### Coordinate Grid
Evaluates spatial reasoning by challenging models to return the coordinates of 5x5 black pixel squares on a 512x512 white grid. Models must identify exact center coordinates of randomly placed black squares on white 512x512 pixel backgrounds, testing both visual perception and mathematical coordinate understanding.

### AITA Conversation
Tests persuasion and argumentation through competitive multi-agent debates on r/AmITheAsshole scenarios. Three models are each randomly assigned a position (YTA/NTA) and must persuade the others to switch to the **opposite** position. Win condition: be the **only** model with your final position after up to 15 turns of debate. Measures strategic reasoning, rhetorical skill, and ability to detect/resist persuasion tactics.

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
