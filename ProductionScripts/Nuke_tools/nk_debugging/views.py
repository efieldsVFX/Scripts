from PySide2 import QtWidgets, QtCore, QtGui
from typing import Optional, Callable
from .constants import DebugActions
from .controllers import DebugController
from .exceptions import NukeDebugError
from .logger import logger

class ProgressDialog(QtWidgets.QProgressDialog):
    """Custom progress dialog with cancel support."""
    
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.setWindowModality(QtCore.Qt.WindowModal)
        self.setMinimumDuration(0)
        self.setCancelButton(None)  # Disable cancel button
        self.setAutoClose(True)
        self.setStyleSheet("QProgressDialog { min-width: 300px; }")

class DebugPanel(QtWidgets.QWidget):
    """Main debugging panel UI."""

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.controller = DebugController()
        self._setup_ui()

    def _setup_ui(self):
        """Initialize UI components."""
        self.setWindowTitle("Nuke Debugging Tool")
        layout = QtWidgets.QVBoxLayout(self)

        # Add description
        description = QtWidgets.QLabel(__description__)
        description.setWordWrap(True)
        layout.addWidget(description)

        # Add problem description field
        self.problem_field = self._create_text_field("Problem Description:")
        layout.addWidget(self.problem_field)

        # Add action buttons
        self._add_debug_buttons(layout)

        # Add status bar
        self.status_bar = QtWidgets.QStatusBar()
        layout.addWidget(self.status_bar)

    def _create_text_field(self, label: str) -> QtWidgets.QTextEdit:
        """Create a labeled text field."""
        group = QtWidgets.QGroupBox(label)
        layout = QtWidgets.QVBoxLayout()
        text_field = QtWidgets.QTextEdit()
        layout.addWidget(text_field)
        group.setLayout(layout)
        return text_field

    def _add_debug_buttons(self, layout: QtWidgets.QVBoxLayout):
        """Add all debug action buttons."""
        button_grid = QtWidgets.QGridLayout()
        
        buttons = [
            (DebugActions.GENERATE_LOG, self._on_generate_log),
            (DebugActions.LIMITED_THREADS, self._on_limit_threads),
            (DebugActions.DEFAULT_ALLOCATOR, self._on_change_allocator),
            (DebugActions.DISABLE_CAM_READ, self._on_disable_camera_read),
            (DebugActions.LOCALIZE, self._on_localize_media),
            (DebugActions.DISABLE_AUTOSAVE, self._on_disable_autosave),
            (DebugActions.DISABLE_ZDEFOCUS, self._on_disable_zdefocus),
            (DebugActions.DISABLE_POSTAGE_STAMPS, self._on_disable_stamps)
        ]

        for i, (action, callback) in enumerate(buttons):
            button = QtWidgets.QPushButton(action.value)
            button.clicked.connect(callback)
            button_grid.addWidget(button, i // 2, i % 2)

        layout.addLayout(button_grid)

    def _show_error(self, message: str):
        """Show error dialog."""
        QtWidgets.QMessageBox.critical(self, "Error", message)

    def _show_success(self, message: str):
        """Show success message in status bar."""
        self.status_bar.showMessage(message, 5000)  # Show for 5 seconds

    def _execute_with_progress(self, action: Callable, message: str):
        """Execute action with progress dialog."""
        progress = ProgressDialog(self)
        progress.setLabelText(message)
        progress.setRange(0, 0)  # Indeterminate progress
        progress.show()

        try:
            result = action()
            self._show_success(f"Operation completed successfully: {result}")
        except NukeDebugError as e:
            self._show_error(str(e))
        finally:
            progress.close()

    # Button callbacks
    def _on_generate_log(self):
        self._execute_with_progress(
            self.controller.generate_log,
            "Generating debug log..."
        )

    def _on_limit_threads(self):
        self._execute_with_progress(
            lambda: self.controller.limit_threads(4),
            "Limiting threads..."
        )

    def _on_disable_camera_read(self):
        """Disable camera read from file."""
        self._execute_with_progress(
            self.controller.disable_camera_read,
            "Disabling camera read from file..."
        )

    def _on_localize_media(self):
        """Localize media."""
        self._execute_with_progress(
            self.controller.localize_media,
            "Localizing media..."
        )

    def _on_disable_autosave(self):
        """Disable autosave."""
        self._execute_with_progress(
            self.controller.disable_autosave,
            "Disabling autosave..."
        )

    def _on_disable_zdefocus(self):
        """Disable ZDefocus nodes."""
        self._execute_with_progress(
            lambda: self.controller.disable_nodes_by_class("ZDefocus"),
            "Disabling ZDefocus nodes..."
        )

    def _on_disable_stamps(self):
        """Disable postage stamps."""
        self._execute_with_progress(
            self.controller.disable_postage_stamps,
            "Disabling postage stamps..."
        )

    def _on_change_allocator(self):
        """Change memory allocator."""
        self._execute_with_progress(
            lambda: self.controller.change_allocator("malloc"),
            "Changing memory allocator..."
        )

    def closeEvent(self, event):
        """Handle panel close event."""
        try:
            # Restore initial state when closing
            self.controller.restore_initial_state()
            logger.info("Debug panel closed, initial state restored")
        except Exception as e:
            logger.error(f"Failed to restore initial state: {e}")
        event.accept()

