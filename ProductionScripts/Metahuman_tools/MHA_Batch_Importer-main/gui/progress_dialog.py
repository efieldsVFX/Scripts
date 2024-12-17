"""Dialog for displaying batch processing progress."""

from PySide6 import QtWidgets, QtCore, QtGui
from ..utils.logging_config import logger
import re

class ProgressDialog(QtWidgets.QDialog):
    """Dialog showing batch processing progress with detailed status."""
    
    def __init__(self, parent=None, actor_character_mapping=None):
        super().__init__(parent)
        self.actor_character_mapping = actor_character_mapping or {}
        self.is_processing = False
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Initialize the UI components."""
        self.setModal(False)
        self.setWindowTitle("Processing")
        self.setGeometry(300, 300, 1200, 500)
        self.setup_window_flags()
        self.setup_layout()
        self.apply_styles()
        
    def setup_window_flags(self):
        """Set up window flags for dialog behavior."""
        self.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.WindowMinimizeButtonHint |
            QtCore.Qt.WindowMaximizeButtonHint |
            QtCore.Qt.WindowCloseButtonHint
        )
        # Ensure dialog stays on top when first shown
        self.activateWindow()
        self.raise_()
        
    def setup_layout(self):
        """Set up the dialog layout and widgets."""
        layout = QtWidgets.QVBoxLayout(self)
        
        # Add spacing at the top
        layout.addSpacing(10)
        
        # Batch progress bar
        self.batch_progress_bar = QtWidgets.QProgressBar()
        self.batch_progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
                height: 25px;
                font-weight: bold;
                font-size: 12px;
                color: white;
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
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
        
        # Add progress table
        self.setup_progress_table()
        layout.addWidget(self.progress_table)
        
        # Add log area
        self.log_text = QtWidgets.QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(100)
        layout.addWidget(self.log_text)
        
        # Add save log and close buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        self.save_log_button = QtWidgets.QPushButton("Save Log")
        self.save_log_button.clicked.connect(self.save_log)
        button_layout.addWidget(self.save_log_button)
        
        self.close_button = QtWidgets.QPushButton("Close")
        self.close_button.setEnabled(False)  # Disabled initially
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
    def setup_progress_table(self):
        """Set up the progress tracking table."""
        self.progress_table = QtWidgets.QTableView()
        self.progress_model = QtGui.QStandardItemModel()
        
        # Set headers
        self.progress_model.setHorizontalHeaderLabels([
            "Folder", "Character", "Slate", "Sequence",
            "Actor", "Take", "Process Status", "Export Status", "Error"
        ])
        
        # Set model to table
        self.progress_table.setModel(self.progress_model)
        
        # Configure table properties
        self.progress_table.setShowGrid(True)  # Make sure grid is visible
        self.progress_table.setAlternatingRowColors(True)  # Optional: for better readability
        self.progress_table.verticalHeader().setVisible(False)  # Hide row numbers
        
        # Enable sorting
        self.progress_table.setSortingEnabled(True)
        
        # Enable selection
        self.progress_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.progress_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        
        # Set resize modes for better column behavior
        header = self.progress_table.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
        header.setStretchLastSection(True)
        
        # Setup column widths
        self.setup_table_columns()
        
    def setup_table_columns(self):
        """Configure table column sizes."""
        column_widths = {
            0: 250,  # Folder
            1: 100,  # Character
            2: 80,   # Slate
            3: 100,  # Sequence
            4: 100,  # Actor
            5: 80,   # Take
            6: 120,  # Process Status
            7: 120,  # Export Status
            8: 200   # Error
        }
        
        for col, width in column_widths.items():
            self.progress_table.setColumnWidth(col, width)
            
    def setup_log_area(self, layout):
        """Set up the log text area."""
        self.log_text = QtWidgets.QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        layout.addWidget(QtWidgets.QLabel("Log:"))
        layout.addWidget(self.log_text)
        
    def apply_styles(self):
        """Apply stylesheet to the dialog."""
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                font-size: 12px;
            }
            QTableView {
                background-color: #363636;
                color: #ffffff;
                gridline-color: #505050;
                border: none;
            }
            QHeaderView::section {
                background-color: #404040;
                color: #ffffff;
                padding: 5px;
                border: 1px solid #505050;
            }
            QTableView::item {
                padding: 5px;
            }
            QTableView::item:selected {
                background-color: #4b4b4b;
            }
            QTextEdit {
                background-color: #363636;
                color: #ffffff;
                border: 1px solid #505050;
            }
            QPushButton {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #505050;
                padding: 8px 15px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:disabled {
                background-color: #2b2b2b;
                color: #808080;
            }
        """)
    def set_batch_progress(self, value):
        """Set the value of the batch progress bar."""
        self.batch_progress_bar.setValue(value)

    def set_status(self, text):
        """Set the status label text."""
        self.status_label.setText(text)

    def add_item(self, folder_name, item_name):
        """Add item to progress dialog."""
        try:
            row_position = self.progress_model.rowCount()
            
            # Clean up folder name to show from Mocap forward
            folder_display = ""
            
            # Log the original folder_name and its type
            logger.info(f"Original folder_name: {folder_name} (type: {type(folder_name).__name__})")
            
            # Get the actual path from the AssetWrapper
            if hasattr(folder_name, 'get_path'):
                folder_display = folder_name.get_path()
                logger.info(f"Using get_path(): {folder_display}")
            elif hasattr(folder_name, 'path'):
                folder_display = folder_name.path
                logger.info(f"Using path attribute: {folder_display}")
            else:
                folder_display = str(folder_name)
                logger.info(f"Using str() fallback: {folder_display}")
            
            # Extract path from Mocap forward
            if "Mocap" in folder_display:
                mocap_index = folder_display.find("Mocap")
                folder_display = folder_display[mocap_index:]
                folder_display = folder_display.strip('/')
                folder_display = "/Game/01_ASSETS/External/" + folder_display
                logger.info(f"Modified folder_display after Mocap processing: {folder_display}")
            
            # Convert item_name to string and get just the filename if it's a path
            if '/' in str(item_name):
                item_name = str(item_name).split('/')[-1]
            
            # Remove '_Performance' suffix if present
            if item_name.endswith('_Performance'):
                item_name = item_name[:-11]
            
            # Parse the item name to extract components
            name_components = self.extract_name_variable(item_name)
            logger.info(f"Parsed components for {item_name}: {name_components}")
            
            # Create items for each column
            folder_item = QtGui.QStandardItem(str(folder_display))
            
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
                take_item = QtGui.QStandardItem(take)
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
            
            return row_position
        except Exception as e:
            logger.error(f"Error adding item to progress dialog: {str(e)}")
            return -1
        
    def update_item_progress(self, index, status, error="", progress_type='processing'):
        """Update progress for a specific item."""
        try:
            if progress_type == 'processing':
                status_item = self.progress_model.item(index, 6)  # Process Status column
                if status_item:
                    status_item.setText(status)
                    # Set color based on status
                    if status == "Complete":
                        status_item.setForeground(QtGui.QColor("#4CAF50"))  # Green
                    elif status == "Failed":
                        status_item.setForeground(QtGui.QColor("#f44336"))  # Red
                    else:
                        status_item.setForeground(QtGui.QColor("#ffffff"))  # White
                    
            elif progress_type == 'exporting':
                status_item = self.progress_model.item(index, 7)  # Export Status column
                if status_item:
                    status_item.setText(status)
                    # Set color based on status
                    if status == "Complete":
                        status_item.setForeground(QtGui.QColor("#4CAF50"))
                    elif status == "Failed":
                        status_item.setForeground(QtGui.QColor("#f44336"))
                    else:
                        status_item.setForeground(QtGui.QColor("#ffffff"))

            if error:
                error_item = self.progress_model.item(index, 8)  # Error column
                if error_item:
                    current_error = error_item.text()
                    new_error = f"{current_error}\n{error}" if current_error else error
                    error_item.setText(new_error)
                    error_item.setForeground(QtGui.QColor("#f44336"))

            self.update_overall_progress()
            
            # Update the log text with detailed progress
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
        failed_items = 0
        
        # Count completed and failed items
        for i in range(total_items):
            process_status = self.progress_model.item(i, 6).text()
            export_status = self.progress_model.item(i, 7).text()
            
            # Consider an item complete if processing failed or both statuses are complete/failed
            if process_status == "Failed":
                failed_items += 1
                completed_items += 1
            elif process_status == "Complete" and export_status in ["Complete", "Failed"]:
                completed_items += 1
                if export_status == "Failed":
                    failed_items += 1
        
        # Calculate progress percentage
        progress_percentage = (completed_items / total_items) * 100 if total_items > 0 else 0
        self.batch_progress_bar.setValue(int(progress_percentage))

        # Update the format to show failed items
        if completed_items > 0:
            success_items = completed_items - failed_items
            # Calculate the success and failure percentages within the completed items
            success_percent_within_completed = (success_items / completed_items)
            failed_percent_within_completed = (failed_items / completed_items)

            # Update the progress bar format
            self.batch_progress_bar.setFormat(
                f"Total: {int(progress_percentage)}% (Success: {int(success_percent_within_completed * 100)}%, Failed: {int(failed_percent_within_completed * 100)}%)"
            )

            # Apply gradient over the chunk (which is up to progress_percentage of the bar)
            self.batch_progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 2px solid grey;
                    border-radius: 5px;
                    text-align: center;
                    height: 25px;
                    font-weight: bold;
                    font-size: 12px;
                    color: white;
                    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
                }}
                QProgressBar::chunk {{
                    background-color: qlineargradient(
                        x1:0, y1:0, x2:1, y2:0,
                        stop: 0 #4CAF50,
                        stop: {success_percent_within_completed:.2f} #4CAF50,
                        stop: {success_percent_within_completed:.2f} #f44336,
                        stop: 1 #f44336
                    );
                    width: 10px;
                    margin: 0.5px;
                }}
            """)
        else:
            # No items completed yet; use default style
            self.batch_progress_bar.setFormat("%p%")
            self.batch_progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid grey;
                    border-radius: 5px;
                    text-align: center;
                    height: 25px;
                    font-weight: bold;
                    font-size: 12px;
                    color: white;
                    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.8);
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                    width: 10px;
                    margin: 0.5px;
                }
            """)

        # Enable close button when complete
        if completed_items == total_items and total_items > 0:
            self.close_button.setEnabled(True)
            self.close_button.setStyleSheet("""
                QPushButton { 
                    background-color: #007ACC;
                    color: white; 
                }
                QPushButton:hover {
                    background-color: #005999;
                }
            """)

    def save_log(self):
        """Save the log text to a file."""
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Log File", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_name:
            with open(file_name, 'w') as f:
                f.write(self.log_text.toPlainText())
            logger.info(f"Log saved to {file_name}")

    def setup_connections(self):
        """Set up signal/slot connections."""
        self.save_log_button.clicked.connect(self.save_log)
        self.close_button.clicked.connect(self.close)

    @staticmethod
    def extract_name_variable(asset_name: str) -> dict:
        """Extract variables from asset name with support for all naming patterns."""
        # Clean up the name
        if asset_name.endswith('_Performance'):
            asset_name = asset_name[:-11]
        asset_name = asset_name.rstrip('_')
        
        # Define patterns for all formats
        patterns = [
            # Quad actor pattern
            r'^(?P<character>[^_]+)_S(?P<slate>\d+)_(?P<sequence>\d+)_(?P<actor1>[^_]+)_(?P<actor2>[^_]+)_(?P<actor3>[^_]+)_(?P<actor4>[^_]+)_(?P<take>\d+)(?:_(?P<subtake>\d+))?$',
            # Triple actor pattern
            r'^(?P<character>[^_]+)_S(?P<slate>\d+)_(?P<sequence>\d+)_(?P<actor1>[^_]+)_(?P<actor2>[^_]+)_(?P<actor3>[^_]+)_(?P<take>\d+)(?:_(?P<subtake>\d+))?$',
            # Dual actor pattern
            r'^(?P<character>[^_]+)_S(?P<slate>\d+)_(?P<sequence>\d+)_(?P<actor1>[^_]+)_(?P<actor2>[^_]+)_(?P<take>\d+)(?:_(?P<subtake>\d+))?$',
            # Single actor pattern
            r'^(?P<character>[^_]+)_S(?P<slate>\d+)_(?P<sequence>\d+)_(?P<actor1>[^_]+)_(?P<take>\d+)(?:_(?P<subtake>\d+))?$'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, asset_name)
            if match:
                components = match.groupdict()
                
                # Set actor count flags
                components['is_quad_actor'] = bool('actor4' in components and components['actor4'])
                components['is_triple_actor'] = bool('actor3' in components and components['actor3'] and not components.get('actor4'))
                components['is_dual_actor'] = bool('actor2' in components and components['actor2'] and not components.get('actor3'))
                components['is_single_actor'] = bool('actor1' in components and not components.get('actor2'))
                
                # Pad numbers
                if components.get('slate'):
                    components['slate'] = components['slate'].zfill(4)
                if components.get('sequence'):
                    components['sequence'] = components['sequence'].zfill(4)
                if components.get('take'):
                    components['take'] = components['take'].zfill(3)
                
                return components
        
        return None
