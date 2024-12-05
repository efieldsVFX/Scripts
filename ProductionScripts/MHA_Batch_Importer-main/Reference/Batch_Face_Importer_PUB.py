# Standard library imports
import sys
import re
import time
import json
import os
import logging
import threading
from pathlib import Path
import importlib

# Third party imports
from PySide6 import QtWidgets, QtGui, QtCore
import unreal

# Local application imports
from export_performance import (
    run_anim_sequence_export,
    run_identity_level_sequence_export,
    run_meta_human_level_sequence_export
)
import export_performance
importlib.reload(export_performance)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants (default values)
DEFAULT_CONFIG = {
    'MAX_RETRIES': 3,
    'RETRY_DELAY': 5,
    'MAX_WORKERS': 1,  # Set to 1 to avoid multithreading issues
}

# Add this constant at the top of the file with the other constants
MOCAP_BASE_PATH = "/Game/01_ASSETS/External/Mocap/"
METAHUMAN_BASE_PATH = "/Game/01_ASSETS/Internal/Metahumans/MHID"


def get_config_path():
    """Return the path to the configuration file."""
    home_dir = Path.home()
    return home_dir / '.unreal_batch_processor_config.json'


def load_config():
    """Load configuration from file or create default if not exists."""
    config = DEFAULT_CONFIG.copy()
    config_path = get_config_path()
    if config_path.exists():
        try:
            with open(config_path, 'r') as config_file:
                loaded_config = json.load(config_file)
                config.update(loaded_config)
            logger.info(f"Configuration loaded from {config_path}")
        except json.JSONDecodeError:
            logger.error(f"Error parsing the configuration file at {config_path}. Using default values.")
        except Exception as e:
            logger.error(f"An error occurred while loading the configuration: {str(e)}. Using default values.")
    else:
        logger.warning(f"Configuration file not found at {config_path}. Using default values.")
        # Create default config file
        try:
            with open(config_path, 'w') as config_file:
                json.dump(DEFAULT_CONFIG, config_file, indent=4)
            logger.info(f"Created default configuration file at {config_path}")
        except Exception as e:
            logger.error(f"Failed to create default configuration file: {str(e)}")
    return config

# Load configuration
CONFIG = load_config()

# Use CONFIG values
MAX_RETRIES = CONFIG['MAX_RETRIES']
RETRY_DELAY = CONFIG['RETRY_DELAY']
MAX_WORKERS = CONFIG['MAX_WORKERS']


class ProgressDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, actor_character_mapping=None):
        super().__init__(parent)
        # Make dialog non-modal
        self.setModal(False)
        self.actor_character_mapping = actor_character_mapping or {}  # Store the mapping
        self.setWindowTitle("Processing")
        self.setGeometry(300, 300, 1200, 500)
        self.setStyleSheet("QDialog { background-color: #2b2b2b; color: #ffffff; }")
        # Set window flags to allow movement and stay on top
        self.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.WindowMinimizeButtonHint |
            QtCore.Qt.WindowMaximizeButtonHint |
            QtCore.Qt.WindowCloseButtonHint |
            QtCore.Qt.WindowStaysOnTopHint
        )
        
        layout = QtWidgets.QVBoxLayout(self)
        
        # Batch progress bar
        self.batch_progress_bar = QtWidgets.QProgressBar()
        self.batch_progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 10px;
                margin: 0.5px;
            }
        """)
        layout.addWidget(QtWidgets.QLabel("Batch Progress:"))
        layout.addWidget(self.batch_progress_bar)
        
        self.status_label = QtWidgets.QLabel("Processing...")
        layout.addWidget(self.status_label)
        
        # Progress table with column sizing
        self.progress_table = QtWidgets.QTableView()
        self.progress_model = QtGui.QStandardItemModel()
        self.progress_model.setHorizontalHeaderLabels([
            "Folder",
            "Character",
            "Slate",
            "Sequence",
            "Actor",
            "Take",
            "Process Status",
            "Export Status",
            "Error"
        ])
        
        # Set up the table view
        self.progress_table.setModel(self.progress_model)
        
        # Set column widths
        self.progress_table.setColumnWidth(0, 250)  # Folder
        self.progress_table.setColumnWidth(1, 100)  # Character
        self.progress_table.setColumnWidth(2, 80)   # Slate
        self.progress_table.setColumnWidth(3, 100)  # Sequence
        self.progress_table.setColumnWidth(4, 100)  # Actor
        self.progress_table.setColumnWidth(5, 80)   # Take
        self.progress_table.setColumnWidth(6, 120)  # Process Status
        self.progress_table.setColumnWidth(7, 120)  # Export Status
        self.progress_table.setColumnWidth(8, 200)  # Error
        
        # Enable horizontal scrolling and stretch last section
        self.progress_table.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.progress_table.horizontalHeader().setStretchLastSection(True)
        
        # Style the table
        self.progress_table.setStyleSheet("""
            QTableView {
                background-color: #3b3b3b;
                color: white;
                gridline-color: #555555;
                border: none;
            }
            QHeaderView::section {
                background-color: #2b2b2b;
                color: white;
                padding: 5px;
                border: 1px solid #555555;
            }
            QTableView::item {
                padding: 5px;
            }
            QTableView::item:selected {
                background-color: #4b4b4b;
            }
        """)
        
        layout.addWidget(self.progress_table)
        
        # Buttons and log area
        # self.cancel_button = QtWidgets.QPushButton("Cancel")
        # self.cancel_button.setStyleSheet("QPushButton { background-color: #f44336; color: white; }")
        # layout.addWidget(self.cancel_button)
        
        self.log_text = QtWidgets.QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(100)
        layout.addWidget(self.log_text)
        
        self.save_log_button = QtWidgets.QPushButton("Save Log")
        self.save_log_button.clicked.connect(self.save_log)
        layout.addWidget(self.save_log_button)
        
        self.close_button = QtWidgets.QPushButton("Close")
        self.close_button.setStyleSheet("""
            QPushButton { 
                background-color: #3b3b3b; 
                color: white; 
            }
            QPushButton:disabled {
                background-color: #707070;
                color: #a0a0a0;
            }
        """)
        self.close_button.setEnabled(False)  # Disabled initially
        self.close_button.clicked.connect(self.close)
        layout.addWidget(self.close_button)
        
        self.cancelled = False
        # self.cancel_button.clicked.connect(self.cancel)

    def set_batch_progress(self, value):
        self.batch_progress_bar.setValue(value)

    def set_status(self, text):
        self.status_label.setText(text)

    def cancel(self):
        # Comment out entire cancel method since it's not being used
        pass
        # self.cancelled = True
        # self.status_label.setText("Cancelling...")

    def add_item(self, folder_name, item_name):
        """Add item to progress dialog."""
        row_position = self.progress_model.rowCount()
        
        # Clean up folder name to show from Mocap forward
        if "Mocap" in str(folder_name):
            mocap_index = str(folder_name).find("Mocap")
            folder_name = str(folder_name)[mocap_index:]
        
        # Convert item_name to string and get just the filename if it's a path
        if '/' in str(item_name):
            item_name = str(item_name).split('/')[-1]
        
        # Remove '_Performance' suffix if present
        if item_name.endswith('_Performance'):
            item_name = item_name[:-11]
        
        # Parse the item name to extract components
        name_components = AssetProcessor.extract_name_variable(item_name)
        logger.info(f"Parsed components for {item_name}: {name_components}")
        
        # Create items for each column
        folder_item = QtGui.QStandardItem(str(folder_name))
        
        if name_components:
            # Standard format components
            character_item = QtGui.QStandardItem(str(name_components.get('character', '')))
            slate_item = QtGui.QStandardItem(str(name_components.get('slate', '')))
            sequence_item = QtGui.QStandardItem(str(name_components.get('sequence', '')))
            
            # Only display the actor associated with the character
            character = name_components.get('character', '').lower()
            actor_text = ''
            
            # Use character mapping regardless of single/dual/triple actor format
            if character in self.actor_character_mapping:
                actor_text = self.actor_character_mapping[character].capitalize()
            else:
                # Fallback to first actor if no mapping found
                actor_text = str(name_components.get('actor1' if name_components.get('is_dual_actor') or name_components.get('is_triple_actor') else 'actor', ''))
            
            actor_item = QtGui.QStandardItem(actor_text)
            
            # Just use take without subtake
            take = str(name_components.get('take', '')).split('_')[0]  # Remove subtake if present
            take_item = QtGui.QStandardItem(take)
        else:
            # Fallback handling
            parts = item_name.split('_')
            character_item = QtGui.QStandardItem(parts[0] if len(parts) > 0 else '')
            slate_item = QtGui.QStandardItem(parts[1] if len(parts) > 1 else '')
            sequence_item = QtGui.QStandardItem(parts[2] if len(parts) > 2 else '')
            actor_item = QtGui.QStandardItem(parts[3] if len(parts) > 3 else '')
            take = parts[4] if len(parts) > 4 else ''
            take_item = QtGui.QStandardItem(f"{take}")
            logger.warning(f"Failed to parse name components for: {item_name}")

        # Add the row with all columns
        self.progress_model.insertRow(row_position)
        self.progress_model.setItem(row_position, 0, folder_item)
        self.progress_model.setItem(row_position, 1, character_item)
        self.progress_model.setItem(row_position, 2, slate_item)
        self.progress_model.setItem(row_position, 3, sequence_item)
        self.progress_model.setItem(row_position, 4, actor_item)
        self.progress_model.setItem(row_position, 5, take_item)
        self.progress_model.setItem(row_position, 6, QtGui.QStandardItem("Waiting"))  # Process Status
        self.progress_model.setItem(row_position, 7, QtGui.QStandardItem("Waiting"))  # Export Status
        self.progress_model.setItem(row_position, 8, QtGui.QStandardItem(""))        # Error
        
        # Debug log for verification
        logger.info(f"Added row {row_position}: {[self.progress_model.item(row_position, i).text() for i in range(9)]}")

    def update_item_progress(self, index, status, error="", progress_type='processing'):
        """Update progress for a specific item."""
        try:
            if progress_type == 'processing':
                status_item = self.progress_model.item(index, 6)  # Process Status column
                if status_item:
                    status_item.setText(status)
            elif progress_type == 'exporting':
                status_item = self.progress_model.item(index, 7)  # Export Status column
                if status_item:
                    status_item.setText(status)

            if error:
                error_item = self.progress_model.item(index, 8)  # Error column
                if error_item:
                    current_error = error_item.text()
                    new_error = f"{current_error}\n{error}" if current_error else error
                    error_item.setText(new_error)

            self.update_overall_progress()
            
            # Update the log text with detailed progress (avoid duplicates)
            log_entry = f"Asset {index + 1}: {status}{' - ' + error if error else ''}"
            current_log = self.log_text.toPlainText()
            if log_entry not in current_log:
                self.log_text.append(log_entry)
                logger.info(log_entry)
        except Exception as e:
            logger.error(f"Error updating progress: {str(e)}")

    def update_overall_progress(self):
        """Update the overall progress and enable close button when all items are processed."""
        total_items = self.progress_model.rowCount()
        completed_items = 0
        
        # Count items that are either Complete or Failed in both processing and exporting
        for i in range(total_items):
            process_status = self.progress_model.item(i, 6).text()
            export_status = self.progress_model.item(i, 7).text()
            
            # Consider an item complete if:
            # 1. Both statuses are either "Complete" or "Failed", or
            # 2. Processing status is "Failed" (no need to wait for export in this case)
            if (process_status == "Failed" or 
                (process_status in ["Complete", "Failed"] and 
                 export_status in ["Complete", "Failed"])):
                completed_items += 1
        
        progress_percentage = (completed_items / total_items) * 100 if total_items > 0 else 0
        self.batch_progress_bar.setValue(int(progress_percentage))
        
        # Enable close button and update style when all items are processed
        if completed_items == total_items:
            self.close_button.setEnabled(True)
            self.close_button.setStyleSheet("""
                QPushButton { 
                    background-color: #007ACC; /* Microsoft Visual Studio Code blue */
                    color: white; 
                }
                QPushButton:hover {
                    background-color: #005999; /* Darker shade for hover */
                }
            """)
            #self.cancel_button.setEnabled(False)

    def save_log(self):
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Log File", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_name:
            with open(file_name, 'w') as f:
                f.write(self.log_text.toPlainText())
            logger.info(f"Log saved to {file_name}")

class MetaHumanHelper:
    # Update to include both base paths
    LEGACY_MHID_PATH = "/Game/PROJECT/LIVELINK/MHID"
    METAHUMAN_BASE_PATH = "/Game/01_ASSETS/Internal/Metahumans/MHID"

    # Update LEGACY_ACTORS to include ricardo, robert, and clara
    LEGACY_ACTORS = {
        'bev',              # Barb character (primary)
        'ralph',           # Tiny character
        'lewis', 'luis',  # Tim character
        'erwin',           # Andre character
        'mark',            # Flike character
        'ricardo',         # Doctor character
        'robert',          # Parole Officer character
        'clara'            # Shell character
    }

    # Update MHID_MAPPING to use legacy paths for ricardo, robert, and clara
    MHID_MAPPING = {
        # Legacy actors (using old path)
        'bev': f'{LEGACY_MHID_PATH}/MHID_Bev.MHID_Bev',
        'barb': f'{LEGACY_MHID_PATH}/MHID_Bev.MHID_Bev',
        'ralph': f'{LEGACY_MHID_PATH}/MHID_Ralph.MHID_Ralph',
        'tim': f'{LEGACY_MHID_PATH}/MHID_Lewis.MHID_Lewis',
        'lewis': f'{LEGACY_MHID_PATH}/MHID_Lewis.MHID_Lewis',
        'luis': f'{LEGACY_MHID_PATH}/MHID_Luis.MHID_Luis',
        'erwin': f'{LEGACY_MHID_PATH}/MHID_Erwin.MHID_Erwin',
        'mark': f'{LEGACY_MHID_PATH}/MHID_Mark.MHID_Mark',
        'ricardo': f'{LEGACY_MHID_PATH}/MHID_Ricardo.MHID_Ricardo',
        'robert': f'{LEGACY_MHID_PATH}/MHID_Robert.MHID_Robert',
        'clara': f'{LEGACY_MHID_PATH}/MHID_Clara.MHID_Clara',

        # Character mappings
        'tiny': f'{LEGACY_MHID_PATH}/MHID_Ralph.MHID_Ralph',
        'tim_lewis': f'{LEGACY_MHID_PATH}/MHID_Lewis.MHID_Lewis',
        'tim_luis': f'{LEGACY_MHID_PATH}/MHID_Luis.MHID_Luis',
        'andre': f'{LEGACY_MHID_PATH}/MHID_Erwin.MHID_Erwin',
        'flike': f'{LEGACY_MHID_PATH}/MHID_Mark.MHID_Mark',
        'doctor': f'{LEGACY_MHID_PATH}/MHID_Ricardo.MHID_Ricardo',
        'paroleofficer': f'{LEGACY_MHID_PATH}/MHID_Robert.MHID_Robert',
        'shell': f'{LEGACY_MHID_PATH}/MHID_Clara.MHID_Clara',

        # New pipeline actors
        'michael': f'{METAHUMAN_BASE_PATH}/Skeezer/MHID_Michael.MHID_Michael',
        'mike': f'{METAHUMAN_BASE_PATH}/Skeezer/MHID_Mike.MHID_Mike',
        'therese': f'{METAHUMAN_BASE_PATH}/Sonia/MHID_Therese.MHID_Therese',

        # Character mappings for new pipeline
        'skeezer': f'{METAHUMAN_BASE_PATH}/Skeezer/MHID_Michael.MHID_Michael',
        'sonia': f'{METAHUMAN_BASE_PATH}/Sonia/MHID_Therese.MHID_Therese'
    }

    SKELETAL_MESH_MAPPING = {
        # Legacy actors (using old path)
        'bev': f'{LEGACY_MHID_PATH}/SK_MHID_Bev.SK_MHID_Bev',
        'barb': f'{LEGACY_MHID_PATH}/SK_MHID_Bev.SK_MHID_Bev',
        'ralph': f'{LEGACY_MHID_PATH}/SK_MHID_Ralph.SK_MHID_Ralph',
        'tim': f'{LEGACY_MHID_PATH}/SK_MHID_Lewis.SK_MHID_Lewis',
        'lewis': f'{LEGACY_MHID_PATH}/SK_MHID_Lewis.SK_MHID_Lewis',
        'luis': f'{LEGACY_MHID_PATH}/SK_MHID_Luis.SK_MHID_Luis',
        'erwin': f'{LEGACY_MHID_PATH}/SK_MHID_Erwin.SK_MHID_Erwin',
        'mark': f'{LEGACY_MHID_PATH}/SK_MHID_Mark.SK_MHID_Mark',
        'ricardo': f'{LEGACY_MHID_PATH}/SK_MHID_Ricardo.SK_MHID_Ricardo',
        'robert': f'{LEGACY_MHID_PATH}/SK_MHID_Robert.SK_MHID_Robert',
        'clara': f'{LEGACY_MHID_PATH}/SK_MHID_Clara.SK_MHID_Clara',

        # Character mappings
        'tiny': f'{LEGACY_MHID_PATH}/SK_MHID_Ralph.SK_MHID_Ralph',
        'tim_lewis': f'{LEGACY_MHID_PATH}/SK_MHID_Lewis.SK_MHID_Lewis',
        'tim_luis': f'{LEGACY_MHID_PATH}/SK_MHID_Luis.SK_MHID_Luis',
        'andre': f'{LEGACY_MHID_PATH}/SK_MHID_Erwin.SK_MHID_Erwin',
        'flike': f'{LEGACY_MHID_PATH}/SK_MHID_Mark.SK_MHID_Mark',
        'doctor': f'{LEGACY_MHID_PATH}/SK_MHID_Ricardo.SK_MHID_Ricardo',
        'paroleofficer': f'{LEGACY_MHID_PATH}/SK_MHID_Robert.SK_MHID_Robert',
        'shell': f'{LEGACY_MHID_PATH}/SK_MHID_Clara.SK_MHID_Clara',

        # New pipeline actors
        'michael': f'{METAHUMAN_BASE_PATH}/Skeezer/SK_MHID_Michael.SK_MHID_Michael',
        'mike': f'{METAHUMAN_BASE_PATH}/Skeezer/SK_MHID_Mike.SK_MHID_Mike',
        'therese': f'{METAHUMAN_BASE_PATH}/Sonia/SK_MHID_Therese.SK_MHID_Therese',

        # Character mappings for new pipeline
        'skeezer': f'{METAHUMAN_BASE_PATH}/Skeezer/SK_MHID_Michael.SK_MHID_Michael',
        'sonia': f'{METAHUMAN_BASE_PATH}/Sonia/SK_MHID_Therese.SK_MHID_Therese'
    }

    @staticmethod
    def is_legacy_actor(actor_name: str) -> bool:
        """Check if the actor/character uses the legacy MHID path."""
        return actor_name.lower() in MetaHumanHelper.LEGACY_ACTORS

    @staticmethod
    def find_matching_identity(character_name):
        """Find matching MHID for given character name, handling legacy and new pipeline paths."""
        character_lower = character_name.lower()
        
        # Try to find direct match in MHID mapping
        mhid_path = MetaHumanHelper.MHID_MAPPING.get(character_lower)
        if mhid_path:
            # Log which path is being used
            if MetaHumanHelper.is_legacy_actor(character_lower):
                logger.info(f"Using legacy MHID path for {character_name}")
            else:
                logger.info(f"Using new pipeline MHID path for {character_name}")
            return mhid_path
            
        # If no match found, log the error
        logger.warning(f"No matching MHID found for character: {character_name}")
        logger.warning(f"Available MHID mappings: {list(MetaHumanHelper.MHID_MAPPING.keys())}")
        return None

    @staticmethod
    def process_shot(performance_asset, progress_callback, completion_callback, error_callback):
        """Process a MetaHuman performance shot using synchronous operations."""
        if not performance_asset:
            error_callback("Invalid performance asset provided")
            return False

        try:
            performance_asset.set_blocking_processing(True)
            progress_callback("Processing", 'processing')
            
            start_pipeline_error = performance_asset.start_pipeline()
            if start_pipeline_error == unreal.StartPipelineErrorType.NONE:
                # Since we're using blocking processing, we can proceed directly
                # The set_blocking_processing(True) call will wait until processing is complete
                progress_callback("Complete", 'processing')
                
                # Start the export process immediately after processing
                return MetaHumanHelper.export_shot(performance_asset, progress_callback, completion_callback, error_callback)
            else:
                error_msg = f"Pipeline start error: {start_pipeline_error}"
                error_callback(error_msg)
                progress_callback("Failed", 'processing')
                return False

        except Exception as e:
            error_callback(f"Processing error: {str(e)}")
            progress_callback("Failed", 'processing')
            return False

    @staticmethod
    def export_shot(performance_asset, progress_callback, completion_callback, error_callback):
        """Export a processed MetaHuman performance to animation sequence."""
        try:
            progress_callback("Starting Export", 'exporting')
            
            # Extract name components for folder structure
            asset_name = performance_asset.get_name()
            # Remove any subtake from asset name
            asset_name = '_'.join(asset_name.split('_')[0:-1]) if '_' in asset_name else asset_name
            
            # Get the identity name and find corresponding skeletal mesh
            identity = performance_asset.get_editor_property("identity")
            identity_name = identity.get_name().lower() if identity else None
            
            if identity_name and identity_name.startswith('mhid_'):
                identity_name = identity_name[5:]
            
            # Get the target skeletal mesh path
            target_mesh_path = MetaHumanHelper.SKELETAL_MESH_MAPPING.get(identity_name)
            if not target_mesh_path:
                error_msg = f"No skeletal mesh mapping found for character: {identity_name}"
                error_callback(error_msg)
                progress_callback("Failed", 'exporting')
                return False
            
            # Load the skeletal mesh asset
            target_skeletal_mesh = unreal.load_asset(target_mesh_path)
            if not target_skeletal_mesh:
                error_msg = f"Failed to load skeletal mesh at path: {target_mesh_path}"
                error_callback(error_msg)
                progress_callback("Failed", 'exporting')
                return False

            # Get the sequence-specific export path from metadata
            sequence_path = unreal.EditorAssetLibrary.get_metadata_tag(
                performance_asset,
                "sequence_export_path"
            )
            
            if not sequence_path:
                error_msg = "No sequence export path found in metadata"
                error_callback(error_msg)
                progress_callback("Failed", 'exporting')
                return False

            # Create export settings
            export_settings = unreal.MetaHumanPerformanceExportAnimationSettings()
            export_settings.set_editor_property("show_export_dialog", False)
            export_settings.set_editor_property("package_path", sequence_path)
            export_settings.set_editor_property("asset_name", f"AS_Face_{asset_name}")  # Ensure AS_Face_ prefix
            export_settings.set_editor_property("enable_head_movement", False)
            export_settings.set_editor_property("export_range", unreal.PerformanceExportRange.PROCESSING_RANGE)
            export_settings.set_editor_property("target_skeleton_or_skeletal_mesh", target_skeletal_mesh)
            export_settings.set_editor_property("auto_save_anim_sequence", True)
            
            # Export the animation sequence
            progress_callback("Exporting Animation", 'exporting')
            anim_sequence = unreal.MetaHumanPerformanceExportUtils.export_animation_sequence(
                performance_asset,
                export_settings
            )
            
            if anim_sequence:
                progress_callback("Complete", 'exporting')
                completion_callback()
                return True
            else:
                error_callback("Animation sequence export failed")
                progress_callback("Failed", 'exporting')
                return False

        except Exception as e:
            error_callback(f"Export error: {str(e)}")
            progress_callback("Failed", 'exporting')
            return False

class BatchProcessor(QtCore.QObject):
    progress_updated = QtCore.Signal(int, str, str, str)
    processing_finished = QtCore.Signal()
    error_occurred = QtCore.Signal(str)

    def __init__(self):
        super().__init__()
        self.asset_processor = AssetProcessor()
        self.helper = MetaHumanHelper()
        self.all_capture_data = []
        self.is_folder = True
        self.current_index = 0
        # Get editor asset subsystem
        self.editor_subsystem = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)

    def run_batch_process(self, selections, is_folder=True):
        """Initialize and start the batch processing"""
        logger.info("Starting batch process...")
        self.all_capture_data = selections if isinstance(selections, list) else []
        self.is_folder = is_folder
        self.current_index = 0

        if not self.all_capture_data:
            logger.error(f"Invalid selections type: {type(selections)}")
            return

        logger.info(f"Processing {len(self.all_capture_data)} assets")
        # Process first asset
        QtCore.QTimer.singleShot(0, self._process_next_asset)

    def _process_next_asset(self):
        """Process next asset in queue"""
        try:
            if self.current_index >= len(self.all_capture_data):
                self.processing_finished.emit()
                return

            capture_data_asset = self.all_capture_data[self.current_index]
            self.progress_updated.emit(self.current_index, "Processing", "", 'processing')

            # Create performance asset
            performance_asset = self.asset_processor.create_performance_asset(
                capture_data_asset.package_name, 
                "/Game/MHA-Data/"
            )

            if not performance_asset:
                self.progress_updated.emit(self.current_index, "Failed", "Failed to create performance asset", 'processing')
                self.current_index += 1
                QtCore.QTimer.singleShot(0, self._process_next_asset)
                return

            # Process the shot
            success = self.helper.process_shot(
                performance_asset,
                lambda status, progress_type='processing': 
                    self.progress_updated.emit(self.current_index, status, "", progress_type),
                lambda: self._on_shot_complete(self.current_index),
                lambda error: self._on_shot_error(self.current_index, error)
            )

            if not success:
                self.progress_updated.emit(self.current_index, "Failed", "Failed to process shot", 'processing')
                self.current_index += 1
                QtCore.QTimer.singleShot(0, self._process_next_asset)

        except Exception as e:
            logger.error(f"Error processing asset: {str(e)}")
            self.progress_updated.emit(self.current_index, "Failed", str(e), 'processing')
            self.current_index += 1
            QtCore.QTimer.singleShot(0, self._process_next_asset)

    def _on_shot_complete(self, index):
        """Handle shot completion"""
        self.progress_updated.emit(index, "Complete", "", 'processing')
        self.current_index += 1
        QtCore.QTimer.singleShot(0, self._process_next_asset)

    def _on_shot_error(self, index, error):
        """Handle shot error"""
        self.progress_updated.emit(index, "Failed", error, 'processing')
        self.current_index += 1
        QtCore.QTimer.singleShot(0, self._process_next_asset)

class AssetProcessor:
    def __init__(self):
        self.asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
        self.asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        # Update the name patterns to include all actor formats
        self.name_patterns = [
            # Quad actor pattern (4 actors)
            r"^(?:(\w+)_)?(S\d+)_(\d+)_(\w+)_(\w+)_(\w+)_(\w+)_(\d+)(?:_\d+)?$",
            # Triple actor pattern (3 actors)
            r"^(?:(\w+)_)?(S\d+)_(\d+)_(\w+)_(\w+)_(\w+)_(\d+)(?:_\d+)?$",
            # Dual actor pattern (2 actors)
            r"^(?:(\w+)_)?(S\d+)_(\d+)_(\w+)_(\w+)_(\d+)(?:_\d+)?$",
            # Single actor pattern (1 actor)
            r"^(?:(\w+)_)?(S\d+)_(\d+)_(\w+)_(\d+)(?:_\d+)?$",
            # TT format pattern
            r"^TT-(\w+)-(\d+)_(\d+)$"
        ]
        # Complete actor to character mapping
        self.actor_character_mapping = {
            # Legacy actors to characters
            'bev': 'barb',           # Primary mapping for Barb
            'beverly': 'barb',       # Alternative mapping
            'ralph': 'tiny',
            'lewis': 'tim',
            'luis': 'tim',
            'erwin': 'andre',
            'mark': 'flike',
            
            # Reverse mappings (character to actor)
            'barb': 'bev',           # Maps to bev (not beverly)
            'tiny': 'ralph',
            'tim': 'lewis',
            'andre': 'erwin',
            'flike': 'mark',
            
            # New pipeline actors to characters
            'michael': 'skeezer',
            'mike': 'skeezer',
            'ricardo': 'doctor',
            'robert': 'paroleofficer',
            'therese': 'sonia',
            'clara': 'shell',
            
            # New pipeline reverse mappings
            'skeezer': 'michael',
            'doctor': 'ricardo',
            'paroleofficer': 'robert',
            'sonia': 'therese',
            'shell': 'clara'
        }

    def get_available_folders(self):
        logger.info("Fetching available folders...")
        full_paths = self.asset_registry.get_sub_paths(MOCAP_BASE_PATH, recurse=True)
        
        # Filter and clean paths to only show from "Mocap" forward
        cleaned_paths = []
        for path in full_paths:
            if "Mocap" in path:
                # Find the index of "Mocap" in the path
                mocap_index = path.find("Mocap")
                # Get everything from "Mocap" forward
                cleaned_path = path[mocap_index:]
                if self.folder_has_capture_data(path):  # Still check using full path
                    cleaned_paths.append(cleaned_path)
        
        logger.info(f"Found {len(cleaned_paths)} folders with capture data")
        return cleaned_paths

    def folder_has_capture_data(self, folder):
        search_filter = unreal.ARFilter(
            package_paths=[folder], 
            class_names=["FootageCaptureData"], 
            recursive_paths=True
        )
        return bool(self.asset_registry.get_assets(search_filter))

    def get_capture_data_assets(self, folder):
        """Get all capture data assets from a folder."""
        logger.info(f"Searching for assets in folder: {folder}")
        
        # Ensure the folder path is properly formatted
        folder_path = str(folder)
        # Remove base path prefix if it exists
        if folder_path.startswith(f'{MOCAP_BASE_PATH}/'):
            folder_path = folder_path[len(f'{MOCAP_BASE_PATH}/'):]
        
        # Add the proper base path prefix
        folder_path = f"{MOCAP_BASE_PATH}/{folder_path.strip('/')}"
        
        logger.info(f"Searching with formatted path: {folder_path}")

        search_filter = unreal.ARFilter(
            package_paths=[folder_path],
            class_names=["FootageCaptureData"],
            recursive_paths=True,  # Enable recursive search
            recursive_classes=True
        )
        
        try:
            assets = self.asset_registry.get_assets(search_filter)
            logger.info(f"Found {len(assets)} assets in {folder_path}")
            
            # Log each found asset for debugging
            for asset in assets:
                logger.info(f"Found asset: {asset.package_name}")
            
            if not assets:
                # Try alternative path format
                alt_folder_path = folder_path.replace(MOCAP_BASE_PATH, '/Game/')
                logger.info(f"Trying alternative path: {alt_folder_path}")
                search_filter.package_paths = [alt_folder_path]
                assets = self.asset_registry.get_assets(search_filter)
                logger.info(f"Found {len(assets)} assets with alternative path")
                
            return assets
        except Exception as e:
            logger.error(f"Error getting assets: {str(e)}")
            return []

    def get_all_capture_data_assets(self):
        """Get all capture data assets in the project."""
        logger.info("Fetching all capture data assets...")
        
        # Create filter for FootageCaptureData assets
        asset_filter = unreal.ARFilter(
            class_names=["FootageCaptureData"],
            package_paths=[MOCAP_BASE_PATH],
            recursive_paths=True,
            recursive_classes=True
        )
        
        # Get assets using the filter
        assets = self.asset_registry.get_assets(asset_filter)
        
        # Clean up asset display names and paths
        cleaned_assets = []
        for asset in assets:
            if asset:
                # Get the full path
                full_path = str(asset.package_path)
                
                # Find the index of "Mocap" in the path
                if "Mocap" in full_path:
                    mocap_index = full_path.find("Mocap")
                    # Set a cleaned display path from "Mocap" forward
                    display_path = full_path[mocap_index:]
                    
                    # Create a wrapper object that maintains the original asset but shows cleaned path
                    class AssetWrapper:
                        def __init__(self, original_asset, display_path):
                            self._asset = original_asset
                            self.display_path = display_path
                        
                        def __getattr__(self, attr):
                            return getattr(self._asset, attr)
                        
                        def get_display_path(self):
                            return self.display_path
                    
                    wrapped_asset = AssetWrapper(asset, display_path)
                    cleaned_assets.append(wrapped_asset)
        
        logger.info(f"Found {len(cleaned_assets)} capture data assets")
        return cleaned_assets

    @staticmethod
    def extract_name_variable(asset_name: str) -> dict:
        """Extract variables from asset name with support for all naming patterns."""
        # Clean up the name
        if asset_name.endswith('_Performance'):
            asset_name = asset_name[:-11]
        asset_name = asset_name.rstrip('_')
        
        logger.info(f"Extracting name components from: {asset_name}")
        
        # Define patterns for all formats
        patterns = [
            # Quad actor pattern (4 actors)
            # Example: Barb_S063_0290_Erwin_Beverly_Clara_Mike_010_10
            r'^(?P<character>[^_]+)_S(?P<slate>\d+)_(?P<sequence>\d+)_(?P<actor1>[^_]+)_(?P<actor2>[^_]+)_(?P<actor3>[^_]+)_(?P<actor4>[^_]+)_(?P<take>\d+)(?:_(?P<subtake>\d+))?$',
            
            # Triple actor pattern (3 actors)
            # Example: Barb_S063_0290_Erwin_Beverly_Clara_010_10
            r'^(?P<character>[^_]+)_S(?P<slate>\d+)_(?P<sequence>\d+)_(?P<actor1>[^_]+)_(?P<actor2>[^_]+)_(?P<actor3>[^_]+)_(?P<take>\d+)(?:_(?P<subtake>\d+))?$',
            
            # Dual actor pattern (2 actors)
            # Example: Barb_S063_0290_Erwin_Beverly_010_10
            r'^(?P<character>[^_]+)_S(?P<slate>\d+)_(?P<sequence>\d+)_(?P<actor1>[^_]+)_(?P<actor2>[^_]+)_(?P<take>\d+)(?:_(?P<subtake>\d+))?$',
            
            # Single actor pattern (1 actor)
            # Example: Barb_S063_0290_Erwin_010_10
            r'^(?P<character>[^_]+)_S(?P<slate>\d+)_(?P<sequence>\d+)_(?P<actor1>[^_]+)_(?P<take>\d+)(?:_(?P<subtake>\d+))?$'
        ]
        
        # Try each pattern
        for i, pattern in enumerate(patterns):
            logger.info(f"Trying pattern {i + 1}: {pattern}")
            match = re.match(pattern, asset_name)
            if match:
                components = match.groupdict()
                logger.info(f"Pattern {i + 1} matched! Raw components: {components}")
                
                # Set actor count flags
                components['is_quad_actor'] = bool('actor4' in components and components['actor4'])
                components['is_triple_actor'] = bool('actor3' in components and components['actor3'] and not components.get('actor4'))
                components['is_dual_actor'] = bool('actor2' in components and components['actor2'] and not components.get('actor3'))
                components['is_single_actor'] = bool('actor1' in components and not components.get('actor2'))
                
                logger.info(f"Actor format flags - Quad: {components['is_quad_actor']}, "
                           f"Triple: {components['is_triple_actor']}, "
                           f"Dual: {components['is_dual_actor']}, "
                           f"Single: {components['is_single_actor']}")
                
                # Store all actor names in a list for easy access
                components['all_actors'] = []
                if components.get('actor4'):
                    components['all_actors'] = [
                        components['actor1'],
                        components['actor2'],
                        components['actor3'],
                        components['actor4']
                    ]
                    logger.info(f"Quad actor format detected: {components['all_actors']}")
                elif components.get('actor3'):
                    components['all_actors'] = [
                        components['actor1'],
                        components['actor2'],
                        components['actor3']
                    ]
                    logger.info(f"Triple actor format detected: {components['all_actors']}")
                elif components.get('actor2'):
                    components['all_actors'] = [
                        components['actor1'],
                        components['actor2']
                    ]
                    logger.info(f"Dual actor format detected: {components['all_actors']}")
                else:
                    components['all_actors'] = [components['actor1']]
                    logger.info(f"Single actor format detected: {components['all_actors']}")
                
                # Pad numbers to ensure consistent formatting
                if components.get('slate'):
                    components['slate'] = components['slate'].zfill(4)
                if components.get('sequence'):
                    components['sequence'] = components['sequence'].zfill(4)
                if components.get('take'):
                    components['take'] = components['take'].zfill(3)
                
                logger.info(f"Final processed components: {components}")
                return components
        
        # If no pattern matches, log the failure and details about the name
        logger.warning(f"No pattern matched for asset name: {asset_name}")
        logger.debug(f"Name parts: {asset_name.split('_')}")
        return None

    def get_available_identities(self):
        logger.info("Fetching available identities...")
        search_filter = unreal.ARFilter(
            package_paths=["/Game/PROJECT/LIVELINK/MHID"],
            class_names=["MetaHumanIdentity"],
            recursive_paths=True
        )
        assets = self.asset_registry.get_assets(search_filter)
        # Convert Name objects to strings
        return {str(asset.asset_name): str(asset.package_name) for asset in assets}

    def find_matching_identity(self, capture_data_name):
        """
        Find matching identity based on character name, handling actor-character relationships.
        """
        available_identities = self.get_available_identities()
        logger.info(f"Available identities: {available_identities}")
        
        name_components = self.extract_name_variable(capture_data_name)
        if not name_components:
            logger.error(f"Could not parse capture data name: {capture_data_name}")
            return None
        
        # Get the character name (this is who we want to process)
        character = name_components.get('character', '').lower().strip()
        
        # Find the actor name for this character
        actor_name = self.actor_character_mapping.get(character, character)
        logger.info(f"Mapped character '{character}' to actor '{actor_name}'")
        
        # Look for matching identity using actor name
        expected_mhid = f"MHID_{actor_name.capitalize()}"
        logger.info(f"Looking for MHID match: {expected_mhid}")
        
        # Look for matching identity
        for identity_name, identity_path in available_identities.items():
            identity_name = str(identity_name).lower()
            
            if identity_name.startswith("mhid_"):
                identity_actor = identity_name[5:].lower().strip()
                logger.info(f"Comparing {actor_name} with {identity_actor}")
                
                if actor_name == identity_actor:
                    logger.info(f"Found matching identity: {identity_path}")
                    return identity_path
        
        logger.warning(f"No matching identity found for character: {character} (Actor: {actor_name})")
        logger.warning(f"Expected MHID name would be: {expected_mhid}")
        return None

    # Add this at the class level of AssetProcessor
    SEQUENCE_MAPPING = {
        # Format: 'shot_number': ('parent_sequence_folder', 'shot_code')
        '0010': ('0010_Prologue', 'PRO'),
        '0020': ('0020_The_Effigy', 'EFF'),
        '0030': ('0030_Parole_Officer_Visit', 'POV'),
        '0040': ('0040_Andre_Work', 'ANW'),
        '0050': ('0050_Barb_Shell_Pool_Time', 'BSP'),
        '0060': ('0060_Barb_Shell_Kitchen_Toast', 'BSK'),
        '0070': ('0070_Walking_To_Flike', 'WTF'),
        '0080': ('0080_Meeting_Flike', 'MEF'),
        '0090': ('0090_Speaking_To_Tim', 'STT'),
        '0100': ('0100_Back_Alley_Walk', 'BAW'),
        '0110': ('0110_SoniaX_Ad', 'SXA'),
        '0120': ('0120_Andre_Bike_Ride', 'ABR'),
        '0130': ('0130_Flike_Vets', 'FLV'),
        '0140': ('0140_Barb_Shell_Meet_Tiny', 'BST'),
        '0150': ('0150_Andre_Eating', 'ANE'),
        '0160': ('0160_Hurricane_Twerking', 'HUT'),
        '0170': ('0170_Pray_Leprechaun', 'PRL'),
        '0180': ('0180_Andre_Thinking', 'ANT'),
        '0190': ('0190_Andre_Refuses_Job', 'ARJ'),
        '0200': ('0200_Doctor_Visit', 'DRV'),
        '0210': ('0210_Flikes_Tap_Dance', 'FTP'),
        '0220': ('0220_Whore_House_Inspection', 'WHI'),
        '0230': ('0230_Andre_Stargazing', 'AST'),
        '0240': ('0240_Molotov_Walk', 'MOW'),
        '0250': ('0250_Molotov_Cocktail', 'MOC'),
        '0260': ('0260_Picking_Up_Tim', 'PUT'),
        '0270': ('0270_Andre_Listens_Heart', 'ALH'),
        '0280': ('0280_Andre_Takes_Job', 'ATJ'),
        '0290': ('0290_Barb_Shell_Meet_Andre', 'BMA'),
        '0300': ('0300_Andre_Self_Reflects', 'ASR'),
        '0310': ('0310_Basketball_Match', 'BBM'),
        '0320': ('0320_Tims_House', 'TMH'),
        '0330': ('0330_Andre_Runs_Home', 'ARH'),
        '0340': ('0340_Barb_Shell_Celebrate', 'BSC'),
        '0350': ('0350_Flike_Raps', 'FLR'),
        '0360': ('0360_Sonia_Limo_Ride', 'SLR'),
        '0370': ('0370_Andre_Sonia', 'ASO'),
        '0380': ('0380_Flike_Molotov_Cocktail', 'FMC'),
        '0390': ('0390_The_Fairy_Costume', 'TFC'),
        '0400': ('0400_Barb_Shell_Dance', 'BSD'),
        '0410': ('0410_Andres_Death', 'ADE'),
        '0420': ('0420_Flikes_Fire_Dance', 'FFD'),
        '0430': ('0430_Andres_Burial', 'ABU'),
        '0440': ('0440_Andre_at_Church', 'AAC')
    }

    def get_sequence_folder(self, sequence_number: str) -> tuple:
        """
        Get the parent sequence folder and shot code for a given sequence number.
        Returns tuple of (parent_folder, shot_code)
        """
        # Find the parent sequence number (first 3 digits + 0)
        parent_seq = sequence_number[:3] + '0'
        
        if parent_seq in self.SEQUENCE_MAPPING:
            parent_folder, shot_code = self.SEQUENCE_MAPPING[parent_seq]
            return parent_folder, shot_code
        else:
            logger.warning(f"No mapping found for sequence {sequence_number}, using default structure")
            return (f"{parent_seq}_Unknown", "UNK")

    def create_performance_asset(self, path_to_capture_data: str, save_performance_location: str) -> unreal.MetaHumanPerformance:
        """Create performance asset with new folder structure."""
        try:
            capture_data_asset = unreal.load_asset(path_to_capture_data)
            if not capture_data_asset:
                raise ValueError(f"Failed to load capture data asset at {path_to_capture_data}")

            capture_data_name = capture_data_asset.get_name()
            name_components = self.extract_name_variable(capture_data_name)
            
            if not name_components:
                raise ValueError(f"Could not parse name components from {capture_data_name}")
                
            logger.info(f"Creating performance asset with components: {name_components}")
            
            character = name_components.get('character', 'Unknown').lower()
            sequence = name_components.get('sequence', '0000')
            take = name_components.get('take', '000')
            
            # Get the mapped actor for this character
            mapped_actor = self.actor_character_mapping.get(character, character)
            logger.info(f"Character '{character}' is mapped to actor '{mapped_actor}'")
            
            # Get sequence folder structure
            sequence_padded = sequence.zfill(4)
            parent_folder, shot_code = self.get_sequence_folder(sequence_padded)
            
            # Build the new folder paths
            base_path = f"/Game/02_SEQUENCES/{parent_folder}/{sequence_padded}_{shot_code}_MAIN"
            mha_path = f"{base_path}/MHA-DATA/{take}/{character}"
            performance_path = f"{mha_path}/MHP"
            
            # Create the performance asset name using only the mapped actor
            performance_asset_name = f"Face_{character}_S{name_components['slate']}_{sequence}_{mapped_actor}_{take}_Performance"
            logger.info(f"Creating performance asset: {performance_asset_name}")

            # Create the performance asset
            performance_asset = self.asset_tools.create_asset(
                asset_name=performance_asset_name,
                package_path=performance_path,
                asset_class=unreal.MetaHumanPerformance,
                factory=unreal.MetaHumanPerformanceFactoryNew()
            )
            
            if not performance_asset:
                raise ValueError(f"Failed to create performance asset {performance_asset_name}")

            # Set properties and metadata
            identity_asset = self._get_identity_asset(name_components)
            performance_asset.set_editor_property("identity", identity_asset)
            performance_asset.set_editor_property("footage_capture_data", capture_data_asset)
            
            # Store export paths in metadata - Single character folder
            export_path = f"{mha_path}"
            unreal.EditorAssetLibrary.set_metadata_tag(
                performance_asset,
                "sequence_export_path",
                export_path
            )
            
            # Update the animation sequence name format using only the mapped actor
            anim_sequence_name = f"AS_Face_{character}_S{name_components['slate']}_{sequence}_{mapped_actor}_{take}"
            
            # Store the animation sequence name in metadata
            unreal.EditorAssetLibrary.set_metadata_tag(
                performance_asset,
                "animation_sequence_name",
                anim_sequence_name
            )
            
            # Save and return the asset
            unreal.EditorAssetLibrary.save_loaded_asset(performance_asset)
            return performance_asset

        except Exception as e:
            logger.error(f"Error creating performance asset: {str(e)}")
            raise

    def _get_identity_asset(self, name_components):
        """Get the appropriate identity asset based on actor information."""
        try:
            # Debug logging for incoming components
            logger.info(f"Starting _get_identity_asset with components: {name_components}")
            
            if not name_components:
                raise ValueError("No name components provided")

            # Get the character name first
            character = name_components.get('character', '')
            if not character:
                raise ValueError("No character found in name components")
            character = character.lower()
            
            # Determine which actor we should use based on the format
            actor_name = None
            if name_components.get('is_quad_actor'):
                logger.info("Quad actor format detected")
                actor_name = name_components.get('actor1', '').lower()
                logger.info(f"Using first actor: {actor_name}")
            elif name_components.get('is_triple_actor'):
                logger.info("Triple actor format detected")
                actor_name = name_components.get('actor1', '').lower()
                logger.info(f"Using first actor: {actor_name}")
            elif name_components.get('is_dual_actor'):
                logger.info("Dual actor format detected")
                actor_name = name_components.get('actor1', '').lower()
                logger.info(f"Using first actor: {actor_name}")
            else:
                logger.info("Single actor format detected")
                actor_name = name_components.get('actor', '').lower()
                if not actor_name:
                    actor_name = name_components.get('actor1', '').lower()
                logger.info(f"Using actor: {actor_name}")

            if not actor_name:
                raise ValueError(f"No actor name found in components: {name_components}")
            
            logger.info(f"Processing character: {character}, actor: {actor_name}")
            
            # First try to get the MHID directly from the character
            identity_path = MetaHumanHelper.MHID_MAPPING.get(character)
            logger.info(f"Trying character MHID mapping for '{character}': {identity_path}")
            
            # If no direct character mapping, try the actor mapping
            if not identity_path:
                # Get character name from actor mapping if it exists
                mapped_character = self.actor_character_mapping.get(actor_name)
                logger.info(f"Actor '{actor_name}' mapped to character: {mapped_character}")
                
                if mapped_character:
                    identity_path = MetaHumanHelper.MHID_MAPPING.get(mapped_character.lower())
                    logger.info(f"Trying mapped character MHID for '{mapped_character}': {identity_path}")
                
                # If still no mapping, try the actor directly
                if not identity_path:
                    identity_path = MetaHumanHelper.MHID_MAPPING.get(actor_name)
                    logger.info(f"Trying direct actor MHID mapping for '{actor_name}': {identity_path}")
            
            if not identity_path:
                error_msg = f"No MHID found for {actor_name} ({character} character)"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            logger.info(f"Using MHID path: {identity_path}")
            identity_asset = unreal.load_asset(identity_path)
            
            if not identity_asset:
                error_msg = f"Failed to load MHID at path: {identity_path}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            return identity_asset

        except Exception as e:
            logger.error(f"Error in _get_identity_asset: {str(e)}")
            logger.error(f"Name components: {name_components}")
            raise

class UnifiedSelectionDialog(QtWidgets.QDialog):
    """Dialog for selecting either folders or individual capture data assets."""
    def __init__(self, available_folders, capture_data_assets, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Items for Batch Processing")
        self.setGeometry(300, 300, 500, 400)
        self.setStyleSheet("""
            QDialog { 
                background-color: #2b2b2b; 
                color: #ffffff; 
            }
            QTreeWidget {
                background-color: #3b3b3b;
                color: #ffffff;
                border: 1px solid #555555;
            }
            QTreeWidget::item {
                padding: 4px;
            }
            QTreeWidget::item:hover {
                background-color: #4b4b4b;
            }
            QTreeWidget::item:selected {
                background-color: #555555;
            }
            QRadioButton {
                color: white;
                padding: 5px;
            }
            QRadioButton::indicator {
                width: 13px;
                height: 13px;
            }
        """)

        layout = QtWidgets.QVBoxLayout(self)

        # Add radio buttons for selection type
        self.radio_layout = QtWidgets.QHBoxLayout()
        self.folder_radio = QtWidgets.QRadioButton("Folders")
        self.asset_radio = QtWidgets.QRadioButton("Capture Data Assets")
        self.folder_radio.setChecked(True)
        self.radio_layout.addWidget(self.folder_radio)
        self.radio_layout.addWidget(self.asset_radio)
        layout.addLayout(self.radio_layout)

        # Connect radio buttons
        self.folder_radio.toggled.connect(self.switch_view)
        self.asset_radio.toggled.connect(self.switch_view)

        # Add search functionality
        search_layout = QtWidgets.QHBoxLayout()
        search_label = QtWidgets.QLabel("Search:")
        search_label.setStyleSheet("color: white;")
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #3b3b3b;
                color: white;
                border: 1px solid #555555;
                padding: 4px;
            }
        """)
        self.search_input.textChanged.connect(self.filter_tree)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Create tree widget
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderLabel("Available Items")
        self.tree.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        layout.addWidget(self.tree)

        # Store data
        self.available_folders = available_folders
        self.capture_data_assets = capture_data_assets

        # Populate initial view (folders)
        self.populate_folders()

        # Add buttons
        button_layout = QtWidgets.QHBoxLayout()
        self.ok_button = QtWidgets.QPushButton("OK")
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        
        for btn in [self.ok_button, self.cancel_button]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3b3b3b;
                    color: white;
                    border: 1px solid #555555;
                    padding: 5px 15px;
                }
                QPushButton:hover {
                    background-color: #4b4b4b;
                }
            """)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        # Connect buttons
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        # Modify tree widget selection mode based on radio button state
        self.folder_radio.toggled.connect(self.update_selection_mode)
        self.asset_radio.toggled.connect(self.update_selection_mode)
        
        # Set initial selection mode
        self.update_selection_mode()

    def switch_view(self):
        """Switch between folder and asset view based on radio selection."""
        self.tree.clear()
        if self.folder_radio.isChecked():
            self.populate_folders()
        else:
            self.populate_assets()

    def populate_folders(self):
        """Populate the tree with folder hierarchy."""
        tree_dict = {}
        for folder_path in self.available_folders:
            # Clean path to start from Mocap
            clean_path = folder_path
            if "Mocap" in clean_path:
                mocap_index = clean_path.find("Mocap")
                clean_path = clean_path[mocap_index:]
            
            parts = clean_path.strip('/').split('/')
            current_dict = tree_dict
            current_path = []
            for part in parts:
                current_path.append(part)
                if '/'.join(current_path) not in current_dict:
                    current_dict['/'.join(current_path)] = {}
                current_dict = current_dict['/'.join(current_path)]
        
        self._create_tree_items(tree_dict, self.tree, is_folder=True)

    def populate_assets(self):
        """Populate the tree with capture data assets."""
        tree_dict = {}
        for asset in self.capture_data_assets:
            if not asset:
                continue
            path = str(asset.package_path)
            
            # Clean path to start from Mocap
            if "Mocap" in path:
                mocap_index = path.find("Mocap")
                path = path[mocap_index:]
            
            parts = path.strip('/').split('/')
            current_dict = tree_dict
            current_path = []
            for part in parts:
                current_path.append(part)
                path_key = '/'.join(current_path)
                if path_key not in current_dict:
                    current_dict[path_key] = {'__assets__': []}
                current_dict = current_dict[path_key]
            current_dict['__assets__'].append(asset)
        
        self._create_tree_items(tree_dict, self.tree, is_folder=False)

    def _create_tree_items(self, tree_dict, parent_item, is_folder):
        """Recursively create tree items from dictionary."""
        sorted_items = []
        
        for path, content in tree_dict.items():
            if path == '__assets__':
                # Sort assets by their display names
                sorted_assets = sorted(content, key=lambda x: str(x.asset_name).lower())
                for asset in sorted_assets:
                    display_name = str(asset.asset_name)
                    # Clean display name if needed
                    if "Mocap" in display_name:
                        mocap_index = display_name.find("Mocap")
                        display_name = display_name[mocap_index:]
                    sorted_items.append(('asset', display_name, asset))
            else:
                # For folders, just use the last part of the path
                display_name = path.split('/')[-1]
                sorted_items.append(('folder', display_name, (path, content)))
        
        # Sort all items alphabetically by their display names
        sorted_items.sort(key=lambda x: x[1].lower())
        
        # Create tree items in sorted order
        for item_type, display_name, data in sorted_items:
            if item_type == 'asset':
                item = QtWidgets.QTreeWidgetItem([display_name])
                item.setData(0, QtCore.Qt.UserRole, data)
            else:
                path, content = data
                item = QtWidgets.QTreeWidgetItem([display_name])
                if is_folder:
                    item.setData(0, QtCore.Qt.UserRole, path)
            
            if isinstance(parent_item, QtWidgets.QTreeWidget):
                parent_item.addTopLevelItem(item)
            else:
                parent_item.addChild(item)
            
            if item_type == 'folder' and content:
                self._create_tree_items(content, item, is_folder)

    def filter_tree(self, filter_text):
        """Filter the tree based on search text."""
        def filter_item(item, text):
            if text.lower() in item.text(0).lower():
                item.setHidden(False)
                parent = item.parent()
                while parent:
                    parent.setHidden(False)
                    parent = parent.parent()
                return True
            
            child_match = False
            for i in range(item.childCount()):
                if filter_item(item.child(i), text):
                    child_match = True
            
            item.setHidden(not child_match)
            return child_match

        for i in range(self.tree.topLevelItemCount()):
            filter_item(self.tree.topLevelItem(i), filter_text)

    def get_selected_items(self):
        """Return selected folders or assets based on current mode."""
        selected_items = self.tree.selectedItems()
        if not selected_items:
            return None
        
        if self.folder_radio.isChecked():
            # For folders, return only the first selected item
            item = selected_items[0]
            return {
                'type': 'folder',
                'data': [item.data(0, QtCore.Qt.UserRole)]
            }
        else:
            # For assets, return all selected items
            return {
                'type': 'asset',
                'data': [item.data(0, QtCore.Qt.UserRole) for item in selected_items]
            }

    def update_selection_mode(self):
        """Update tree selection mode based on current radio button state"""
        if self.folder_radio.isChecked():
            self.tree.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        else:
            self.tree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

class BatchProcessorUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.processor = BatchProcessor()
        self.progress_dialog = None
        self.show_selection_dialog()

    def show_selection_dialog(self):
        """Show unified selection dialog immediately."""
        try:
            available_folders = self.processor.asset_processor.get_available_folders()
            capture_data_assets = self.processor.asset_processor.get_all_capture_data_assets()
            
            if not available_folders and not capture_data_assets:
                QtWidgets.QMessageBox.warning(self, "No Items", "No folders or capture data assets were found.")
                return

            dialog = UnifiedSelectionDialog(available_folders, capture_data_assets, self)
            
            if dialog.exec_():
                selected_items = dialog.get_selected_items()
                if selected_items:
                    self.confirm_and_start_processing(selected_items['data'], is_folder=(selected_items['type'] == 'folder'))
                else:
                    QtWidgets.QMessageBox.warning(self, "No Selection", "Please select items to process.")
        except Exception as e:
            logger.error(f"Error in item selection: {str(e)}")
            QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred while selecting items: {str(e)}")

    def confirm_and_start_processing(self, selections, is_folder):
        selection_type = "folders" if is_folder else "capture data assets"
        reply = QtWidgets.QMessageBox.question(self, 'Start Batch Process',
                                               f"Are you sure you want to start batch processing for {len(selections)} {selection_type}?",
                                               QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.start_processing(selections, is_folder)

    def start_processing(self, selections, is_folder):
        # Create new progress dialog for each batch with the actor mapping
        self.progress_dialog = ProgressDialog(
            self, 
            actor_character_mapping=self.processor.asset_processor.actor_character_mapping
        )
        self.progress_dialog.show()

        # Clear any existing connections
        try:
            self.processor.progress_updated.disconnect()
            self.processor.processing_finished.disconnect()
            self.processor.error_occurred.disconnect()
        except:
            pass

        # Connect signals
        self.processor.progress_updated.connect(self.update_progress)
        self.processor.processing_finished.connect(self.on_processing_finished)
        self.processor.error_occurred.connect(self.show_error_dialog)
        
        # Prepare the progress dialog items
        total_assets = []
        
        if is_folder:
            logger.info(f"Processing folders: {selections}")
            for folder in selections:
                logger.info(f"Getting assets from folder: {folder}")
                try:
                    # Ensure we're using the full game path
                    folder_path = str(folder)
                    if "Mocap" in folder_path:
                        mocap_index = folder_path.find("Mocap")
                        folder_path = "/Game/01_ASSETS/External/" + folder_path[mocap_index:]
                    
                    logger.info(f"Searching in path: {folder_path}")
                    
                    # Get all assets in the folder
                    assets = unreal.EditorAssetLibrary.list_assets(folder_path, recursive=True)
                    logger.info(f"Found {len(assets)} total assets in folder")
                    
                    # Filter for FootageCaptureData assets
                    for asset_path in assets:
                        try:
                            asset = unreal.load_asset(asset_path)
                            if asset and asset.get_class().get_name() == "FootageCaptureData":
                                # Create a wrapper object that matches the expected interface
                                class AssetWrapper:
                                    def __init__(self, asset, path):
                                        self.asset = asset
                                        self.package_name = path
                                        self.asset_name = asset.get_name()
                                        self.package_path = '/'.join(path.split('/')[:-1])
                                    
                                    def get_name(self):
                                        return self.asset_name

                                wrapped_asset = AssetWrapper(asset, asset_path)
                                total_assets.append(wrapped_asset)
                                
                                # Get clean folder name for display
                                display_folder = folder_path
                                if "Mocap" in display_folder:
                                    mocap_index = display_folder.find("Mocap")
                                    display_folder = display_folder[mocap_index:]
                                self.progress_dialog.add_item(display_folder, asset.get_name())
                                logger.info(f"Added asset {asset.get_name()} from {display_folder}")
                        except Exception as asset_e:
                            logger.error(f"Error processing asset {asset_path}: {str(asset_e)}")
                            continue
                
                except Exception as e:
                    logger.error(f"Error processing folder {folder}: {str(e)}")
                    continue

        else:
            total_assets = []
            for asset in selections:
                if asset is None:
                    logger.warning("Skipping None asset in selections")
                    continue
                    
                try:
                    # Verify asset has required attributes
                    asset_name = str(asset.asset_name) if hasattr(asset, 'asset_name') else str(asset.get_name())
                    package_path = str(asset.package_path) if hasattr(asset, 'package_path') else str(asset.get_path_name())
                    
                    if not asset_name or not package_path:
                        logger.error(f"Invalid asset found - Name: {asset_name}, Path: {package_path}")
                        continue
                        
                    total_assets.append(asset)
                    self.progress_dialog.add_item(package_path, asset_name)
                    logger.info(f"Added individual asset {asset_name} to progress dialog")
                except Exception as e:
                    logger.error(f"Error processing individual asset: {str(e)}")
                    continue

        # Update the total count in the progress dialog
        total_count = len(total_assets)
        logger.info(f"Total assets to process: {total_count}")
        
        if total_count == 0:
            error_msg = "No assets found in selected folders."
            logger.error(error_msg)
            QtWidgets.QMessageBox.warning(self, "No Assets", error_msg)
            self.progress_dialog.close()
            return

        # Start processing with the collected assets
        QtCore.QTimer.singleShot(0, lambda: self.processor.run_batch_process(total_assets, False))

    def update_progress(self, index, status, error="", progress_type='processing'):
        if self.progress_dialog:
            self.progress_dialog.update_item_progress(index, status, error, progress_type)
            logger.info(f"Progress updated - Index: {index}, Status: {status}, Type: {progress_type}")

    def on_processing_finished(self):
        # Remove the popup message and replace with bold log entry
        if self.progress_dialog:
            self.progress_dialog.log_text.append("<b>Batch processing has finished.</b>")
            logger.info("Batch processing has finished.")

    def show_error_dialog(self, error_message):
        QtWidgets.QMessageBox.critical(self, "Error", error_message)

    def update_log_level(self, level):
        logging.getLogger().setLevel(level)

    def show_help(self):
        help_text = """
        Batch Processor Help:
        
        1. Select Folders: Choose the folders containing assets to process.
        2. Select Capture Data: Choose individual capture data assets to process.
        3. Log Level: Choose the verbosity of logging.
        4. Progress Dialog: Shows processing progress and allows cancellation.
        5. Save Log: Export the processing log for troubleshooting.
        
        For more information, please refer to the user manual.
        """
        QtWidgets.QMessageBox.information(self, "Help", help_text)

    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self, 'Exit',
                                               "Are you sure you want to exit?",
                                               QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            # Comment out cancel processing call
            # self.processor.cancel_processing()
            event.accept()
        else:
            event.ignore()

class ProcessingDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ProcessingDialog, self).__init__(parent)
        self.setWindowTitle("Processing")
        self.setModal(True)
        self.setMinimumWidth(300)
        self.is_processing = True
        
        # Create layout
        layout = QtWidgets.QVBoxLayout(self)
        
        # Add progress label
        self.progress_label = QtWidgets.QLabel("Processing...")
        layout.addWidget(self.progress_label)
        
        # Add progress bar
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        layout.addWidget(self.progress_bar)
        
        # Style the dialog
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
                color: #ffffff;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 10px;
                margin: 0.5px;
            }
        """)

    def closeEvent(self, event):
        """Override close event to prevent premature closing"""
        if self.is_processing:
            # If processing is ongoing, show confirmation dialog
            reply = QtWidgets.QMessageBox.question(
                self,
                'Confirm Exit',
                'Processing is still in progress. Are you sure you want to cancel?',
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No
            )
            
            if reply == QtWidgets.QMessageBox.Yes:
                event.accept()
            else:
                # User decided to continue processing
                event.ignore()
        else:
            # If not processing, allow normal close
            event.accept()

    def update_progress(self, message, status):
        """Update progress status and handle completion"""
        self.progress_label.setText(message)
        
        if status == 'complete':
            self.is_processing = False
            self.accept()  # Close dialog when complete
        elif status == 'failed':
            self.is_processing = False
            self.reject()  # Close dialog on failure
        else:
            self.is_processing = True
            
    def closeEvent(self, event):
        """Override close event to prevent premature closing"""
        if self.is_processing:
            # If processing is ongoing, show confirmation dialog
            reply = QtWidgets.QMessageBox.question(
                self,
                'Confirm Exit',
                'Processing is still in progress. Are you sure you want to cancel?',
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No
            )
            
            if reply == QtWidgets.QMessageBox.Yes:
                # Comment out cancelled flag
                # self.cancelled = True
                event.accept()
            else:
                # User decided to continue processing
                event.ignore()
        else:
            # If not processing, allow normal close
            event.accept()

    def update_progress(self, message, status):
        """Update progress status and handle completion"""
        self.progress_label.setText(message)
        
        if status == 'complete':
            self.is_processing = False
            self.accept()  # Close dialog when complete
        elif status == 'failed':
            self.is_processing = False
            self.reject()  # Close dialog on failure
        else:
            self.is_processing = True

def run():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)

    # Create and show the selection dialog directly
    global ui
    ui = BatchProcessorUI()

    # Define the tick function
    def tick(delta_time):
        app.processEvents()
        return True

    # Keep global references
    global tick_handle
    tick_handle = unreal.register_slate_post_tick_callback(tick)

    class KeepAlive:
        pass

    global keep_alive
    keep_alive = KeepAlive()
    keep_alive.ui = ui
    keep_alive.tick_handle = tick_handle


if __name__ == "__main__":
    run()
