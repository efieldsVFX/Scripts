"""Environment configuration for integrations.

This module handles loading and validating environment variables for the application.
It uses python-dotenv to load variables from a .env file and provides defaults
where appropriate.
"""

import os
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Configure module logger
logger = logging.getLogger(__name__)

def load_environment_config() -> bool:
    """Load environment configuration from .env file.
    
    Returns:
        bool: True if environment was loaded successfully, False otherwise.
    """
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        logger.info(f"Loaded environment from {env_path}")
        return True
    logger.warning(f"No .env file found at {env_path}")
    return False

def get_env_var(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """Get environment variable with validation.
    
    Args:
        key: Environment variable key
        default: Default value if not set
        required: Whether the variable is required
        
    Returns:
        str: Environment variable value or default
        
    Raises:
        ValueError: If required variable is missing
    """
    value = os.getenv(key, default)
    if required and not value:
        raise ValueError(f"Required environment variable {key} is not set")
    return value

# Load environment configuration
load_environment_config()

# FTrack Configuration
FTRACK_SERVER = get_env_var('FTRACK_SERVER', required=True)
FTRACK_API_KEY = get_env_var('FTRACK_API_KEY', required=True)
FTRACK_API_USER = get_env_var('FTRACK_API_USER', required=True)

# Project Configuration
PROJECT_ID = get_env_var('FTRACK_PROJECT_ID', required=True)
ASSET_BUILD_TYPE_NAME = get_env_var('FTRACK_ASSET_BUILD_TYPE', 'Character')

# Path Configuration
MOCAP_BASE_PATH = get_env_var('MOCAP_BASE_PATH', '/Game/Mocap/')
METAHUMAN_BASE_PATH = get_env_var('METAHUMAN_BASE_PATH', '/Game/Metahumans/MHID')

# Integration Settings
USE_FTRACK = get_env_var('USE_FTRACK', 'True').lower() == 'true'

# Logging Configuration
LOG_LEVEL = get_env_var('LOG_LEVEL', 'INFO')
LOG_FILE_PATH = get_env_var('LOG_FILE_PATH', 'logs/mha_batch_importer.log')

# Validate paths
def validate_paths():
    """Validate and create necessary directories."""
    log_dir = Path(LOG_FILE_PATH).parent
    log_dir.mkdir(parents=True, exist_ok=True)

validate_paths()