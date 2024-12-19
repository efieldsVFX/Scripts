import nuke
from typing import List, Optional
from pathlib import Path
from .models import SystemInfo, DebugState
from .exceptions import NodeOperationError
from .logger import logger
from .utils import UndoContext, get_node_by_class, get_system_info

class DebugController:
    """Controller for debug operations."""
    
    def __init__(self):
        self.initial_state = DebugState.from_current_state()

    def limit_threads(self, thread_count: int = 4) -> None:
        """Limit Nuke thread count."""
        try:
            with UndoContext():
                nuke.toNode("preferences")["Threads"].setValue(thread_count)
                logger.info(f"Thread count limited to {thread_count}")
        except Exception as e:
            logger.error(f"Failed to limit threads: {e}")
            raise NodeOperationError("Failed to set thread limit") from e

    def change_allocator(self, allocator: str = "malloc") -> None:
        """Change memory allocator."""
        try:
            with UndoContext():
                nuke.toNode("preferences")["default_allocator"].setValue(allocator)
                logger.info(f"Changed allocator to {allocator}")
        except Exception as e:
            logger.error(f"Failed to change allocator: {e}")
            raise NodeOperationError("Failed to change allocator") from e

    def disable_nodes_by_class(self, node_class: str) -> int:
        """Disable all nodes of specified class."""
        try:
            count = 0
            with UndoContext():
                for node in get_node_by_class(node_class):
                    node["disable"].setValue(True)
                    count += 1
            logger.info(f"Disabled {count} {node_class} nodes")
            return count
        except Exception as e:
            logger.error(f"Failed to disable {node_class} nodes: {e}")
            raise NodeOperationError(f"Failed to disable {node_class} nodes") from e

    def localize_media(self, policy: str = "on") -> int:
        """Set localization policy for all Read nodes."""
        try:
            count = 0
            with UndoContext():
                for node in get_node_by_class("Read"):
                    node["localizationPolicy"].setValue(policy)
                    count += 1
            logger.info(f"Set localization policy to {policy} for {count} nodes")
            return count
        except Exception as e:
            logger.error(f"Failed to set localization policy: {e}")
            raise NodeOperationError("Failed to set localization policy") from e 

    def disable_postage_stamps(self) -> int:
        """Disable postage stamps on all applicable nodes."""
        try:
            count = 0
            with UndoContext():
                for node in nuke.allNodes():
                    if "postage_stamp" in node.knobs():
                        node["postage_stamp"].setValue(False)
                        count += 1
            logger.info(f"Disabled postage stamps on {count} nodes")
            return count
        except Exception as e:
            logger.error(f"Failed to disable postage stamps: {e}")
            raise NodeOperationError("Failed to disable postage stamps") from e

    def disable_autosave(self) -> None:
        """Disable Nuke's autosave functionality."""
        try:
            with UndoContext():
                nuke.toNode("preferences")["AutoSave"].setValue(False)
                logger.info("Disabled autosave")
        except Exception as e:
            logger.error(f"Failed to disable autosave: {e}")
            raise NodeOperationError("Failed to disable autosave") from e

    def restore_initial_state(self) -> None:
        """Restore Nuke to initial state."""
        try:
            with UndoContext():
                prefs = nuke.toNode("preferences")
                prefs["Threads"].setValue(self.initial_state.thread_limit)
                prefs["AutoSave"].setValue(self.initial_state.autosave_enabled)
                prefs["default_allocator"].setValue(self.initial_state.default_allocator)
            logger.info("Restored initial state")
        except Exception as e:
            logger.error(f"Failed to restore initial state: {e}")
            raise NodeOperationError("Failed to restore initial state") from e