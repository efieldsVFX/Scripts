import nuke
from typing import List, Optional
from datetime import datetime, timedelta
from pathlib import Path
from .logger import logger
from .constants import LOG_DIR, LOG_RETENTION_DAYS
from .exceptions import LoggingError

def get_system_info() -> dict:
    """Gather system and Nuke information."""
    try:
        return {
            'nuke_version': nuke.NUKE_VERSION_STRING,
            'gpu_drivers': nuke.getGPUDrivers(),
            'plugin_path': nuke.plugin_path(),
            'user': nuke.env['user'],
            'script': nuke.root()['name'].value(),
            'platform': platform.platform(),
            'hostname': socket.gethostname()
        }
    except Exception as e:
        logger.error(f"Failed to gather system info: {e}")
        raise LoggingError("Failed to gather system information") from e

def cleanup_old_logs():
    """Remove log files older than retention period."""
    try:
        cutoff = datetime.now() - timedelta(days=LOG_RETENTION_DAYS)
        for log_file in LOG_DIR.glob("*.log"):
            if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff:
                log_file.unlink()
    except Exception as e:
        logger.error(f"Failed to cleanup logs: {e}")

def get_node_by_class(node_class: str) -> List[nuke.Node]:
    """Get all nodes of a specific class."""
    return [n for n in nuke.allNodes() if n.Class() == node_class]

class UndoContext:
    """Context manager for undo operations."""
    def __enter__(self):
        nuke.Undo.begin()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        nuke.Undo.end() 