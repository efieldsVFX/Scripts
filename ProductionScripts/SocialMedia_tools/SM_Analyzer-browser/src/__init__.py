"""
Social Media Analyzer
"""
import logging
import os
from pathlib import Path

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logs_dir / "social_media_analyzer.log"),
        logging.StreamHandler()
    ]
)

# Create logger instance
logger = logging.getLogger("social_media_analyzer")

# API Configuration
API_CONFIG = {
    'instagram': {
        'access_token': os.getenv('INSTAGRAM_ACCESS_TOKEN', ''),
        'account_id': os.getenv('INSTAGRAM_ACCOUNT_ID', '')
    },
    'youtube': {
        'api_key': os.getenv('YOUTUBE_API_KEY', ''),
        'channel_id': os.getenv('YOUTUBE_CHANNEL_ID', '')
    },
    'tiktok': {
        'api_key': os.getenv('TIKTOK_API_KEY', ''),
        'app_id': os.getenv('TIKTOK_APP_ID', '')
    }
}

# Export these variables
__all__ = ['logger', 'API_CONFIG']