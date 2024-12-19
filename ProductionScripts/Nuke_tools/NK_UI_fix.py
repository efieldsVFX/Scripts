from PySide2 import QtWidgets, QtGui
import nuke
import os
import logging
from configparser import ConfigParser
import shutil
from typing import Tuple, Optional
import unittest
import sys
from logging.handlers import RotatingFileHandler
import platform
import traceback
from functools import wraps
import datetime

MINIMUM_NUKE_VERSION = 13.0
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5MB
BACKUP_EXTENSION = ".backup"

def check_nuke_version() -> bool:
    """Check if current Nuke version meets minimum requirements."""
    try:
        current_version = float(nuke.NUKE_VERSION_STRING.split('v')[1])
        return current_version >= MINIMUM_NUKE_VERSION
    except Exception as e:
        logging.error(f"Failed to check Nuke version: {e}")
        return False

def error_telemetry(func):
    """Decorator to capture and report errors."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_info = {
                'timestamp': datetime.datetime.now().isoformat(),
                'function': func.__name__,
                'error': str(e),
                'traceback': traceback.format_exc(),
                'platform': platform.platform(),
                'python_version': sys.version,
                'nuke_version': nuke.NUKE_VERSION_STRING
            }
            logging.error(f"Error telemetry: {error_info}")
            return None
    return wrapper

def setup_logging():
    """Configure logging with rotation and both file and console handlers."""
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format
    )
    file_handler = RotatingFileHandler(
        "nuke_ui_fixer.log",
        maxBytes=MAX_LOG_SIZE,
        backupCount=3
    )
    file_handler.setFormatter(logging.Formatter(log_format))
    logging.getLogger().addHandler(file_handler)

def get_uistate_ini_path():
    return os.path.join(os.getenv("NUKE_DIR", os.path.expanduser("~")), ".nuke", "uistate.ini")

def load_config(uistate_ini_path):
    config = ConfigParser()
    try:
        config.read(uistate_ini_path)
        return config
    except Exception as e:
        logging.error(f"Failed to load config file: {e}")
        nuke.message("Error: Could not read uistate.ini file.")
        return None

def validate_input(value):
    try:
        num = int(value)
        return 0 <= num <= 9999
    except ValueError:
        return False

def backup_config(file_path: str) -> bool:
    """Create a backup of the config file before modifications."""
    try:
        backup_path = f"{file_path}.backup"
        shutil.copy2(file_path, backup_path)
        logging.info(f"Backup created at: {backup_path}")
        return True
    except Exception as e:
        logging.error(f"Failed to create backup: {e}")
        return False

def validate_dimensions(left: int, top: int, right: int, bottom: int) -> Tuple[bool, str]:
    """Validate window dimensions."""
    screen = QtWidgets.QApplication.primaryScreen().geometry()
    if right <= left or bottom <= top:
        return False, "Window width/height must be positive"
    if left < 0 or top < 0 or right > screen.width() or bottom > screen.height():
        return False, f"Window dimensions exceed screen bounds ({screen.width()}x{screen.height()})"
    if (right - left) < 50 or (bottom - top) < 50:
        return False, "Window dimensions too small (minimum 50x50)"
    return True, ""

def restore_from_backup(file_path: str) -> bool:
    """Restore configuration from backup file."""
    backup_path = f"{file_path}{BACKUP_EXTENSION}"
    try:
        if not os.path.exists(backup_path):
            logging.error("No backup file found")
            return False
        shutil.copy2(backup_path, file_path)
        logging.info(f"Successfully restored from backup: {backup_path}")
        return True
    except Exception as e:
        logging.error(f"Failed to restore from backup: {e}")
        return False

class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    def test_validate_input(self):
        self.assertTrue(validate_input("100"))
        self.assertTrue(validate_input("0"))
        self.assertTrue(validate_input("9999"))
        self.assertFalse(validate_input("-1"))
        self.assertFalse(validate_input("10000"))
        self.assertFalse(validate_input("abc"))
    def test_validate_dimensions(self):
        is_valid, _ = validate_dimensions(100, 100, 200, 200)
        self.assertTrue(is_valid)
        is_valid, msg = validate_dimensions(200, 100, 100, 200)
        self.assertFalse(is_valid)
        self.assertIn("must be positive", msg)
        is_valid, msg = validate_dimensions(0, 0, 40, 40)
        self.assertFalse(is_valid)
        self.assertIn("too small", msg)

@error_telemetry
def main():
    setup_logging()
    logging.info("Starting Nuke UI Fixer")
    if not check_nuke_version():
        nuke.message(f"Error: Nuke {MINIMUM_NUKE_VERSION}+ required")
        return
    uistate_ini_path = get_uistate_ini_path()
    if not os.path.exists(uistate_ini_path):
        logging.error(f"uistate.ini not found: {uistate_ini_path}")
        nuke.message(f"Error: uistate.ini file not found at {uistate_ini_path}")
        return
    if not os.access(uistate_ini_path, os.R_OK | os.W_OK):
        logging.error("Insufficient permissions for uistate.ini")
        nuke.message("Error: Insufficient permissions to access uistate.ini file.")
        return
    if not backup_config(uistate_ini_path):
        if not nuke.ask("Failed to create backup. Continue anyway?"):
            return
    config = load_config(uistate_ini_path)
    if not config:
        return
    main_logic(uistate_ini_path, config)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        unittest.TextTestRunner(verbosity=2).run(unittest.TestLoader().loadTestsFromTestCase(ValidationTests))
    else:
        main()
