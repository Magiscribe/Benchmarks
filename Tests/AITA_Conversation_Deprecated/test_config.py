# Configuration settings for AITA Conversation Test

# Conversation settings
MAX_TURNS = 15  # Maximum conversation rounds
MODELS_PER_CONVERSATION = 3  # Always 3 models debating

# Turn mechanics: 
# - First turn: random speaker
# - Subsequent turns: random selection from 2 models who didn't just speak
# - No model speaks twice in a row
TURN_ORDER = "conversational_random"

# Model selection for default test runs
DEFAULT_MODELS = [
    "claude-4.5-sonnet",  # Latest Anthropic flagship
    "gpt-5",              # Latest OpenAI flagship
    "gemini-2.5-pro"      # Latest Google flagship
]

# Position options
POSITIONS = ["YTA", "NTA"]  # You're The Asshole / Not The Asshole

# Dataset Configuration
NUM_SCENARIOS = 10  # Number of AITA scenarios
DATASET_FILE = "dataset.json"

# Output directories
CONVERSATIONS_DIR = "conversations"
RESPONSES_DIR = "responses"

# Evaluation Settings
DEFAULT_MODEL_TRIO = DEFAULT_MODELS
