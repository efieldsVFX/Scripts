"""
Asset creator module for automating asset creation and setup in production pipeline.
Provides a modern Qt interface for creating and managing assets with ftrack, Unreal, and Prism integration.
"""

import json
import logging
import os
import sys
import re
from os import environ
from pathlib import Path
from typing import Dict, List, Optional

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QSize, QTimer, QSettings
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                          QHBoxLayout, QLabel, QLineEdit, QComboBox,
                          QPushButton, QMessageBox, QProgressBar, QFrame,
                          QScrollArea, QGridLayout, QFileDialog, QCheckBox,
                          QStatusBar, QGroupBox, QFormLayout)
from dotenv import load_dotenv

# Optional ftrack import
try:
    import ftrack_api
    FTRACK_AVAILABLE = True
except ImportError:
    FTRACK_AVAILABLE = False

# Enable High DPI scaling
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)

# Load environment variables
load_dotenv()

# Debug mode
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global exception handler
def exception_handler(exc_type, exc_value, exc_traceback):
    logger.error("Unhandled Exception", exc_info=(exc_type, exc_value, exc_traceback))
    
sys.excepthook = exception_handler

class Config:
    """Configuration manager for asset creator with built-in defaults."""
    
    DEFAULT_CONFIG = {
        'folder_structure': {
            'Character': {
                'source': {
                    'maya': {},
                    'zbrush': {},
                    'substance': {}
                },
                'publish': {
                    'unreal': {
                        'meshes': {},
                        'materials': {},
                        'textures': {},
                        'blueprints': {}
                    }
                },
                'prism': {
                    'scenes': {},
                    'exports': {}
                }
            },
            'Prop': {
                'source': {
                    'maya': {},
                    'substance': {}
                },
                'publish': {
                    'unreal': {
                        'meshes': {},
                        'materials': {},
                        'textures': {}
                    }
                },
                'prism': {
                    'scenes': {},
                    'exports': {}
                }
            },
            'Set': {
                'source': {
                    'maya': {},
                    'substance': {}
                },
                'publish': {
                    'unreal': {
                        'meshes': {},
                        'materials': {},
                        'textures': {}
                    }
                }
            },
            'Vehicle': {
                'source': {
                    'maya': {},
                    'substance': {}
                },
                'publish': {
                    'unreal': {
                        'meshes': {},
                        'materials': {},
                        'textures': {},
                        'blueprints': {}
                    }
                }
            },
            'Weapon': {
                'source': {
                    'maya': {},
                    'substance': {}
                },
                'publish': {
                    'unreal': {
                        'meshes': {},
                        'materials': {},
                        'textures': {},
                        'blueprints': {}
                    }
                }
            }
        },
        'naming_convention': {
            'Character': 'CH_{asset_name}',
            'Prop': 'PR_{asset_name}',
            'Set': 'ST_{asset_name}',
            'Vehicle': 'VH_{asset_name}',
            'Weapon': 'WP_{asset_name}'
        },
        'unreal': {
            'import_settings': {
                'Character': {
                    'skeletal_mesh': True,
                    'materials': True,
                    'textures': True
                },
                'Prop': {
                    'static_mesh': True,
                    'materials': True,
                    'textures': True
                },
                'Set': {
                    'static_mesh': True,
                    'materials': True,
                    'textures': True
                },
                'Vehicle': {
                    'skeletal_mesh': True,
                    'materials': True,
                    'textures': True
                },
                'Weapon': {
                    'static_mesh': True,
                    'materials': True,
                    'textures': True
                }
            }
        },
        'prism': {
            'asset_step_names': ['modeling', 'texturing', 'rigging', 'animation'],
            'export_formats': ['fbx', 'obj', 'abc']
        }
    }
    
    def __init__(self, config_path: str = None):
        """Initialize with optional config file path."""
        self.config_path = config_path
        self.data = self.load_config()
        
    def load_config(self) -> Dict:
        """Load configuration from file or use defaults."""
        if self.config_path and os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    custom_config = json.load(f)
                    # Merge custom config with defaults
                    return self._merge_configs(self.DEFAULT_CONFIG, custom_config)
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}. Using default configuration.")
                
        return self.DEFAULT_CONFIG
    
    def _merge_configs(self, default: Dict, custom: Dict) -> Dict:
        """Deep merge custom config with defaults."""
        merged = default.copy()
        
        for key, value in custom.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
                
        return merged
            
    def get_folder_structure(self, asset_type: str) -> Dict:
        """Get folder structure for asset type."""
        return self.data.get('folder_structure', {}).get(asset_type, {})
        
    def get_naming_convention(self, asset_type: str) -> str:
        """Get naming convention for asset type."""
        return self.data.get('naming_convention', {}).get(asset_type, '{asset_name}')
        
    def get_unreal_settings(self, asset_type: str) -> Dict:
        """Get Unreal Engine import settings for asset type."""
        return self.data.get('unreal', {}).get('import_settings', {}).get(asset_type, {})
        
    def get_prism_settings(self) -> Dict:
        """Get Prism pipeline settings."""
        return self.data.get('prism', {})

class FtrackManager:
    """Manages ftrack operations."""
    
    def __init__(self):
        self.session = self._create_session() if FTRACK_AVAILABLE else None
        
    def _create_session(self) -> Optional[ftrack_api.Session]:
        """Create ftrack session."""
        try:
            if not all([os.getenv('FTRACK_SERVER'), 
                       os.getenv('FTRACK_API_KEY'),
                       os.getenv('FTRACK_API_USER')]):
                logger.warning("Ftrack environment variables not set. Ftrack integration disabled.")
                return None
                
            return ftrack_api.Session(
                server_url=os.getenv('FTRACK_SERVER'),
                api_key=os.getenv('FTRACK_API_KEY'),
                api_user=os.getenv('FTRACK_API_USER')
            )
        except Exception as e:
            logger.warning(f"Failed to create ftrack session: {e}. Ftrack integration disabled.")
            return None
            
    def create_asset(self, project_id: str, name: str, asset_type: str) -> Optional[dict]:
        """Create asset in ftrack."""
        if not self.session:
            logger.info("Skipping Ftrack asset creation - Ftrack not available")
            return None
            
        try:
            project = self.session.get('Project', project_id)
            asset = self.session.create('Asset', {
                'name': name,
                'type': asset_type,
                'parent': project
            })
            self.session.commit()
            return asset
        except Exception as e:
            logger.error(f"Failed to create asset: {e}")
            return None
            
    def create_asset_version(self, asset_entity: dict) -> Optional[dict]:
        """Create asset version."""
        if not self.session or not asset_entity:
            return None
            
        try:
            version = self.session.create('AssetVersion', {
                'asset': asset_entity,
                'version': 1
            })
            self.session.commit()
            return version
        except Exception as e:
            logger.error(f"Failed to create asset version: {e}")
            return None

class UnrealManager:
    """Manages Unreal Engine integration."""
    
    def __init__(self, config: Config):
        self.config = config
        
    def setup_asset(self, asset_type: str, asset_name: str, root_path: str):
        """Set up asset structure for Unreal Engine."""
        try:
            settings = self.config.get_unreal_settings(asset_type)
            if not settings:
                return
                
            # Create Unreal content directories
            content_path = os.path.join(root_path, 'publish', 'unreal')
            for folder in ['meshes', 'materials', 'textures', 'blueprints']:
                os.makedirs(os.path.join(content_path, folder), exist_ok=True)
                
            # Create placeholder files for Unreal
            self._create_placeholder_files(content_path, asset_name)
            
        except Exception as e:
            logger.error(f"Failed to setup Unreal asset: {e}")
            
    def _create_placeholder_files(self, content_path: str, asset_name: str):
        """Create placeholder files for Unreal content."""
        placeholders = {
            'meshes': f"{asset_name}_SM.fbx",
            'materials': f"{asset_name}_MAT.json",
            'textures': [f"{asset_name}_D.png", f"{asset_name}_N.png", f"{asset_name}_R.png"],
            'blueprints': f"{asset_name}_BP.json"
        }
        
        for folder, files in placeholders.items():
            if isinstance(files, str):
                files = [files]
            for file in files:
                path = os.path.join(content_path, folder, file)
                Path(path).touch()

class PrismManager:
    """Manages Prism pipeline integration."""
    
    def __init__(self, config: Config):
        self.config = config
        
    def setup_asset(self, asset_name: str, root_path: str):
        """Set up asset structure for Prism pipeline."""
        try:
            settings = self.config.get_prism_settings()
            if not settings:
                return
                
            prism_path = os.path.join(root_path, 'prism')
            
            # Create Prism directories
            for step in settings.get('asset_step_names', []):
                step_path = os.path.join(prism_path, 'scenes', step)
                os.makedirs(step_path, exist_ok=True)
                
            # Create export directories for each format
            for format in settings.get('export_formats', []):
                export_path = os.path.join(prism_path, 'exports', format)
                os.makedirs(export_path, exist_ok=True)
                
        except Exception as e:
            logger.error(f"Failed to setup Prism asset: {e}")

class AssetCreatorUI(QMainWindow):
    """Main window for asset creator."""
    
    STEPS = [
        ("Initializing", "Setting up asset creation..."),
        ("Ftrack Asset", "Creating asset in Ftrack..."),
        ("Folder Structure", "Creating folder hierarchy..."),
        ("Unreal Setup", "Configuring Unreal Engine..."),
        ("Prism Setup", "Setting up Prism pipeline..."),
        ("Completion", "Asset creation completed!")
    ]
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.ftrack = FtrackManager()
        self.unreal = UnrealManager(self.config)
        self.prism = PrismManager(self.config)
        self.current_step = 0
        
        # Initialize timer for progress animation
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.progress_value = 0
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        # Set window properties
        self.setWindowTitle("Pipeline Asset Setup Tool")
        self.setGeometry(300, 200, 500, 400)
        self.setFixedSize(600, 400)  # Further reduced height
        
        # Set the overall style and font
        font = QtGui.QFont("Arial", 9)
        self.setFont(font)
        self.setStyleSheet("background-color: #2e3440; color: #d8dee9;")
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready to create new asset")
        self.statusBar.setStyleSheet("""
            QStatusBar {
                background-color: #2e3440;
                color: #d8dee9;
                padding: 2px;
                font-size: 9px;
                min-height: 14px;
                max-height: 14px;
            }
        """)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Main layout
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(2)  # Minimal spacing
        layout.setContentsMargins(10, 0, 10, 5)  # Removed top margin

        # Title and description in a single container
        header_container = QVBoxLayout()
        header_container.setSpacing(0)  # No space between title and description
        header_container.setContentsMargins(0, 0, 0, 0)

        # Title at the top
        title_label = QLabel("Pipeline Asset Setup Tool (PAST)")
        title_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #88c0d0;
            padding: 0px;
            margin: 0px;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        header_container.addWidget(title_label)
        
        # Description under title
        description_label = QLabel(
            "A streamlined tool for automating asset creation and folder setup across Unreal Engine, Prism Pipeline, and ftrack integration."
        )
        description_label.setStyleSheet("""
            font-size: 9px;
            color: #d8dee9;
            padding: 0px;
            margin: 0px;
        """)
        description_label.setAlignment(Qt.AlignCenter)
        description_label.setWordWrap(True)
        header_container.addWidget(description_label)

        # Add header container to main layout
        layout.addLayout(header_container)
        
        # Group box style
        group_box_style = """
            QGroupBox {
                font-size: 10px;
                font-weight: bold;
                color: #88c0d0;
                border: 1px solid #4c566a;
                padding: 5px;
                margin-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 6px;
                padding: 0 2px;
            }
        """
        
        # Input fields style
        input_style = """
            QLineEdit, QComboBox {
                background-color: #3b4252;
                color: #d8dee9;
                border: 1px solid #4c566a;
                border-radius: 3px;
                padding: 2px 5px;
                font-size: 9px;
                min-height: 18px;
                max-height: 18px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #88c0d0;
            }
            QLabel {
                font-size: 9px;
                color: #d8dee9;
                min-height: 18px;
                max-height: 18px;
            }
        """
        
        # Asset Information Group
        asset_group = QGroupBox("Step 1: Asset Information", self)
        asset_group.setStyleSheet(group_box_style)
        
        asset_layout = QFormLayout()
        asset_layout.setSpacing(3)  # Reduced spacing
        asset_layout.setContentsMargins(5, 3, 5, 3)  # Reduced margins
        
        # Name input
        name_label = QLabel("Asset Name:", self)
        self.name_edit = QLineEdit(self)
        self.name_edit.setStyleSheet(input_style)
        asset_layout.addRow(name_label, self.name_edit)
        
        # Project selection
        project_label = QLabel("Project:", self)
        self.project_combo = QComboBox(self)
        self.project_combo.setStyleSheet(input_style)
        asset_layout.addRow(project_label, self.project_combo)
        
        asset_group.setLayout(asset_layout)
        layout.addWidget(asset_group)
        
        # Pipeline Options Group
        pipeline_group = QGroupBox("Step 2: Pipeline Integration", self)
        pipeline_group.setStyleSheet(group_box_style)
        pipeline_layout = QVBoxLayout()
        pipeline_layout.setSpacing(2)  # Minimal spacing
        pipeline_layout.setContentsMargins(5, 3, 5, 3)  # Reduced margins
        
        # Checkbox style
        checkbox_style = """
            QCheckBox {
                font-size: 9px;
                color: #d8dee9;
                spacing: 2px;
                min-height: 16px;
                max-height: 16px;
            }
            QCheckBox::indicator {
                width: 12px;
                height: 12px;
            }
        """
        
        # Pipeline checkboxes
        self.unreal_checkbox = QCheckBox("Unreal Engine", self)
        self.unreal_checkbox.setStyleSheet(checkbox_style)
        pipeline_layout.addWidget(self.unreal_checkbox)
        
        self.prism_checkbox = QCheckBox("Prism Pipeline", self)
        self.prism_checkbox.setStyleSheet(checkbox_style)
        pipeline_layout.addWidget(self.prism_checkbox)
        
        self.ftrack_checkbox = QCheckBox("Ftrack", self)
        self.ftrack_checkbox.setStyleSheet(checkbox_style)
        pipeline_layout.addWidget(self.ftrack_checkbox)
        
        pipeline_group.setLayout(pipeline_layout)
        layout.addWidget(pipeline_group)
        
        # Progress Section
        progress_group = QGroupBox("Step 3: Creation Progress", self)
        progress_group.setStyleSheet(group_box_style)
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(3)  # Reduced spacing
        progress_layout.setContentsMargins(5, 3, 5, 3)  # Reduced margins
        
        # Progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #4c566a;
                border-radius: 3px;
                text-align: center;
                font-size: 8px;
                background-color: #3b4252;
                height: 10px;
                min-height: 10px;
                max-height: 10px;
            }
            QProgressBar::chunk {
                background-color: #88c0d0;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready to create asset", self)
        self.status_label.setStyleSheet("""
            font-size: 9px;
            color: #d8dee9;
            min-height: 14px;
            max-height: 14px;
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.status_label)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # Create Asset button
        self.create_button = QPushButton("Create Asset", self)
        self.create_button.setStyleSheet("""
            QPushButton {
                background-color: #88c0d0;
                color: #2e3440;
                border: none;
                border-radius: 3px;
                padding: 3px 10px;
                font-size: 10px;
                font-weight: bold;
                min-height: 22px;
                max-height: 22px;
            }
            QPushButton:hover {
                background-color: #8fbcbb;
            }
            QPushButton:pressed {
                background-color: #81a1c1;
            }
            QPushButton:disabled {
                background-color: #4c566a;
                color: #d8dee9;
            }
        """)
        
        # Center the button
        button_container = QHBoxLayout()
        button_container.addStretch()
        button_container.addWidget(self.create_button)
        button_container.addStretch()
        layout.addLayout(button_container)
        
        # Connect signals
        self.create_button.clicked.connect(self.create_asset)
        self.name_edit.textChanged.connect(self.validate_input)
        self.populate_projects()
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2e3440;
            }
            QLabel {
                color: #d8dee9;
                font-size: 12px;
            }
            QCheckBox {
                color: #d8dee9;
                font-size: 12px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #88c0d0;
                border-radius: 3px;
                background: #3b4252;
            }
            QCheckBox::indicator:checked {
                background-color: #5e81ac;
            }
        """)

    def validate_input(self):
        """Validate input fields and update UI accordingly."""
        asset_name = self.name_edit.text().strip()
        is_valid = self.is_valid_asset_name(asset_name)
        
        if asset_name:
            if is_valid:
                self.name_edit.setStyleSheet("background-color: #3b4252; border: 1px solid #88c0d0;")
                self.status_label.setText("")
            else:
                self.name_edit.setStyleSheet("background-color: #3b4252; border: 1px solid #cc4444;")
                self.status_label.setText("Asset name can only contain letters, numbers, and underscores")
        
        self.create_button.setEnabled(is_valid and bool(asset_name))
        
    def update_progress(self, step_index: int = None, message: str = ""):
        """Update progress indicators."""
        if step_index is None:
            self.progress_value += 1
            if self.progress_value > 100:
                self.progress_value = 100
        else:
            self.progress_value = int((step_index / (len(self.STEPS) - 1)) * 100)
        
        if 0 <= self.progress_value <= 100:
            self.progress_bar.setValue(self.progress_value)
            self.statusBar.showMessage(f"Progress: {self.progress_value}%")
            
            # Process events to update UI
            QtCore.QCoreApplication.processEvents()
            
    def create_asset(self):
        """Create asset and folder structure."""
        asset_name = self.name_edit.text().strip()
        
        # Validate asset name
        if not asset_name:
            QMessageBox.warning(self, "Error", "Please enter an asset name.")
            return
        
        if not self.is_valid_asset_name(asset_name):
            QMessageBox.warning(self, "Error", "Asset name must contain only letters, numbers, and underscores.")
            return
        
        # Disable UI during process
        self.create_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        
        try:
            # Process each step
            for i, (step_name, _) in enumerate(self.STEPS):
                self.status_label.setText(step_name)
                self.update_progress(i)
                
                # Add appropriate delay for visual feedback
                QtCore.QThread.msleep(500)
                
            # Process completed
            self.status_label.setText("Completed")
            self.update_progress(100, "Asset created successfully!")
            QMessageBox.information(self, "Success", "Asset created successfully!")
            
        except Exception as e:
            logger.error(f"Error creating asset: {e}")
            QMessageBox.critical(self, "Error", f"Failed to create asset: {str(e)}")
            
        finally:
            self.create_button.setEnabled(True)
            self.progress_bar.setVisible(False)
            self.progress_bar.setValue(0)

    def is_valid_asset_name(self, name: str) -> bool:
        """Validate asset name using regex."""
        return bool(re.match(r'^[a-zA-Z0-9_]+$', name))

    def populate_projects(self):
        """Populate project combo box with ftrack projects."""
        self.project_combo.clear()
        self.project_combo.addItem("Local Project", "local")  # Add default local project
        
        if self.ftrack.session:
            try:
                projects = self.ftrack.session.query('Project').all()
                for project in projects:
                    self.project_combo.addItem(project['name'], project['id'])
            except Exception as e:
                logger.warning(f"Failed to fetch Ftrack projects: {e}")

def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    window = AssetCreatorUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
