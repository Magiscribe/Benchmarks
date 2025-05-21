# LLM Eye Test

A benchmark for testing vision models' ability to read text at different sizes, mimicking a human eye test.

## Overview

LLM Eye Test generates eye chart images with standard font sizes and evaluates how well vision models can read text as it gets smaller. Currently supports evaluation of Anthropic Claude and OpenAI GPT models.

## Setup

```bash
# Clone repository
git clone https://github.com/yourusername/LLM_EYE_TEST.git
cd LLM_EYE_TEST

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.template .env
# Edit .env and add your API keys
```

## Usage

### Generate Test Images

```bash
python main.py --generate --images-per-font 3
```

### Evaluate a Model

```bash
# Run evaluation with Anthropic Claude (uses API key from .env file)
python main.py --evaluate --model claude-3-7-sonnet

# Run evaluation with OpenAI GPT (uses API key from .env file)
python main.py --evaluate --model gpt-4o-vision
```

### Generate CSV Results

```bash
python generate_model_results.py
```

## Supported Models

### Anthropic
- Claude 3: Opus, Sonnet, Haiku
- Claude 3.5: Sonnet, Sonnet V2, Haiku
- Claude 3.7: Sonnet

### OpenAI
- GPT-4 Vision Preview
- GPT-4o Vision
- GPT-4o Mini Vision
- GPT-4 Turbo

## Project Structure

- `main.py` - Main script for dataset generation and model evaluation
- `config.py` - Configuration settings
- `image_generator.py` - Creates eye chart test images
- `dataset_creator.py` - Generates benchmark dataset
- `model_runner.py` - Handles API calls to models
- `evaluator.py` - Evaluates model responses
- `generate_model_results.py` - Creates consolidated CSV of results
- `.env.template` - Template for environment variables
- `.env` - Local environment configuration (not committed to git)
- `data/` - Contains model responses
- `test_images/` - Generated test images organized by font

## License

MIT License