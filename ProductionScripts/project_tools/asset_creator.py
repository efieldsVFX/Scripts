"""
Asset creator module for automating asset creation and setup in production pipeline.
Provides a modern Qt interface for creating and managing assets with ftrack, Unreal, and Prism integration.
"""

import json
import logging
import os
import sys
from os import environ
from pathlib import Path
from typing import Dict, List, Optional

import ftrack_api
import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                          QHBoxLayout, QLabel, QLineEdit, QComboBox,
                          QPushButton, QMessageBox, QProgressBar, QFrame,
                          QScrollArea, QGridLayout, QFileDialog, QCheckBox)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
ASSET_CATEGORIES = ['Character', 'Prop', 'Set', 'Vehicle', 'Weapon']
STYLE_SHEET = '''
QMainWindow {
    background-color: #2b2b2b;
}
QLabel {
    color: #ffffff;
    font-size: 12px;
}
QLineEdit, QComboBox {
    background-color: #3b3b3b;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 5px;
    color: #ffffff;
    font-size: 12px;
}
QPushButton {
    background-color: #0d6efd;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-size: 12px;
}
QPushButton:hover {
    background-color: #0b5ed7;
}
QPushButton:pressed {
    background-color: #0a58ca;
}
QProgressBar {
    border: 1px solid #555555;
    border-radius: 4px;
    text-align: center;
    color: white;
}
QProgressBar::chunk {
    background-color: #0d6efd;
    border-radius: 3px;
}
QCheckBox {
    color: #ffffff;
}
QCheckBox::indicator {
    width: 15px;
    height: 15px;
    background-color: #3b3b3b;
    border: 1px solid #555555;
    border-radius: 3px;
}
QCheckBox::indicator:checked {
    background-color: #0d6efd;
}
'''

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Config:
    """Configuration manager for asset creator."""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.data = self.load_config()
        
    def load_config(self) -> Dict:
        """Load configuration from JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
            
    def get_folder_structure(self, asset_type: str) -> Dict:
        """Get folder structure for asset type."""
        return self.data.get('folder_structure', {}).get(asset_type, {})
        
    def get_naming_convention(self, asset_type: str) -> str:
        """Get naming convention for asset type."""
        return self.data.get('naming_convention', {}).get(asset_type, '')
        
    def get_unreal_settings(self, asset_type: str) -> Dict:
        """Get Unreal Engine import settings for asset type."""
        return self.data.get('unreal', {}).get('import_settings', {}).get(asset_type, {})
        
    def get_prism_settings(self) -> Dict:
        """Get Prism pipeline settings."""
        return self.data.get('prism', {})

class FtrackManager:
    """Manages ftrack operations."""
    
    def __init__(self):
        self.session = self._create_session()
        
    def _create_session(self) -> Optional[ftrack_api.Session]:
        """Create ftrack session."""
        try:
            return ftrack_api.Session(
                server_url=os.getenv('FTRACK_SERVER'),
                api_key=os.getenv('FTRACK_API_KEY'),
                api_user=os.getenv('FTRACK_API_USER')
            )
        except Exception as e:
            logger.error(f"Failed to create ftrack session: {e}")
            return None
            
    def create_asset(self, project_id: str, name: str, asset_type: str) -> Optional[dict]:
        """Create asset in ftrack."""
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
    
    def __init__(self):
        super().__init__()
        self.config = Config('config.json')
        self.ftrack = FtrackManager()
        self.unreal = UnrealManager(self.config)
        self.prism = PrismManager(self.config)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("Asset Creator")
        self.setMinimumSize(800, 600)
        self.setStyleSheet(STYLE_SHEET)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Header
        header = QLabel("Asset Creator")
        header.setStyleSheet("font-size: 24px; color: white; padding: 20px;")
        layout.addWidget(header)
        
        # Form layout
        form = QGridLayout()
        
        # Project selection
        form.addWidget(QLabel("Project:"), 0, 0)
        self.project_combo = QComboBox()
        self.populate_projects()
        form.addWidget(self.project_combo, 0, 1)
        
        # Asset type
        form.addWidget(QLabel("Asset Type:"), 1, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItems(ASSET_CATEGORIES)
        form.addWidget(self.type_combo, 1, 1)
        
        # Asset name
        form.addWidget(QLabel("Asset Name:"), 2, 0)
        self.name_edit = QLineEdit()
        form.addWidget(self.name_edit, 2, 1)
        
        # Pipeline options
        form.addWidget(QLabel("Pipeline Options:"), 3, 0)
        pipeline_widget = QWidget()
        pipeline_layout = QHBoxLayout()
        
        self.unreal_checkbox = QCheckBox("Unreal Engine")
        self.unreal_checkbox.setChecked(True)
        pipeline_layout.addWidget(self.unreal_checkbox)
        
        self.prism_checkbox = QCheckBox("Prism Pipeline")
        self.prism_checkbox.setChecked(True)
        pipeline_layout.addWidget(self.prism_checkbox)
        
        pipeline_widget.setLayout(pipeline_layout)
        form.addWidget(pipeline_widget, 3, 1)
        
        # Add form to layout
        form_widget = QWidget()
        form_widget.setLayout(form)
        layout.addWidget(form_widget)
        
        # Create button
        self.create_button = QPushButton("Create Asset")
        self.create_button.clicked.connect(self.create_asset)
        layout.addWidget(self.create_button)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.hide()
        layout.addWidget(self.progress)
        
        # Status
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)
        
        # Add stretch to push everything up
        layout.addStretch()
        
    def populate_projects(self):
        """Populate project combo box with ftrack projects."""
        if self.ftrack.session:
            projects = self.ftrack.session.query('Project').all()
            for project in projects:
                self.project_combo.addItem(project['name'], project['id'])
                
    def create_asset(self):
        """Create asset and folder structure."""
        try:
            self.progress.show()
            self.progress.setValue(0)
            
            # Get values
            project_id = self.project_combo.currentData()
            asset_type = self.type_combo.currentText()
            asset_name = self.name_edit.text()
            
            # Validate
            if not all([project_id, asset_type, asset_name]):
                QMessageBox.warning(self, "Error", "Please fill all fields")
                return
                
            # Create in ftrack
            self.progress.setValue(20)
            asset = self.ftrack.create_asset(project_id, asset_name, asset_type)
            if not asset:
                raise Exception("Failed to create asset in ftrack")
                
            # Create folder structure
            self.progress.setValue(40)
            folder_structure = self.config.get_folder_structure(asset_type)
            root_path = self._create_folders(folder_structure, asset_name)
            
            # Setup Unreal if enabled
            if self.unreal_checkbox.isChecked():
                self.progress.setValue(60)
                self.unreal.setup_asset(asset_type, asset_name, root_path)
            
            # Setup Prism if enabled
            if self.prism_checkbox.isChecked():
                self.progress.setValue(80)
                self.prism.setup_asset(asset_name, root_path)
            
            # Create asset version
            self.progress.setValue(90)
            version = self.ftrack.create_asset_version(asset)
            
            # Complete
            self.progress.setValue(100)
            QMessageBox.information(self, "Success", 
                                  f"Asset {asset_name} created successfully!\n"
                                  f"Pipeline integrations:\n"
                                  f"- Ftrack: {'✓' if asset else '✗'}\n"
                                  f"- Unreal: {'✓' if self.unreal_checkbox.isChecked() else '−'}\n"
                                  f"- Prism: {'✓' if self.prism_checkbox.isChecked() else '−'}")
            
        except Exception as e:
            logger.error(f"Failed to create asset: {e}")
            QMessageBox.critical(self, "Error", str(e))
        finally:
            self.progress.hide()
            
    def _create_folders(self, structure: Dict, asset_name: str, parent_path: str = "") -> str:
        """Recursively create folder structure."""
        root_path = ""
        for folder, subfolders in structure.items():
            folder_path = os.path.join(parent_path, folder.format(asset_name=asset_name))
            if not root_path:
                root_path = folder_path
            os.makedirs(folder_path, exist_ok=True)
            if isinstance(subfolders, dict):
                self._create_folders(subfolders, asset_name, folder_path)
        return root_path

def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    window = AssetCreatorUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
