"""Main UI window for the batch metahuman importer."""

from PySide6 import QtWidgets, QtCore
from batch_metahuman_importer.processing.body.body_batch_processor import BodyBatchProcessor
from batch_metahuman_importer.processing.face.face_processor import FaceProcessor, AssetWrapper
from batch_metahuman_importer.processing.face.face_helper import FaceHelper
from batch_metahuman_importer.utils.constants import MOCAP_BASE_PATH
from batch_metahuman_importer.utils.logging_config import logger
from batch_metahuman_importer.gui.progress_dialog import ProgressDialog
from batch_metahuman_importer.gui.selection_dialog import UnifiedSelectionDialog

class BatchProcessorUI(QtWidgets.QWidget):
    """Main window for the batch face/body importer application."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.body_processor = BodyBatchProcessor()
        self.face_processor = FaceProcessor()
        self.face_helper = FaceHelper()
        self.progress_dialog = None
        self.setup_ui()

    def setup_ui(self):
        """Set up the main UI with two choices."""
        self.setWindowTitle("MHA Batch Processor")
        self.setGeometry(300, 300, 400, 200)
        
        # Set window flags for proper window behavior
        self.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.WindowMinimizeButtonHint |
            QtCore.Qt.WindowMaximizeButtonHint |
            QtCore.Qt.WindowCloseButtonHint
        )
        
        # Style the window
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QPushButton {
                background-color: #3b3b3b;
                color: white;
                border: 1px solid #555555;
                padding: 15px;
                font-size: 14px;
                min-width: 200px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #4b4b4b;
            }
        """)

        # Create layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # Add title label
        title_label = QtWidgets.QLabel("Select Import Type")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title_label)

        # Add buttons
        face_button = QtWidgets.QPushButton("MHA Face Import")
        body_button = QtWidgets.QPushButton("MHA Body Import")
        
        # Connect buttons
        face_button.clicked.connect(self.show_face_importer)
        body_button.clicked.connect(self.show_body_importer)

        layout.addWidget(face_button)
        layout.addWidget(body_button)
        
        # Center the window
        self.center_window()
        
        # Show the window
        self.show()

    def center_window(self):
        """Center the window on the screen."""
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )

    def show_face_importer(self):
        """Handle face import selection."""
        try:
            # Hide the main window
            self.hide()
            
            # Import and reload the reference implementation
            import importlib.util
            import sys
            
            # Define the absolute path to the reference file
            reference_path = r"S:\UNREAL_PROJECTS\TWINKLETWINKLE_MAIN\Content\Python\batch_metahuman_importer\Reference\Batch_Face_Importer_PUB_updated_v4.py"
            
            # Import the module
            spec = importlib.util.spec_from_file_location("batch_face_importer", reference_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules["batch_face_importer"] = module
            spec.loader.exec_module(module)
            
            # Run the reference implementation
            module.run()
            
        except Exception as e:
            logger.error(f"Error running face importer: {str(e)}")
            self.show_error_dialog(str(e))
            self.show()  # Show main window again if there's an error

    def show_face_selection_dialog(self, available_folders, capture_data_assets):
        """Show selection dialog for face processing."""
        try:
            if not available_folders and not capture_data_assets:
                QtWidgets.QMessageBox.warning(self, "No Items", "No folders or capture data assets were found.")
                return

            dialog = UnifiedSelectionDialog(available_folders, capture_data_assets, self)
            
            if dialog.exec_():
                selected_items = dialog.get_selected_items()
                if selected_items and (selected_items['folders'] or selected_items['assets']):
                    self.confirm_and_start_face_processing(selected_items)
                else:
                    QtWidgets.QMessageBox.warning(self, "No Selection", "Please check at least one folder or asset to process.")
        except Exception as e:
            logger.error(f"Error in face selection dialog: {str(e)}")
            QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            self.show()

    def show_body_importer(self):
        """Handle body import selection."""
        try:
            self.hide()  # Hide the main window
            
            # Create file dialog for FBX selection
            files, _ = QtWidgets.QFileDialog.getOpenFileNames(
                self,
                "Select Body Animation FBX Files",
                "",
                "FBX Files (*.fbx)"
            )
            
            if not files:
                self.show()  # Show main window if no files selected
                return
            
            # Create character selection dialog
            character_name, ok = QtWidgets.QInputDialog.getItem(
                self,
                "Select Character",
                "Choose target character:",
                list(self.body_processor.helper.skeletal_mesh_mapping.keys()),
                0,
                False
            )
            
            if not ok or not character_name:
                self.show()  # Show main window if no character selected
                return
            
            self.start_body_processing(files, character_name)
            
        except Exception as e:
            logger.error(f"Error in body importer: {str(e)}")
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to start body import: {str(e)}")
            self.show()

    def confirm_and_start_face_processing(self, selections):
        try:
            assets_to_process = []
            folder_assets = []
            
            # Process folders first
            if selections['folders']:
                for folder_path in selections['folders']:
                    # Convert AssetWrapper to string path if needed
                    if hasattr(folder_path, 'get_path_name'):
                        folder_path = folder_path.get_path_name()
                    else:
                        folder_path = str(folder_path)
                    
                    folder_assets.extend(self.face_processor.asset_processor.get_capture_data_assets(folder_path))
            
            # Add individual assets and combine
            if selections['assets']:
                assets_to_process.extend(selections['assets'])
            assets_to_process.extend(folder_assets)
            
            if not assets_to_process:
                QtWidgets.QMessageBox.warning(self, "No Assets", "No valid assets found to process.")
                return

            # Start processing
            self.start_face_processing(assets_to_process)
            
        except Exception as e:
            logger.error(f"Error in face confirmation: {str(e)}")
            QtWidgets.QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def start_face_processing(self, assets):
        """Start the face batch processing."""
        try:
            # Create progress dialog
            self.progress_dialog = ProgressDialog(self)
            
            # Add assets to progress dialog
            for asset in assets:
                asset_name = asset.get_name() if hasattr(asset, 'get_name') else str(asset).split('/')[-1]
                self.progress_dialog.add_item(str(asset), asset_name)
                
            self.progress_dialog.show()

            # Connect signals
            self.face_processor.progress_updated.connect(self.update_progress)
            self.face_processor.processing_finished.connect(self.on_processing_finished)
            self.face_processor.error_occurred.connect(self.show_error_dialog)

            # Start processing
            self.face_processor.run_batch_process(assets, False)
            
        except Exception as e:
            logger.error(f"Error starting face processing: {str(e)}")
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to start face processing: {str(e)}")
            if self.progress_dialog:
                self.progress_dialog.close()

    def update_progress(self, index, status, error="", progress_type='processing'):
        """Update progress in dialog."""
        if self.progress_dialog:
            self.progress_dialog.update_item_progress(index, status, error, progress_type)
            
    def on_processing_finished(self):
        """Handle completion of batch processing."""
        if self.progress_dialog:
            self.progress_dialog.log_text.append("<b>Batch processing has finished.</b>")
            logger.info("Batch processing has finished.")

    def show_error_dialog(self, error_message):
        """Display error message."""
        QtWidgets.QMessageBox.critical(self, "Error", error_message)

    def start_body_processing(self, files, character_name):
        """Start the body batch processing."""
        try:
            # Create progress dialog
            self.progress_dialog = ProgressDialog(self)
            
            # Add files to progress dialog
            for fbx_path in files:
                file_name = fbx_path.split('/')[-1]
                self.progress_dialog.add_item(fbx_path, file_name)
                
            self.progress_dialog.show()

            # Connect signals
            self.body_processor.progress_updated.connect(self.update_progress)
            self.body_processor.processing_finished.connect(self.on_processing_finished)
            self.body_processor.error_occurred.connect(self.show_error_dialog)
            
            # Start batch processing
            self.body_processor.run_batch_process(files, character_name)
            
        except Exception as e:
            logger.error(f"Error starting body processing: {str(e)}")
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to start body processing: {str(e)}")
            if self.progress_dialog:
                self.progress_dialog.close()
