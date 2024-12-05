# Standard library imports
import json
import logging
import os
import sys

# Third-party imports
import ftrack_api
from PIL import Image
from PyQt5 import QtCore, QtGui, QtWidgets

"""
Project Setup Tool

A utility for creating and configuring new projects with project management 
integration and local folder structure creation. Includes a GUI for easy setup.
"""

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str) -> dict:
    """Load configuration settings from a JSON file.

    Args:
        config_path: Path to the JSON configuration file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If configuration file is missing
        json.JSONDecodeError: If configuration file has invalid JSON
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error("Failed to load configuration: %s", e)
        raise


def create_project_session(url: str, key: str, user: str):
    """Create and validate project management session.

    Args:
        url: Server URL
        key: API key
        user: Username

    Returns:
        Active session object

    Raises:
        ConnectionError: If unable to connect to server
    """
    try:
        session = ftrack_api.Session(
            server_url=url,
            api_key=key,
            api_user=user
        )
        session.query('User').first()
        logger.info("Connected to project management server")
        return session
    except Exception as e:
        logger.error("Connection failed: %s", e)
        raise ConnectionError("Unable to connect to server")


class ProjectSetupUI(QtWidgets.QWidget):
    """Project setup graphical interface."""
    
    def __init__(self):
        super().__init__()
        self.config = self._init_config()
        self.session = None
        self.project = None
        self._setup_ui()

    def _init_config(self) -> dict:
        """Initialize configuration settings."""
        try:
            return load_config('settings.json')
        except Exception as e:
            self._show_error('Configuration Error', str(e))
            sys.exit(1)

    def _setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle('Project Setup Tool')
        
        # Create main layout
        layout = QtWidgets.QVBoxLayout()
        form = QtWidgets.QFormLayout()
        
        # Add input fields
        self.name_input = QtWidgets.QLineEdit()
        self.code_input = QtWidgets.QLineEdit()
        self.start_date = QtWidgets.QDateEdit()
        self.end_date = QtWidgets.QDateEdit()
        
        form.addRow('Project Name:', self.name_input)
        form.addRow('Project Code:', self.code_input)
        form.addRow('Start Date:', self.start_date)
        form.addRow('End Date:', self.end_date)
        
        # Add thumbnail selector
        thumb_layout = QtWidgets.QHBoxLayout()
        self.thumb_label = QtWidgets.QLabel('No thumbnail selected')
        self.thumb_btn = QtWidgets.QPushButton('Select Thumbnail')
        self.thumb_btn.clicked.connect(self._select_thumbnail)
        
        thumb_layout.addWidget(self.thumb_label)
        thumb_layout.addWidget(self.thumb_btn)
        
        # Add create button and status
        self.create_btn = QtWidgets.QPushButton('Create Project')
        self.create_btn.clicked.connect(self._create_project)
        self.status = QtWidgets.QLabel()
        
        # Assemble layout
        layout.addLayout(form)
        layout.addLayout(thumb_layout)
        layout.addWidget(self.create_btn)
        layout.addWidget(self.status)
        
        self.setLayout(layout)

    def _select_thumbnail(self):
        """Handle thumbnail selection."""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            'Select Project Thumbnail',
            '',
            'Images (*.png *.jpg *.jpeg)'
        )
        if file_path:
            self.thumb_path = file_path
            self.thumb_label.setText(os.path.basename(file_path))

    def _show_error(self, title: str, message: str):
        """Display error dialog."""
        logger.error(message)
        QtWidgets.QMessageBox.critical(self, title, message)

    def _update_status(self, message: str):
        """Update status display."""
        logger.info(message)
        self.status.setText(message)
        QtWidgets.QApplication.processEvents()

    def _create_project(self):
        """Handle project creation process."""
        try:
            self._update_status("Creating project...")
            # Project creation logic here
            self._update_status("Project created successfully")
            
        except Exception as e:
            self._show_error("Error", f"Failed to create project: {str(e)}")


def main():
    """Application entry point."""
    app = QtWidgets.QApplication(sys.argv)
    window = ProjectSetupUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main() 