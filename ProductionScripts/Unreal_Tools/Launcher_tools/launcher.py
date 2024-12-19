import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                             QProgressBar, QMessageBox, QFileDialog, QWidget, QComboBox, QPushButton, QHBoxLayout, QGroupBox)
from PyQt5.QtCore import Qt, QTimer, QSettings
from PyQt5.QtGui import QIcon, QFont
import subprocess

def resource_path(relative_path):
    """ Get the absolute path to the resource. """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

class UnrealEngineLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Add exception handling for the entire application
        sys.excepthook = self.handle_exception

        # Initialize the default Unreal Projects Directory
        # Try to read from settings first, fallback to default
        try:
            saved_dir = self.settings.value('last_directory')
            self.ue_projects_dir = saved_dir if saved_dir and os.path.exists(saved_dir) else "S:/UNREAL_PROJECTS"
        except:
            self.ue_projects_dir = "S:/UNREAL_PROJECTS"
        
        # Initialize timer and progress value
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.progress_value = 0

        # Initialize settings
        self.settings = QSettings('UnrealLauncher', 'ProjectSettings')

        # Set up the window icon and title
        self.initUI()  # Call a method to set up the UI

    def initUI(self):
        # Set up the window icon
        logo_path = resource_path("logo_white_Do5_icon.ico")
        self.setWindowIcon(QIcon(logo_path))

        # Set the window title
        self.setWindowTitle("Unreal Engine Launcher")
        self.setGeometry(300, 300, 600, 400)

        # Set the overall style
        self.setStyleSheet("background-color: #2e3440; color: #d8dee9;")
        
        # Create central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Add instructions at the top
        instructions_label = QLabel("Step 1: Select your Unreal Projects folder. Step 2: Choose a project to launch.", self)
        instructions_label.setAlignment(Qt.AlignCenter)
        instructions_label.setStyleSheet("font-size: 14px; color: #d8dee9; margin-bottom: 10px;")
        layout.addWidget(instructions_label)

        # Create a more prominent directory selection section
        directory_group = QGroupBox("Step 1: Select Unreal Projects Root Folder", self)
        directory_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #88c0d0;
                border: 2px solid #88c0d0;
                border-radius: 6px;
                margin-top: 1ex;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        directory_layout = QVBoxLayout(directory_group)
        
        # Add help text
        help_label = QLabel("This should be the folder that contains all your Unreal Engine projects\n"
                           "Example: S:/UNREAL_PROJECTS", self)
        help_label.setStyleSheet("color: #d8dee9; font-size: 12px; margin-bottom: 10px;")
        help_label.setAlignment(Qt.AlignCenter)
        directory_layout.addWidget(help_label)
        
        # Directory selection controls in horizontal layout
        directory_controls = QHBoxLayout()
        
        # Large, prominent browse button
        self.add_directory_button = QPushButton("📁 Browse for Projects Folder", self)
        self.add_directory_button.setToolTip("Click here to select your Unreal Projects folder")
        self.add_directory_button.setStyleSheet("""
            QPushButton {
                background-color: #5e81ac;
                color: white;
                font-size: 13px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 4px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #81a1c1;
            }
        """)
        self.add_directory_button.clicked.connect(self.prompt_for_directory)
        directory_controls.addWidget(self.add_directory_button)
        
        # Current directory display
        self.directory_label = QLabel(self.ue_projects_dir, self)
        self.directory_label.setStyleSheet("""
            QLabel {
                background-color: #3b4252;
                color: #d8dee9;
                padding: 10px;
                border-radius: 4px;
                border: 1px solid #4c566a;
            }
        """)
        directory_controls.addWidget(self.directory_label)
        
        directory_layout.addLayout(directory_controls)
        layout.addWidget(directory_group)
        
        # Project selection section
        project_group = QGroupBox("Step 2: Select Project", self)
        project_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #88c0d0;
                border: 2px solid #88c0d0;
                border-radius: 6px;
                margin-top: 1ex;
                padding: 10px;
            }
        """)
        project_layout = QVBoxLayout(project_group)
        
        # Add help text for project selection
        project_help_label = QLabel("Choose the Unreal project you want to launch", self)
        project_help_label.setStyleSheet("color: #d8dee9; font-size: 12px; margin-bottom: 10px;")
        project_help_label.setAlignment(Qt.AlignCenter)
        project_layout.addWidget(project_help_label)
        
        # Project dropdown with improved styling and arrow
        self.project_dropdown = QComboBox(self)
        self.project_dropdown.setToolTip("Select your Unreal project from the list")
        self.project_dropdown.setStyleSheet("""
            QComboBox {
                font-size: 12px;
                padding: 8px;
                border: 1px solid #88c0d0;
                border-radius: 4px;
                background: #3b4252;
                margin: 5px;
                min-width: 200px;
            }
            QComboBox:hover {
                border: 1px solid #5e81ac;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
                background: #4c566a;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
            }
            QComboBox::down-arrow {
                color: #d8dee9;
                font-size: 12px;
            }
            QComboBox::down-arrow:on {
                top: 1px;
            }
        """)
        self.project_dropdown.addItem("▼")  # Unicode down arrow
        project_layout.addWidget(self.project_dropdown)
        
        # Add status label
        self.status_label = QLabel("", self)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #d8dee9;
                font-size: 12px;
                margin-top: 10px;
            }
        """)
        layout.addWidget(self.status_label)

        # Add log label
        self.log_label = QLabel("", self)
        self.log_label.setStyleSheet("""
            QLabel {
                color: #a3be8c;
                font-size: 11px;
                font-style: italic;
            }
        """)
        layout.addWidget(self.log_label)

        layout.addWidget(project_group)

        # Info label to display selected project and version
        self.info_label = QLabel("", self)
        self.info_label.setStyleSheet("color: #d8dee9; font-size: 12px; margin-top: 10px;")
        layout.addWidget(self.info_label)

        # Progress bar for initialization
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #88c0d0;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #5e81ac;
            }
        """)
        layout.addWidget(self.progress_bar)

        # Connect the project dropdown to its handler
        self.project_dropdown.currentTextChanged.connect(self.on_project_changed)

        # Populate projects from default directory
        self.populate_projects()

        # Add Launch button
        self.launch_button = QPushButton("🚀 Launch Project", self)
        self.launch_button.setToolTip("Launch the selected Unreal project")
        self.launch_button.setStyleSheet("""
            QPushButton {
                background-color: #a3be8c;
                color: white;
                font-size: 13px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 4px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #b5d19a;
            }
        """)
        self.launch_button.clicked.connect(self.start_launch)
        layout.addWidget(self.launch_button)

    def prompt_for_directory(self):
        """
        Prompt the user to select their project directory and provide feedback.
        """
        try:
            # Create a more descriptive dialog
            dir = QFileDialog.getExistingDirectory(
                self,
                "Select the Root Unreal Projects Folder (e.g., S:/UNREAL_PROJECTS)",
                self.ue_projects_dir,
                QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
            )
            
            if dir:
                # Check if they selected a project folder instead of the root directory
                try:
                    if any(f.endswith('.uproject') for f in os.listdir(dir)):
                        QMessageBox.warning(
                            self,
                            "Invalid Selection",
                            "You've selected a specific project folder.\n\n"
                            "Please select the parent folder that contains ALL your Unreal projects.\n"
                            "For example: 'S:/UNREAL_PROJECTS'\n\n"
                            "✗ Incorrect: 'S:/UNREAL_PROJECTS/MyProject'\n"
                            "✓ Correct: 'S:/UNREAL_PROJECTS'"
                        )
                        return
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Error accessing directory:\n{str(e)}"
                    )
                    return
                
                # Validate that this looks like an Unreal projects directory
                if self.is_valid_projects_directory(dir):
                    self.ue_projects_dir = dir
                    self.directory_label.setText(dir)
                    self.populate_projects()
                    self.status_label.setText("✓ Projects folder set successfully!")
                    self.log_label.setText("Found Unreal Engine projects")
                    
                    try:
                        # Save to settings for next time
                        self.settings.setValue('last_directory', dir)
                    except Exception as e:
                        print(f"Warning: Could not save settings: {str(e)}")
                else:
                    QMessageBox.warning(
                        self,
                        "Invalid Directory",
                        "The selected folder doesn't appear to contain any Unreal Engine projects.\n\n"
                        "Please select the root folder where your Unreal projects are stored.\n"
                        "This is typically a folder containing multiple project folders, "
                        "each with a .uproject file.\n\n"
                        "Example: 'S:/UNREAL_PROJECTS'"
                    )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred while selecting directory:\n{str(e)}"
            )

    def is_valid_projects_directory(self, directory):
        """
        Check if the directory contains valid Unreal Engine projects.
        Returns True if at least one subdirectory contains a .uproject file.
        """
        try:
            # Look for at least one .uproject file in immediate subdirectories
            for item in os.listdir(directory):
                project_dir = os.path.join(directory, item)
                if os.path.isdir(project_dir):
                    # Check each subdirectory for a .uproject file
                    for subitem in os.listdir(project_dir):
                        if subitem.endswith('.uproject'):
                            return True
            return False
        except Exception:
            return False

    def on_project_changed(self):
        """
        Handle project change event.
        """
        project_name = self.project_dropdown.currentText()
        if project_name:
            self.project_name = project_name
            self.info_label.setText(f"Project selected: {self.project_name}")

    def populate_projects(self):
        """
        Populate the project dropdown based on the selected directory,
        ignoring projects that start with 'UP_' or 'UE_'.
        """
        self.project_dropdown.clear()
        if os.path.exists(self.ue_projects_dir):
            projects = [
                f for f in os.listdir(self.ue_projects_dir) 
                if os.path.isdir(os.path.join(self.ue_projects_dir, f)) and not (f.startswith('UP_') or f.startswith('UE_'))
            ]
            self.project_dropdown.addItems(projects)
            if projects:
                self.status_label.setText("Found Unreal Engine projects")
            else:
                self.status_label.setText("No valid projects found in directory")
        else:
            self.status_label.setText("Selected directory does not exist!")
    
    def read_metadata(self):
        """
        Read Unreal Engine version from METADATA.txt.
        """
        self.metadata_file = os.path.join(self.ue_projects_dir, self.project_name, "METADATA.txt")
        
        # Log the full path we're checking
        print(f"Looking for METADATA.txt at: {self.metadata_file}")
        self.update_log(f"Looking for METADATA.txt at: {self.metadata_file}")
        
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r') as file:
                    version = file.read().strip().strip('"')
                    print(f"Found UE version: {version}")
                    self.update_log(f"Found UE version: {version}")
                    return version
            else:
                error_msg = f"❌ METADATA.txt not found at:\n{self.metadata_file}"
                print(error_msg)
                self.update_log(error_msg)
                QMessageBox.critical(self, "Error", error_msg)
                return None
        except Exception as e:
            error_msg = f"❌ Error reading METADATA.txt at {self.metadata_file}\nError: {str(e)}"
            print(error_msg)
            self.update_log(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
            return None
    
    def clean_version(self, version_str):
        """
        Clean the version string (remove UE_ and convert to a readable format).
        Example: 'UE_5_4_2' becomes 'Unreal 5.4.2'
                'UE_5_4' becomes 'Unreal 5.4'
        """
        if version_str.startswith("UE_"):
            # Remove 'UE_' prefix and split by underscore
            parts = version_str[3:].split("_")
            if len(parts) >= 2:
                # Handle cases with and without patch version
                if len(parts) == 2:
                    return f"Unreal {parts[0]}.{parts[1]}"
                else:
                    return f"Unreal {parts[0]}.{parts[1]}.{parts[2]}"
        return version_str

    def start_launch(self):
        """
        Start the progress bar and simulate Unreal Engine launch when the Launch button is pressed.
        """
        if self.project_name:
            # Reset progress value before starting
            self.progress_value = 0
            self.progress_bar.setValue(0)
            
            # Read metadata only when launching
            self.ue_version_full = self.read_metadata()
            if self.ue_version_full:  # Only proceed if metadata was successfully read
                self.ue_version_clean = self.clean_version(self.ue_version_full)
                self.status_label.setText(f"Launching Unreal Engine {self.ue_version_clean}... Please wait.")
                self.timer.start(100)
        else:
            QMessageBox.warning(self, "Warning", "Please select a project before launching!")

    def update_progress(self):
        if self.progress_value < 100:
            self.progress_value += 5
            self.progress_bar.setValue(self.progress_value)
        else:
            self.timer.stop()
            self.launch_unreal()

    def update_log(self, message):
        """
        Update the log message underneath the progress bar.
        """
        if self.log_label is not None:
            self.log_label.setText(message)

    def verify_permissions(self, path):
        """
        Verify read/write permissions for the given path
        """
        try:
            if os.path.exists(path):
                # Check if we can read the directory/file
                if os.access(path, os.R_OK):
                    self.update_log(f"✓ Read permission verified for: {path}")
                    return True
                else:
                    error_msg = f"❌ No read permission for: {path}"
                    self.update_log(error_msg)
                    QMessageBox.warning(
                        self,
                        "Permission Error",
                        f"Missing read permissions!\n\n"
                        f"Path: {path}\n\n"
                        "Please ensure you have proper permissions to access this location."
                    )
                    return False
            return True  # Return True for non-existent paths (they'll be handled elsewhere)
        except Exception as e:
            self.update_log(f"❌ Permission check failed: {str(e)}")
            return False

    def launch_unreal(self):
        """
        Launch Unreal Engine executable with the specified project.
        """
        try:
            # Build paths
            project_folder = os.path.join(self.ue_projects_dir, self.project_name)
            unreal_path = os.path.join(self.ue_projects_dir, self.ue_version_full, 
                                      "Windows", "Engine", "Binaries", "Win64", "UnrealEditor.exe")
            project_file = os.path.join(project_folder, f"{self.project_name}.uproject")

            # Verify permissions first
            paths_to_verify = [
                self.ue_projects_dir,
                project_folder,
                os.path.dirname(unreal_path),
                project_file
            ]

            for path in paths_to_verify:
                if not self.verify_permissions(path):
                    return

            # Create detailed verification messages
            paths_to_check = {
                "Project folder": (project_folder, "Project folder not found. Please verify the project exists."),
                "Unreal executable": (unreal_path, f"Unreal Engine {self.ue_version_full} not found. Please verify the engine is installed."),
                "Project file": (project_file, f"Project file ({self.project_name}.uproject) not found. Please verify the project is valid.")
            }

            # Check paths exist
            for name, (path, error_msg) in paths_to_check.items():
                exists = os.path.exists(path)
                status = "✓ Found" if exists else "❌ Not found"
                message = f"{status} - {name} at:\n{path}"
                print(message)
                self.update_log(message)
                
                if not exists:
                    QMessageBox.critical(self, "Launch Error", f"{error_msg}\n\nExpected path:\n{path}")
                    return

            # Launch with proper error handling
            try:
                # Launch with explicit working directory
                process = subprocess.Popen(
                    [unreal_path, project_file],
                    cwd=os.path.dirname(unreal_path),
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
                
                # Wait briefly to check if process started successfully
                try:
                    return_code = process.wait(timeout=2)
                    if return_code != 0:
                        raise subprocess.SubprocessError(f"Process exited with code {return_code}")
                except subprocess.TimeoutExpired:
                    # Process is still running after 2 seconds, this is good
                    QMessageBox.information(
                        self, 
                        "Success", 
                        f"Unreal Engine {self.ue_version_clean} is launching!\n"
                        f"Project: {self.project_name}"
                    )
                    
            except subprocess.SubprocessError as e:
                QMessageBox.critical(
                    self,
                    "Launch Failed",
                    f"Failed to launch Unreal Engine.\n\n"
                    f"Error: {str(e)}\n\n"
                    "Please verify:\n"
                    "1. You have sufficient permissions\n"
                    "2. Antivirus is not blocking the executable\n"
                    "3. The Unreal Engine installation is not corrupted"
                )
                return
            
        except Exception as e:
            error_msg = (
                f"Launch failed:\n{str(e)}\n\n"
                f"Project: {self.project_name}\n"
                f"Engine Version: {self.ue_version_full}\n"
                "Please verify all paths and permissions are correct."
            )
            print(error_msg)
            self.update_log(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
            return

        self.close()

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """Global exception handler for the application"""
        error_msg = f"An unexpected error occurred:\n{str(exc_value)}\n\nPlease contact support."
        QMessageBox.critical(
            self,
            "Critical Error",
            error_msg
        )
        # Log the full error for debugging
        import traceback
        print("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        
        # Set application metadata
        app.setApplicationName("Unreal Engine Launcher")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("Your Organization")
        
        # Apply system-wide exception handling
        sys.excepthook = lambda *args: UnrealEngineLauncher.handle_exception(None, *args)
        
        # Create and show the launcher
        launcher = UnrealEngineLauncher()
        launcher.show()
        
        sys.exit(app.exec_())
    except Exception as e:
        QMessageBox.critical(
            None,
            "Critical Error",
            f"Failed to start the application:\n{str(e)}\n\nPlease contact support."
        )
