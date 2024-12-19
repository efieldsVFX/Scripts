from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional

@dataclass
class SystemInfo:
    """System information data container."""
    nuke_version: str
    gpu_drivers: str
    plugin_path: str
    user: str
    script_name: str
    platform: str
    hostname: str
    timestamp: datetime = datetime.now()

@dataclass
class DebugState:
    """State container for debugging operations."""
    thread_limit: int
    autosave_enabled: bool
    default_allocator: str
    postage_stamps_enabled: bool

    @classmethod
    def from_current_state(cls) -> 'DebugState':
        """Create instance from current Nuke preferences."""
        import nuke
        prefs = nuke.toNode('preferences')
        return cls(
            thread_limit=prefs['Threads'].value(),
            autosave_enabled=prefs['AutoSave'].value(),
            default_allocator=prefs['default_allocator'].value(),
            postage_stamps_enabled=True  # Default Nuke state
        ) 