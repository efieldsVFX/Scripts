"""Main entry point for the batch metahuman importer."""

import sys
import unreal
from PySide6 import QtWidgets

from batch_metahuman_importer.gui.main_ui import BatchProcessorUI
from batch_metahuman_importer.utils.logging_config import logger

def run():
    """Initialize and run the batch metahuman importer application."""
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)

    # Create and show the main UI
    global ui
    ui = BatchProcessorUI()

    # Set up Unreal Engine tick callback
    def tick(delta_time):
        app.processEvents()
        return True

    # Keep global references
    global tick_handle, keep_alive
    tick_handle = unreal.register_slate_post_tick_callback(tick)

    # Create keepalive object to prevent garbage collection
    class KeepAlive:
        pass

    keep_alive = KeepAlive()
    keep_alive.ui = ui
    keep_alive.tick_handle = tick_handle

if __name__ == "__main__":
    run()
