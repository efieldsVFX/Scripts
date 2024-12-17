from .paths import setup_analysis_folders, get_desktop_path
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Assuming MODEL_CONFIG is already defined here
# MODEL_CONFIG = ...

# Add this configuration
MODEL_CONFIG = {
    'sentiment_model': 'distilbert-base-uncased-finetuned-sst-2-english',
    # Add any other model configurations you need
}

# Make sure MODEL_CONFIG is included in __all__ if you're using it
__all__ = ['logger', 'MODEL_CONFIG']
