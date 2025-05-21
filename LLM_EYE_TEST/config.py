# Standard configuration settings for LLM_EYE_TEST

# Standard font sizes for all eye charts
STANDARD_FONT_SIZES = [24, 20, 16, 14, 12, 11, 10, 9, 8] 

# Number of characters per row
CHARS_PER_ROW = 32

# Vertical spacing factor (multiplied by font size to determine spacing)
VERTICAL_SPACING = 3

# Image dimensions
IMAGE_WIDTH = 512
IMAGE_HEIGHT = 512

# Supported fonts
FONTS = {
    "Arial": "arial.ttf",
    "Times New Roman": "times.ttf",
    "Comic Sans": "comic.ttf",
    "Courier": "cour.ttf",
    "Verdana": "verdana.ttf"
}

# Characters to use (uppercase and lowercase letters)
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

# Model definitions
# Format: {"display_name": "api_endpoint_name"}
MODELS = {
    # Anthropic Claude models
    "claude-3-opus": "claude-3-opus-20240229",
    "claude-3-sonnet": "claude-3-sonnet-20240229",
    "claude-3-haiku": "claude-3-haiku-20240307",
    
    # Claude 3.5 family
    "claude-3-5-sonnet": "claude-3-5-sonnet-20240620",
    "claude-3-5-sonnet-v2": "claude-3-5-sonnet-20241022",
    "claude-3-5-haiku": "claude-3-5-haiku-20241022",
    
    # Claude 3.7 family
    "claude-3-7-sonnet": "claude-3-7-sonnet-20250219",
    
    # OpenAI models
    "gpt-4o": "gpt-4o",
    "gpt-4.1": "gpt-4.1",
    "o4-mini": "o4-mini",
    "o3": "o3",
}

# List of all available model names (for command line choices)
AVAILABLE_MODELS = list(MODELS.keys())