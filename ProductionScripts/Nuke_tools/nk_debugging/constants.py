from enum import Enum
from pathlib import Path

class DebugActions(Enum):
    GENERATE_LOG = "Generate Log Info"
    LIMITED_THREADS = "Limit Threads"
    RESTART = "Restart Nuke"
    DEFAULT_ALLOCATOR = "Change Default Allocator to Malloc"
    DISABLE_CAM_READ = "Disable Camera Read from File"
    LOCALIZE = "Localize Media"
    DISABLE_AUTOSAVE = "Disable Autosave"
    DISABLE_ZDEFOCUS = "Disable All zDefocus Nodes"
    DISABLE_POSTAGE_STAMPS = "Disable All Postage Stamps"

# File paths
ROOT_DIR = Path(__file__).parent.parent
CONFIG_PATH = ROOT_DIR / "configs" / "debug_config.yaml"
LOG_DIR = Path.home() / ".nuke" / "debug_logs"

# Default settings
DEFAULT_THREAD_LIMIT = 4
MAX_LOG_FILES = 100
LOG_RETENTION_DAYS = 30 