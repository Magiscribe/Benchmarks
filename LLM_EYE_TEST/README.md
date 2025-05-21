# AI Spy Vision Benchmark

A benchmark for testing vision models' ability to read text like humans do on an eye chart.

## Overview

AI Spy generates eye chart-style images with standardized font sizes and evaluates how well vision models can read the text, especially as it gets smaller. This benchmark provides a quantitative way to assess the "visual acuity" of AI vision systems across multiple models.

## Features

- Eye chart image generation with:
  - Multiple fonts (Arial, Times New Roman, Comic Sans, etc.)
  - Standardized font sizes (72, 36, 18, 12, 9 pt)
  - Random letters (uppercase and lowercase)
- Dataset creation with ground truth
- Evaluation metrics:
  - Character-level accuracy
  - Row-level accuracy
  - Performance by font and font size
  - Detailed reporting
- Built-in support for evaluating Anthropic Claude models:
  - Claude 3 family (Opus, Sonnet, Haiku)
  - Claude 3.5 family (Sonnet, Sonnet V2, Haiku)
  - Claude 3.7 family (Sonnet)
- Model comparison tools for benchmarking

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-spy.git
cd ai-spy

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt 
```

## Configuration

You can modify the standard font sizes and other parameters in `config.py`:

- `STANDARD_FONT_SIZES`: The standard font sizes for all eye charts (default: [72, 36, 18, 12, 9])
- `CHARS_PER_ROW`: Number of characters per row (default: 12)
- `VERTICAL_SPACING`: Vertical spacing factor (default: 2.0)
- `IMAGE_WIDTH` and `IMAGE_HEIGHT`: Image dimensions (default: 1000×1200)
- `FONTS`: Dictionary of supported fonts and their file paths
- `ALPHABET`: Characters to use (uppercase and lowercase letters)

## Usage

### Generate Test Images and Dataset

```bash
python main.py --generate --images-per-font 3
```

### Run Evaluation with Mock Model

```bash
python main.py --evaluate --model mock
```

### Run Evaluation with Claude Models

To evaluate Claude models, you'll need an Anthropic API key:

```bash
# Set API key as environment variable
export ANTHROPIC_API_KEY=your_api_key

# Evaluate Claude 3 models
python main.py --evaluate --model claude-3-opus
python main.py --evaluate --model claude-3-sonnet
python main.py --evaluate --model claude-3-haiku

# Evaluate Claude 3.5 models
python main.py --evaluate --model claude-3-5-sonnet
python main.py --evaluate --model claude-3-5-sonnet-v2
python main.py --evaluate --model claude-3-5-haiku

# Evaluate Claude 3.7 models
python main.py --evaluate --model claude-3-7-sonnet
```

Or provide the API key directly:

```bash
python main.py --evaluate --model claude-3-sonnet --api-key your_api_key
```

### Compare Models

After evaluating multiple models, you can compare their results:

```bash
python main.py --compare claude-3-sonnet_results.json claude-3-haiku_results.json mock_results.json
```

### Full Pipeline Example

```bash
# Generate dataset
python main.py --generate --images-per-font 1

# Evaluate different models
python main.py --evaluate --model claude-3-sonnet 
python main.py --evaluate --model claude-3-5-sonnet-v2
python main.py --evaluate --model claude-3-7-sonnet

# Compare the models
python main.py --compare data/claude-3-sonnet_results.json data/claude-3-5-sonnet-v2_results.json data/claude-3-7-sonnet_results.json
```

### Running All Models Automatically

Use the `run_all_models.py` script to run multiple models in sequence and automatically generate a comparison:

```bash
# Run all supported models with existing dataset
python run_all_models.py

# Generate a new dataset and run all models
python run_all_models.py --generate --images-per-font 1

# Run specific models only
python run_all_models.py --models claude-3-7-sonnet claude-3-5-sonnet-v2 claude-3-haiku

# Skip models that already have results
python run_all_models.py --skip-existing

# Generate visualizations after running models
python run_all_models.py --models claude-3-haiku claude-3-sonnet --visualize
```

The script saves model responses and results in separate directories:
- Model responses are saved to `data/responses/{model_name}_responses.json`
- Evaluation results are saved to `data/results/{model_name}_results.json`

### Generating Visualizations

The easiest way to generate visualizations is using the visualizations.py script, which automatically processes all results:

```bash
# Windows: Double-click run_visualizer.bat
# OR use the command line:

# Process all results in data/results directory (recommended)
python visualizations.py --data-dir data

# Customize parameters
python visualizations.py --data-dir data --dpi 600 --figsize 16,10 --title "My Benchmark Results"

# Alternative: Specify results directory explicitly
python visualizations.py --results-dir data/results --output-dir visualizations

# Alternative: Specify individual result files
python visualizations.py --results data/results/claude-3-haiku_results.json data/results/claude-3-sonnet_results.json
```

The script generates two visualization types:
1. **Font Accuracy Chart**: Bar chart comparing model accuracy across different fonts
2. **Font Size Accuracy Chart**: Scatter plot showing accuracy vs font size for each model

All visualizations are saved in the specified output directory with timestamps in the filenames.

### Command-line Options

#### Dataset Generation
- `--generate`: Generate new test images and dataset
- `--fonts N`: Number of fonts to use (default: all)
- `--images-per-font N`: Number of images per font (default: 1)
- `--output-dir DIR`: Directory for test images (default: test_images)
- `--dataset FILE`: Path to dataset file (default: dataset.json)

#### Model Evaluation
- `--evaluate`: Run evaluation
- `--model NAME`: Model to evaluate (choices: mock, claude-3-opus, claude-3-sonnet, claude-3-haiku, claude-3-5-sonnet, claude-3-5-sonnet-v2, claude-3-5-haiku, claude-3-7-sonnet; default: mock)
- `--model-responses FILE`: Path to saved model responses JSON (default: None = run the model)
- `--api-key KEY`: API key for real models (default: uses ANTHROPIC_API_KEY environment variable)
- `--responses FILE`: Path to save model responses (default: data/responses/model_name_responses.json)
- `--results FILE`: Path to save evaluation results (default: data/results/model_name_results.json)

#### Model Comparison
- `--compare FILES`: Compare multiple models by specifying their result files

#### Run All Models Script
- `--models LIST`: Specific models to run (default: all models)
- `--generate`: Generate a new dataset before running models
- `--images-per-font N`: Number of images per font when generating dataset (default: 1)
- `--dataset FILE`: Path to dataset file (default: dataset.json)
- `--output-dir DIR`: Directory to save results (default: data)
- `--skip-existing`: Skip models that already have result files
- `--api-key KEY`: API key for Claude models (default: uses ANTHROPIC_API_KEY environment variable)
- `--delay N`: Delay between model runs in seconds (default: 5)
- `--visualize`: Generate visualizations after running models
- `--vis-dpi N`: DPI for visualizations (default: 300)

#### Visualization Generator (visualizations.py)
- `--data-dir DIR`: Path to data directory containing 'results' and 'visualizations' folders
- `--results FILES`: Paths to specific result JSON files
- `--results-dir DIR`: Directory containing result JSON files
- `--output-dir DIR`: Directory to save visualizations (default: visualizations or data-dir/visualizations)
- `--dpi N`: DPI for saved figures (default: 300)
- `--figsize WxH`: Figure size in inches as width,height (default: 12,8)
- `--title TEXT`: Main title for visualizations
- `--min-models N`: Minimum number of model results required (default: 2)


## Using with Custom Models

To use this benchmark with your own vision models:

1. Generate a dataset using the `--generate` option
2. Implement a function that processes each image with your model
3. Format the responses as a list of lists of dicts with `{row: int, text: string}` format
4. Save the responses to a JSON file
5. Use `--evaluate --model-responses your_responses.json` to evaluate your model

Example code for using with a custom model:

```python
import json
from your_vision_api import YourModelAPI

# Load the dataset
with open("dataset.json", 'r') as f:
    dataset = json.load(f)

# Initialize your model
model = YourModelAPI()

# Process each image
all_responses = []
for item in dataset:
    image_path = item["image_path"]
    
    # Call your model API
    response = model.process_image(image_path)
    
    # Format response as list of {row: int, text: str} dicts
    formatted_response = [
        {"row": i, "text": text} 
        for i, text in enumerate(response)
    ]
    
    all_responses.append(formatted_response)

# Save responses
with open("your_model_responses.json", 'w') as f:
    json.dump(all_responses, f, indent=2)

# Evaluate using AI Spy
# python main.py --evaluate --model-responses your_model_responses.json
```

## Directory Structure

- `data/`: Contains all benchmark output
  - `responses/`: Raw model responses to images
  - `results/`: Processed evaluation results
  - `visualizations/`: Generated charts and visualizations
- `test_images/`: Generated test images organized by font

## Component Files

- `config.py`: Configuration settings for font sizes, image dimensions, etc.
- `image_generator.py`: Creates eye chart test images
- `dataset_creator.py`: Generates the benchmark dataset with ground truth
- `evaluator.py`: Evaluates model responses against ground truth
- `model_runner.py`: Handles API calls to Claude models
- `main.py`: Orchestrates the workflow
- `run_all_models.py`: Script to run and compare multiple models
- `visualizations.py`: Generates visual comparisons of model performance
- `run_visualizer.bat`: Windows batch file to quickly generate visualizations

## License

MIT License