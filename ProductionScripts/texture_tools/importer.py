"""
Texture importer module for handling multi-threaded texture imports.
Provides thread-safe importing of textures into Unreal Engine.
"""

import os
import math
import logging
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from PySide2.QtCore import QObject, QThread, QEventLoop, Qt
from PySide2.QtWidgets import (
    QDialog, QMessageBox, QVBoxLayout, QHBoxLayout, 
    QPushButton, QTreeWidget, QTreeWidgetItem,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QLabel, QProgressBar
)

# Configure logging
logger = logging.getLogger(__name__)

class TextureImporterWorker(QObject):
    """Worker class for handling texture imports in a separate thread."""
    
    def __init__(self, parent, selected_paths, auto_create_folders=False):
        """Initialize the worker with import parameters."""
        super().__init__()
        self.parent = parent
        self.selected_paths = selected_paths
        self.import_list = []
        self._thread = None
        self._io_worker = None
        self.auto_create_folders = auto_create_folders
        self._lock = Lock()
        self._is_running = False

    # Rest of TextureImporterWorker implementation...

class TextureImporterClass:
    """Main texture importer class."""
    
    def __init__(self):
        """Initialize the importer with thread safety."""
        self._import_lock = Lock()
        self._worker = None
        self._progress_dialog = None

    # Rest of TextureImporterClass implementation...

class IOWorker(QObject):
    """Worker class for IO operations."""
    
    def __init__(self, selected_paths):
        super().__init__()
        self.selected_paths = selected_paths

    # Rest of IOWorker implementation...

class SelectionDialog(QDialog):
    """Dialog for selecting assets to import."""
    
    def __init__(self, descriptors, parent=None):
        super(SelectionDialog, self).__init__(parent)
        self.setWindowTitle("Select Asset Builds and Object Names")
        # Rest of SelectionDialog implementation...

class ConfirmationDialog(QDialog):
    """Dialog for confirming import selections."""
    
    def __init__(self, parent, selected_items):
        super().__init__(parent)
        self.setWindowTitle("Confirm Import")
        # Rest of ConfirmationDialog implementation...

class ProgressDialog(QDialog):
    """Dialog for showing import progress."""
    
    def __init__(self, title, initial_message, parent=None):
        super(ProgressDialog, self).__init__(parent)
        self.setWindowTitle(title)
        # Rest of ProgressDialog implementation...

def run_texture_importer():
    """Entry point for running the texture importer."""
    # Implementation...

def register(core):
    """Register the texture importer with the core system."""
    # Implementation...
