"""Logging configuration for the batch face importer package."""

import logging
import unreal

class UnrealLogger:
    """Custom logger that integrates with Unreal Engine's logging system."""
    
    def __init__(self, name="BatchFaceImporter"):
        """Initialize logger with name and default settings."""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Add Unreal output handler
        unreal_handler = UnrealLogHandler()
        unreal_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(unreal_handler)
        
        # Add console output handler for development
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(console_handler)

class UnrealLogHandler(logging.Handler):
    """Handler that routes Python logging to Unreal's logging system."""
    
    def emit(self, record):
        """Emit a log record to Unreal's logging system."""
        try:
            msg = self.format(record)
            if record.levelno >= logging.ERROR:
                unreal.log_error(msg)
            elif record.levelno >= logging.WARNING:
                unreal.log_warning(msg)
            else:
                unreal.log(msg)
        except Exception as e:
            # Fallback to print if logging fails
            print(f"Logging failed: {str(e)}")
            print(f"Original message: {record.getMessage()}")

def setup_logger(name="BatchFaceImporter", level=logging.INFO):
    """Set up and return a logger instance with the specified configuration."""
    logger = UnrealLogger(name).logger
    logger.setLevel(level)
    return logger

# Create global logger instance
logger = setup_logger()

def update_log_level(level):
    """Update the log level of the global logger."""
    logger.setLevel(level)
    
def log_error(message):
    """Convenience function for logging errors."""
    logger.error(message)
    
def log_warning(message):
    """Convenience function for logging warnings."""
    logger.warning(message)
    
def log_info(message):
    """Convenience function for logging info messages."""
    logger.info(message)
    
def log_debug(message):
    """Convenience function for logging debug messages."""
    logger.debug(message)