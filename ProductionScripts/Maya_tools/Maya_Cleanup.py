"""Maya scene cleanup utility for managing and optimizing Maya scenes."""

# Standard library imports
import json
import logging
import os
from datetime import datetime
from functools import wraps

# Third-party imports
from PySide2 import QtCore, QtWidgets
import maya.cmds as cmds
import maya.mel as mel


# Config Management Class
class Config:
    """Configuration management for the Maya Scene Cleanup utility."""

    CONFIG_FILE = "render_cleaner_config.json"
    BACKUP_DIR = "backups"
    LOG_DIR = "logs"
    
    DEFAULT_CONFIG = {
        "protected_nodes": [
            "defaultRenderLayer",
        ],
        "protected_materials": [
            "lambert1",
        ],
        "backup_enabled": True,
        "log_to_file": True,
    }

    @classmethod
    def setup_dirs(cls) -> None:
        """Create necessary directories for backups and logs."""
        os.makedirs(cls.BACKUP_DIR, exist_ok=True)
        os.makedirs(cls.LOG_DIR, exist_ok=True)
        
    @classmethod
    def get_backup_path(cls) -> str:
        """Generate backup file path with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        scene_name = os.path.splitext(
            os.path.basename(cmds.file(q=True, sn=True))
        )[0]
        return os.path.join(cls.BACKUP_DIR, f"{scene_name}_{timestamp}.mb")

    @classmethod
    def load(cls) -> dict:
        """Load configuration from file or return defaults."""
        if os.path.exists(cls.CONFIG_FILE):
            try:
                with open(cls.CONFIG_FILE, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logging.error("Failed to load config. Using default.")
        return cls.DEFAULT_CONFIG


# Safety Decorator
def safe_operation(func):
    """Decorator to ensure safe execution of Maya operations."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            config = Config.load()
            if config["backup_enabled"]:
                Config.setup_dirs()
                backup_path = Config.get_backup_path()
                cmds.file(rename=backup_path)
                cmds.file(save=True, type="mayaAscii")
                cmds.file(rename=cmds.file(q=True, sn=True))
            
            cmds.undoInfo(openChunk=True)
            result = func(*args, **kwargs)
            cmds.undoInfo(closeChunk=True)
            return result
        except Exception as e:
            cmds.undoInfo(closeChunk=True)
            logging.exception(f"Error in {func.__name__}: {str(e)}")
            raise
    return wrapper


# Maya Scene Cleanup Class
class MayaCleanup:
    """Handles Maya scene cleanup operations."""

    @staticmethod
    @safe_operation
    def delete_nodes(node_type: str, protected: list = None) -> None:
        """Delete nodes of specified type, excluding protected nodes."""
        if protected is None:
            protected = []
        nodes = cmds.ls(type=node_type) or []
        nodes_to_delete = [n for n in nodes if n not in protected]
        if nodes_to_delete:
            cmds.delete(nodes_to_delete)
            logging.info(
                f"Deleted nodes of type {node_type}: {nodes_to_delete}"
            )
        else:
            logging.info(f"No nodes of type {node_type} to delete.")

    @staticmethod
    @safe_operation
    def delete_unknown_plugins() -> None:
        """Remove all unknown plugins from the scene."""
        unknown_plugins = cmds.unknownPlugin(q=True, l=True) or []
        for plugin in unknown_plugins:
            cmds.unknownPlugin(plugin, r=True)
            logging.info(f"Removed unknown plugin: {plugin}")

    @staticmethod
    @safe_operation
    def delete_unused_materials() -> None:
        """Remove materials that aren't connected to any objects."""
        materials = cmds.ls(mat=True) or []
        protected = Config.load()["protected_materials"]
        materials_to_delete = [
            m for m in materials if m not in protected and not cmds.listConnections(m, s=False, d=True)
        ]
        if materials_to_delete:
            cmds.delete(materials_to_delete)
            logging.info(f"Deleted unused materials: {materials_to_delete}")
        else:
            logging.info("No unused materials found.")

    @staticmethod
    @safe_operation
    def delete_render_layers() -> None:
        """Delete all render layers except protected ones."""
        render_layers = cmds.ls(type="renderLayer") or []
        protected = Config.load()["protected_nodes"]
        for layer in render_layers:
            if layer not in protected:
                cmds.delete(layer)
                logging.info(f"Deleted render layer: {layer}")
        mel.eval('setAttr "defaultRenderLayer.renderable" 0')

    @staticmethod
    @safe_operation
    def fix_render_layer_errors() -> None:
        """Fix common render layer errors."""
        try:
            mel.eval("fixRenderLayerOutAdjustmentErrors()")
            logging.info("Fixed render layer errors.")
        except Exception as e:
            logging.error(f"Failed to fix render layer errors: {e}")


# UI Class for User Interaction
class RenderCleanupUI(QtWidgets.QDialog):
    """User interface for Maya scene cleanup operations."""

    def __init__(self, parent=None):
        """Initialize the cleanup UI."""
        super(RenderCleanupUI, self).__init__(parent)
        self.setWindowTitle("Maya Scene Cleanup")
        self.setMinimumWidth(400)
        self.create_layout()
        self.create_connections()
        
        if Config.load()["log_to_file"]:
            Config.setup_dirs()
            log_file = os.path.join(
                Config.LOG_DIR,
                f"cleanup_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )
            logging.basicConfig(
                filename=log_file,
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )

    def create_layout(self):
        """Create and setup the UI layout."""
        main_layout = QtWidgets.QVBoxLayout(self)
        
        info_label = QtWidgets.QLabel(
            "Select cleanup operations to perform. "
            "All operations will show a preview before executing."
        )
        info_label.setWordWrap(True)
        main_layout.addWidget(info_label)
        
        # Create UI groups
        self._create_scene_group(main_layout)
        self._create_tech_group(main_layout)
        self._create_full_group(main_layout)
        self._create_progress_group(main_layout)
        self._create_bottom_buttons(main_layout)

    def _create_scene_group(self, main_layout):
        """Create scene elements group."""
        scene_group = QtWidgets.QGroupBox("Scene Elements")
        scene_layout = QtWidgets.QVBoxLayout()
        
        self.clean_audio_btn = QtWidgets.QPushButton("Remove Audio Nodes")
        self.clean_audio_btn.setToolTip("Removes all audio nodes from the scene")
        
        self.clean_materials_btn = QtWidgets.QPushButton(
            "Remove Unused Materials"
        )
        self.clean_materials_btn.setToolTip(
            "Removes materials not assigned to any objects"
        )
        
        scene_layout.addWidget(self.clean_audio_btn)
        scene_layout.addWidget(self.clean_materials_btn)
        scene_group.setLayout(scene_layout)
        main_layout.addWidget(scene_group)

    def _create_tech_group(self, main_layout):
        """Create technical cleanup group."""
        tech_group = QtWidgets.QGroupBox("Technical Cleanup")
        tech_layout = QtWidgets.QVBoxLayout()
        
        self.remove_plugins_btn = QtWidgets.QPushButton("Remove Unknown Plugins")
        self.remove_plugins_btn.setToolTip(
            "Removes references to missing plugins"
        )
        
        self.fix_render_layers_btn = QtWidgets.QPushButton(
            "Fix Render Layer Issues"
        )
        self.fix_render_layers_btn.setToolTip(
            "Attempts to fix common render layer problems"
        )
        
        tech_layout.addWidget(self.remove_plugins_btn)
        tech_layout.addWidget(self.fix_render_layers_btn)
        tech_group.setLayout(tech_layout)
        main_layout.addWidget(tech_group)

    def _create_full_group(self, main_layout):
        """Create full scene cleanup group."""
        full_group = QtWidgets.QGroupBox("Full Scene Cleanup")
        full_layout = QtWidgets.QVBoxLayout()
        
        self.clean_scene_btn = QtWidgets.QPushButton("Clean Full Scene")
        self.clean_scene_btn.setToolTip("Performs all cleanup operations")
        
        full_layout.addWidget(self.clean_scene_btn)
        full_group.setLayout(full_layout)
        main_layout.addWidget(full_group)

    def _create_progress_group(self, main_layout):
        """Create progress group."""
        progress_group = QtWidgets.QGroupBox("Progress")
        progress_layout = QtWidgets.QVBoxLayout()
        
        self.progress_bar = QtWidgets.QProgressBar()
        self.status_label = QtWidgets.QLabel("Ready")
        
        progress_layout.addWidget(self.status_label)
        progress_layout.addWidget(self.progress_bar)
        progress_group.setLayout(progress_layout)
        main_layout.addWidget(progress_group)

    def _create_bottom_buttons(self, main_layout):
        """Create bottom buttons."""
        button_layout = QtWidgets.QHBoxLayout()
        self.close_btn = QtWidgets.QPushButton("Close")
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        main_layout.addLayout(button_layout)

    def create_connections(self):
        """Create signal connections for UI elements."""
        self.clean_audio_btn.clicked.connect(
            lambda: self.run_task(self.clean_audio)
        )
        self.clean_materials_btn.clicked.connect(
            lambda: self.run_task(self.clean_materials)
        )
        self.remove_plugins_btn.clicked.connect(
            lambda: self.run_task(self.clean_plugins)
        )
        self.fix_render_layers_btn.clicked.connect(
            lambda: self.run_task(self.fix_render_layers)
        )
        self.clean_scene_btn.clicked.connect(
            lambda: self.run_task(self.clean_scene)
        )
        self.close_btn.clicked.connect(self.close)

    def update_status(self, message: str) -> None:
        """Update the status label and process events."""
        self.status_label.setText(message)
        QtWidgets.QApplication.processEvents()

    def run_task(self, task_func) -> None:
        """Execute a cleanup task with progress updates."""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.update_status("Analyzing scene...")
        
        # Preview changes
        preview_items = task_func(preview=True)
        if not any(preview_items.values()):
            QtWidgets.QMessageBox.information(
                self,
                "No Changes",
                "No items found that need cleanup."
            )
            self.progress_bar.setVisible(False)
            self.update_status("Ready")
            return
            
        dialog = PreviewDialog(preview_items, self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.update_status("Cleaning scene...")
            self.progress_bar.setValue(50)
            task_func(preview=False)
            self.progress_bar.setValue(100)
            self.update_status("Cleanup complete")
        else:
            self.update_status("Operation cancelled")
            
        self.progress_bar.setVisible(False)

    @safe_operation
    def clean_audio(self, preview: bool = True) -> dict:
        """Clean audio nodes from the scene."""
        nodes = cmds.ls(type="audio") or []
        if preview:
            return {"Audio Nodes": nodes}
        if nodes:
            cmds.delete(nodes)
            logging.info(f"Deleted audio nodes: {nodes}")
        return {}

    @safe_operation
    def clean_materials(self, preview: bool = True) -> dict:
        """Clean unused materials from the scene."""
        materials = cmds.ls(mat=True) or []
        protected = Config.load()["protected_materials"]
        to_delete = [
            m for m in materials 
            if m not in protected 
            and not cmds.listConnections(m, s=False, d=True)
        ]
        
        if preview:
            return {"Unused Materials": to_delete}
            
        if to_delete:
            cmds.delete(to_delete)
            logging.info(f"Deleted unused materials: {to_delete}")
        return {}

    @safe_operation
    def clean_plugins(self, preview: bool = True) -> dict:
        """Clean unknown plugins from the scene."""
        unknown_plugins = cmds.unknownPlugin(q=True, l=True) or []
        
        if preview:
            return {"Unknown Plugins": unknown_plugins}
            
        for plugin in unknown_plugins:
            cmds.unknownPlugin(plugin, r=True)
            logging.info(f"Removed unknown plugin: {plugin}")
        return {}

    @safe_operation
    def clean_scene(self, preview: bool = True) -> dict:
        """Perform full scene cleanup."""
        preview_items = {}
        
        # Collect all items to be cleaned
        preview_items.update(self.clean_audio(preview=True))
        preview_items.update(self.clean_materials(preview=True))
        preview_items.update(self.clean_plugins(preview=True))
        
        if preview:
            return preview_items
            
        # Execute all cleanup tasks
        self.clean_audio(preview=False)
        self.clean_materials(preview=False)
        self.clean_plugins(preview=False)
        return {}


class PreviewDialog(QtWidgets.QDialog):
    """Dialog for previewing changes before execution."""

    def __init__(
        self,
        items_to_delete: dict,
        parent: QtWidgets.QWidget = None
    ) -> None:
        """Initialize the preview dialog."""
        super(PreviewDialog, self).__init__(parent)
        self.setWindowTitle("Preview Changes")
        self.resize(500, 400)
        
        self._create_layout(items_to_delete)
        self._create_connections()

    def _create_layout(self, items_to_delete: dict) -> None:
        """Create the dialog layout."""
        layout = QtWidgets.QVBoxLayout(self)
        
        # Preview list
        self.list_widget = QtWidgets.QListWidget()
        for category, items in items_to_delete.items():
            self.list_widget.addItem(f"=== {category} ===")
            for item in items:
                self.list_widget.addItem(f"  • {item}")
        
        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        self.proceed_btn = QtWidgets.QPushButton("Proceed")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        
        btn_layout.addWidget(self.proceed_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addWidget(self.list_widget)
        layout.addLayout(btn_layout)

    def _create_connections(self) -> None:
        """Create signal connections."""
        self.proceed_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)


def main() -> None:
    """Main entry point for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    try:
        app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        win = RenderCleanupUI()
        win.show()
        app.exec_()
    except Exception as e:
        logging.exception(f"Application failed: {e}")


if __name__ == "__main__":
    main()
