import nuke
import nukescripts
from pathlib import Path
from .nk_debugging.views import DebugPanel
from .nk_debugging.logger import logger
from .nk_debugging.constants import __version__, __author__, __copyright__, __description__

def add_panel():
    """Register the debugging panel."""
    panel_id = "uk.co.thefoundry.NkDebugging"
    nukescripts.panels.registerPanel(panel_id, DebugPanel)
    logger.info(f"Registered debug panel with ID: {panel_id}")

def main():
    """Initialize and show the debugging panel."""
    try:
        panel_id = "uk.co.thefoundry.NkDebugging"
        panel = nukescripts.panels.restorePanel(panel_id)
        if panel:
            panel.show()
            logger.info("Debug panel displayed successfully")
        else:
            logger.error("Failed to restore debug panel")
    except Exception as e:
        logger.error(f"Failed to initialize debug panel: {e}")
        nuke.message(f"Error initializing debug panel: {str(e)}")

# Register menu command
nuke.menu("Nuke").addCommand(
    "Tools/Nuke Debugging Tool",
    "main()",
    "F10"
)

# Initialize panel on module load
add_panel()
