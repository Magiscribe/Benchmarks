# Configuration settings specific to LLM Coordinate Grid Test

# Image dimensions
IMAGE_WIDTH = 512
IMAGE_HEIGHT = 512

# Square properties
SQUARE_SIZE = 5  # 5x5 pixel squares
NUM_SQUARES = 5  # Number of squares per image
SQUARE_COLOR = (0, 0, 0)  # Black squares
BACKGROUND_COLOR = (255, 255, 255)  # White background

# Grid coordinate system
# Bottom left: (0, 0)
# Top right: (512, 512)  
# Bottom right: (512, 0)
# Top left: (0, 512)

# Minimum distance between square centers to avoid overlap
MIN_DISTANCE_BETWEEN_SQUARES = 32

# Border distance (automatically calculated as half of MIN_DISTANCE_BETWEEN_SQUARES)
# Squares will be at least 16 pixels away from image borders

# Dataset Configuration
IMAGES_PER_SET = 10  # Number of test images to generate
OUTPUT_DIR = "assets"
DATASET_FILE = "dataset.json"

# Evaluation Settings
DEFAULT_MODEL = "llama-4-scout"
RESPONSES_DIR = "responses"
