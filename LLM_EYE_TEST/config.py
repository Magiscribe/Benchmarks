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
    "claude-3-5-haiku": "claude-3-5-haiku-20241022",
    "claude-3-7-sonnet": "claude-3-7-sonnet-20250219",
    "claude-4-sonnet": "claude-sonnet-4-20250514",
    "claude-4-opus": "claude-opus-4-20250514",
    
    # OpenAI models
    "gpt-4o": "gpt-4o",
    "gpt-4.1": "gpt-4.1",
    "o4-mini": "o4-mini",

    # GOOGLE
    "gemini-2.5-pro": "gemini-2.5-pro-preview-05-06",
    "gemini-2.5-flash": "gemini-2.5-flash-preview-05-20",
    
    # GROQ
    "llama-4-maverick": "meta-llama/llama-4-maverick-17b-128e-instruct",
    "llama-4-scout": "meta-llama/llama-4-scout-17b-16e-instruct"
}

# List of all available model names (for command line choices)
AVAILABLE_MODELS = list(MODELS.keys())