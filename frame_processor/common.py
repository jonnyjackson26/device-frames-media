import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

GITHUB_PAGES_BASE_URL = "https://raw.githubusercontent.com/jonnyjackson26/device-frames-media/main/device-frames-output/"

# Alpha thresholds
ALPHA_CLEAR = 10      # Transparent threshold

# Constraints
# Aspect ratio bounds (portrait phones: 1.7-2.4, tablets: 1.3-1.6)
MIN_SCREEN_RATIO = 1.3    # Aspect ratio bounds
MAX_SCREEN_RATIO = 2.5
MIN_MASK_COVERAGE = 0.5   # Mask area / frame area
MAX_MASK_COVERAGE = 0.9
MIN_REGION_AREA = 5000    # Minimum region size (pixels)
