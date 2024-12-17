"""
Logging Configuration
Sets up logging for the entire application
"""

import logging
import logging.handlers
import os
import yaml
from pathlib import Path

def setup_logging(config_path: str = "../config/config.yaml"):
    """
    Configure logging based on settings in config.yaml
    
    Args:
        config_path: Path to configuration file
    """
    try:
        # Load config
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        log_config = config['logging']
        
        # Create logs directory if it doesn't exist
        log_file = Path(log_config['file'])
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure root logger
        logger = logging.getLogger()
        logger.setLevel(log_config['level'])
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_config['file'],
            maxBytes=log_config['max_size'],
            backupCount=log_config['backup_count']
        )
        file_handler.setFormatter(logging.Formatter(log_config['format']))
        logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(log_config['format']))
        logger.addHandler(console_handler)
        
        logger.info("Logging configured successfully")
        
    except Exception as e:
        print(f"Error setting up logging: {str(e)}")
        raise

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name
    
    Args:
        name: Logger name (usually __name__ of the module)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
