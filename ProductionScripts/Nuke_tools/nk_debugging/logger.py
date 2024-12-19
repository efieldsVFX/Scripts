import logging
from pathlib import Path
from datetime import datetime
from .constants import LOG_DIR

def setup_logger():
    """Configure the debugging tool logger."""
    logger = logging.getLogger("NukeDebugger")
    logger.setLevel(logging.DEBUG)

    # Ensure log directory exists
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # File handler
    log_file = LOG_DIR / f"debug_tool_{datetime.now():%Y%m%d}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger() 