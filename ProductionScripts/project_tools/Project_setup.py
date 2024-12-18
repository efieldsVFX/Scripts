import sys
import os
import json
import logging
import traceback
from datetime import datetime
from PyQt5 import QtWidgets, QtGui, QtCore
from PIL import Image
import ftrack_api

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# High DPI Scaling Fix
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)

# Global Exception Handler
def handle_exception(exc_type, exc_value, exc_traceback):
    error_details = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logger.error(f"Unhandled Exception:\n{error_details}")
    QtWidgets.QMessageBox.critical(
        None, "Critical Error", f"An unexpected error occurred:\n{exc_value}"
    )
    sys.exit(1)

sys.excepthook = handle_exception

# Utility Functions
def load_config(config_path):
    try:
        with open(config_path, 'r') as config_file:
            return json.load(config_file)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return {
            "root_path": "C:/Fake/RootPath",
            "ftrack": {
                "server_url": "https://fake.ftrack.com",
                "api_key": "fake_api_key",
                "api_user": "fake_user"
            },
            "folder_structure": [
                "00_Pipeline",
                "01_ASSETS",
                "02_SCENES"
            ],
            "pipeline_data": {
                "globals": {
                    "project_name": "FakeProject",
                    "project_code": "FP001"
                },
                "prjManagement": {
                    "ftrack_projectName": "FakeProject"
                }
            }
        }
        # NOTE: Replace this fake data with an actual 'config.json' file for production use.

def save_config(config_path, config):
    try:
        with open(config_path, 'w') as config_file:
            json.dump(config, config_file, indent=4)
    except Exception as e:
        logger.error(f"Error saving config: {e}")

# Core Logic
def validate_inputs(project_name, project_code, start_date, end_date):
    if not all([project_name, project_code, start_date, end_date]):
        raise ValueError("All fields (name, code, dates) are required.")

def create_ftrack_project(project_name, project_code, start_date, end_date, config):
    try:
        session = ftrack_api.Session(
            server_url=config['server_url'],
            api_key=config['api_key'],
            api_user=config['api_user']
        )
        project = session.create('Project', {
            'name': project_name,
            'full_name': project_name,
            'name': project_code,
            'start_date': start_date,
            'end_date': end_date
        })
        session.commit()
        return project, session
    except Exception as e:
        logger.error(f"Error creating Ftrack project: {e}")
        return None, None

def setup_folder_structure(project_path, structure):
    try:
        for folder in structure:
            os.makedirs(os.path.join(project_path, folder), exist_ok=True)
        logger.info(f"Folder structure created at {project_path}")
    except Exception as e:
        logger.error(f"Error setting up folder structure: {e}")

def process_thumbnail(thumbnail_path, save_paths):
    try:
        image = Image.open(thumbnail_path) if thumbnail_path else Image.new('RGB', (512, 512), (200, 200, 200))
        image.thumbnail((512, 512), Image.Resampling.LANCZOS)
        for path in save_paths:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            image.save(path, "JPEG", quality=95)
            logger.info(f"Thumbnail saved at {path}")
    except Exception as e:
        logger.error(f"Error processing thumbnail: {e}")

# Main Application Class
class ProjectSetupApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_file_path = 'config.json'
        self.config = load_config(self.config_file_path)
        if not self.config:
            QtWidgets.QMessageBox.critical(self, 'Error', 'Failed to load configuration.')
            sys.exit(1)
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #2e3440;
                color: #d8dee9;
            }
            QLabel {
                color: #d8dee9;
                font-size: 8pt;
                padding: 0px;
                margin: 0px;
                background-color: transparent;
            }
            QGroupBox {
                border: 1px solid #4c566a;
                border-radius: 4px;
                color: #d8dee9;
                font-size: 8pt;
                font-weight: bold;
                margin-top: 8px;
                padding-top: 8px;
                background-color: #3b4252;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 3px;
                background-color: #3b4252;
            }
            QStatusBar {
                background-color: #2e3440;
                color: #d8dee9;
                font-size: 8pt;
                padding: 2px;
            }
            QMessageBox {
                background-color: #2e3440;
                color: #d8dee9;
            }
            QMessageBox QPushButton {
                background-color: #5e81ac;
                color: white;
                padding: 3px 12px;
                border-radius: 2px;
                min-width: 60px;
                font-size: 8pt;
            }
            QMessageBox QPushButton:hover {
                background-color: #81a1c1;
            }
            QLineEdit {
                background-color: #3b4252;
                color: #d8dee9;
                border: 1px solid #4c566a;
                border-radius: 2px;
                padding: 2px 4px;
                height: 16px;
                font-size: 8pt;
            }
            QLineEdit:focus {
                border: 1px solid #5e81ac;
            }
            QTextEdit {
                background-color: #2e3440;
                color: #d8dee9;
                border: 1px solid #4c566a;
                border-radius: 2px;
                font-family: 'Consolas', monospace;
                font-size: 8pt;
                padding: 2px;
            }
            QPushButton {
                background-color: #4c566a;
                color: #d8dee9;
                border: none;
                border-radius: 2px;
                padding: 3px 12px;
                font-size: 8pt;
                height: 20px;
            }
            QPushButton:hover {
                background-color: #5e81ac;
            }
            QPushButton:pressed {
                background-color: #4c566a;
            }
        """)
        
        # Set window properties
        self.setWindowTitle("Project Setup")
        self.setMinimumSize(600, 500)
        self.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__), "icons", "logo.ico")))
        
        # Create central widget and main layout
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(4)
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        
        # Set application-wide font
        self.font = QtGui.QFont("Segoe UI", 8)
        QtWidgets.QApplication.setFont(self.font)
        
        # Initialize UI
        self.init_ui()
        
        # Create status bar
        self.status_bar = QtWidgets.QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def init_ui(self):
        # Title and Description
        title_label = QtWidgets.QLabel("Project Setup Tool")
        title_label.setStyleSheet("""
            font-size: 12pt;
            font-weight: bold;
            color: #88c0d0;
            padding-bottom: 4px;
        """)
        
        desc_label = QtWidgets.QLabel(
            "Create and configure new projects with standardized folder structure and Ftrack integration. "
            "This tool helps maintain consistency across project setups by automating the creation of "
            "required directories and initializing project tracking."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #d8dee9; padding-bottom: 8px;")
        
        # Add title and description to layout
        self.main_layout.addWidget(title_label)
        self.main_layout.addWidget(desc_label)
        self.main_layout.addSpacing(8)
        
        # Create form group for inputs
        form_group = QtWidgets.QGroupBox("Project Information")
        form_layout = QtWidgets.QFormLayout(form_group)
        form_layout.setSpacing(4)
        form_layout.setContentsMargins(8, 8, 8, 8)
        form_layout.setLabelAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        
        # Input Widgets
        self.project_name_input = QtWidgets.QLineEdit()
        self.project_code_input = QtWidgets.QLineEdit()
        self.start_date_input = QtWidgets.QLineEdit()
        self.end_date_input = QtWidgets.QLineEdit()
        
        for input_widget in [self.project_name_input, self.project_code_input, 
                           self.start_date_input, self.end_date_input]:
            input_widget.setMinimumWidth(200)
        
        form_layout.addRow("Project Name:", self.project_name_input)
        form_layout.addRow("Project Code:", self.project_code_input)
        form_layout.addRow("Start Date:", self.start_date_input)
        form_layout.addRow("End Date:", self.end_date_input)
        
        # Thumbnail section
        thumbnail_group = QtWidgets.QGroupBox("Project Thumbnail")
        thumbnail_layout = QtWidgets.QVBoxLayout(thumbnail_group)
        thumbnail_layout.setSpacing(4)
        thumbnail_layout.setContentsMargins(8, 8, 8, 8)
        
        self.thumbnail_label = QtWidgets.QLabel("No thumbnail selected")
        self.thumbnail_button = self.create_button("Choose Thumbnail", self.choose_thumbnail)
        
        thumbnail_layout.addWidget(self.thumbnail_label)
        thumbnail_layout.addWidget(self.thumbnail_button)
        
        # Log output section
        log_group = QtWidgets.QGroupBox("Log Output")
        log_layout = QtWidgets.QVBoxLayout(log_group)
        log_layout.setSpacing(4)
        log_layout.setContentsMargins(8, 8, 8, 8)
        
        self.log_window = QtWidgets.QTextEdit()
        self.log_window.setReadOnly(True)
        self.log_window.setMaximumHeight(100)
        log_layout.addWidget(self.log_window)
        
        # Create project button
        self.create_project_btn = self.create_button("Create Project", self.create_project)
        self.create_project_btn.setStyleSheet("""
            QPushButton {
                background-color: #5e81ac;
                height: 24px;
                font-weight: bold;
            }
        """)
        
        # Add all sections to main layout with spacing
        self.main_layout.addWidget(form_group)
        self.main_layout.addSpacing(4)
        self.main_layout.addWidget(thumbnail_group)
        self.main_layout.addSpacing(4)
        self.main_layout.addWidget(log_group)
        self.main_layout.addSpacing(8)
        self.main_layout.addWidget(self.create_project_btn)

    def create_button(self, label, func):
        button = QtWidgets.QPushButton(label)
        button.setStyleSheet("""
            QPushButton {
                background-color: #4c566a;
                color: #d8dee9;
                border: none;
                border-radius: 2px;
                padding: 3px 12px;
                font-size: 8pt;
                height: 20px;
            }
            QPushButton:hover {
                background-color: #5e81ac;
            }
            QPushButton:pressed {
                background-color: #4c566a;
            }
        """)
        button.clicked.connect(func)
        return button

    def choose_thumbnail(self):
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Choose Thumbnail", "", 
            "Images (*.png *.jpg *.jpeg)", options=options
        )
        if file_path:
            self.thumbnail_label.setText(f"Selected: {os.path.basename(file_path)}")
            self.thumbnail_path = file_path
            self.status_bar.showMessage(f"Thumbnail selected: {os.path.basename(file_path)}")

    def create_project(self):
        try:
            self.status_bar.showMessage("Creating project...")
            # Validate Inputs
            project_name = self.project_name_input.text()
            project_code = self.project_code_input.text()
            start_date = self.start_date_input.text()
            end_date = self.end_date_input.text()
            validate_inputs(project_name, project_code, start_date, end_date)

            # Update Config and Save
            self.config['pipeline_data']['globals']['project_name'] = project_name
            save_config(self.config_file_path, self.config)

            # Create Ftrack Project
            logger.info("Creating Ftrack project...")
            project, session = create_ftrack_project(project_name, project_code, start_date, end_date, self.config['ftrack'])
            if not project:
                raise Exception("Failed to create Ftrack project.")

            # Setup Folder Structure
            root_path = self.config['root_path']
            project_path = os.path.join(root_path, project_name)
            setup_folder_structure(project_path, self.config['folder_structure'])

            # Process Thumbnail
            save_paths = [
                os.path.join(project_path, "00_Pipeline", "project.jpg")
            ]
            self.thumbnail_path = getattr(self, 'thumbnail_path', None)
            process_thumbnail(self.thumbnail_path, save_paths)

            self.status_bar.showMessage(f"Project '{project_name}' created successfully!")
            QtWidgets.QMessageBox.information(self, 'Success', f"Project '{project_name}' setup complete.")
        except Exception as e:
            logger.error(str(e))
            self.status_bar.showMessage("Error creating project")
            QtWidgets.QMessageBox.critical(self, 'Error', f"An error occurred:\n{e}")

# Main Function
def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Project Setup Tool")
    app.setOrganizationName("Your Organization")
    window = ProjectSetupApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
