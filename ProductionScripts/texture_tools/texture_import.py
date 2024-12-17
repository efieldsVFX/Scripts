"""
Texture importer module for handling multi-threaded texture imports.
Provides thread-safe importing of textures into Unreal Engine.
"""

import os
import math
import logging
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from PySide2.QtCore import QObject, QThread, QEventLoop, Qt
from PySide2.QtWidgets import (
    QDialog, QMessageBox, QVBoxLayout, QHBoxLayout, 
    QPushButton, QTreeWidget, QTreeWidgetItem
)

# Configure logging
logger = logging.getLogger(__name__)

class TextureImporterWorker(QObject):
    """Worker class for handling texture imports in a separate thread."""
    
    def __init__(self, parent, selected_paths, auto_create_folders=False):
        """Initialize the worker with import parameters."""
        super().__init__()
        self.parent = parent
        self.selected_paths = selected_paths
        self.import_list = []
        self._thread = None
        self._io_worker = None
        self.auto_create_folders = auto_create_folders
        self._lock = Lock()
        self._is_running = False
        
    def start_import(self):
        """Start the import process in a thread-safe manner."""
        with self._lock:
            if self._is_running:
                logger.warning("Import already in progress")
                return False
                
            self._is_running = True
            try:
                self._prepare_import_list()
                success = self._import_textures()
                return success
            finally:
                self._is_running = False

    def _import_textures(self):
        """Import textures with thread safety and progress tracking."""
        total_steps = len(self.import_list)
        current_step = 0
        
        with self._lock:
            for source_path, destination_path, texture_set, master_path in self.import_list:
                try:
                    current_step += 1
                    progress = int((current_step / total_steps) * 100)
                    self.progress_updated.emit(progress)
                    
                    logger.debug(f"Starting import of texture set {texture_set}")
                    
                    if not self._check_unreal_available():
                        return False
                        
                    if not self._import_texture_set(source_path, destination_path, texture_set):
                        logger.error(f"Failed to import texture set: {texture_set}")
                        continue
                        
                except Exception as e:
                    logger.exception(f"Error importing texture set {texture_set}: {str(e)}")
                    continue
                    
        return True

    def _check_unreal_available(self):
        """Check if Unreal Engine is available."""
        if not UNREAL_AVAILABLE:
            self.log_updated.emit(
                "Unreal Engine is not available. Import cancelled.",
                "Error"
            )
            return False
        return True

    def _import_texture_set(self, source_path, destination_path, texture_set):
        """Import a single texture set with proper folder handling."""
        try:
            destination_folder = unreal.Paths.get_path(destination_path)
            if not unreal.EditorAssetLibrary.does_directory_exist(destination_folder):
                if self.auto_create_folders:
                    logger.info(f"Auto-creating folder: {destination_folder}")
                    unreal.EditorAssetLibrary.make_directory(destination_folder)
                elif not self._confirm_folder_creation(destination_folder):
                    return False

            # Import texture logic here
            return True

        except Exception as e:
            logger.exception(f"Error importing texture set {texture_set}")
            return False

    def _confirm_folder_creation(self, folder_path):
        """Thread-safe folder creation confirmation."""
        if self.auto_create_folders:
            return True
            
        display_path = folder_path.replace("/Game/", "/Content/")
        result = None
        
        if QThread.currentThread() is QApplication.instance().thread():
            result = self._show_confirmation_dialog(display_path)
        else:
            QMetaObject.invokeMethod(
                self,
                "_show_confirmation_dialog",
                Qt.BlockingQueuedConnection,
                Q_RETURN_ARG(bool),
                Q_ARG(str, display_path)
            )
        return result

    def cleanup(self):
        """Clean up resources when worker is done."""
        with self._lock:
            if self._thread:
                self._thread.quit()
                self._thread.wait()
            self._is_running = False

class TextureImporterClass:
    """Main texture importer class."""
    
    def __init__(self):
        """Initialize the importer with thread safety."""
        self._import_lock = Lock()
        self._worker = None
        self._progress_dialog = None
        
    def start_import(self, selected_items, auto_create_folders=False):
        """Start the import process with batching and thread safety."""
        try:
            with self._import_lock:
                if not self._check_prerequisites():
                    return
                    
                self._process_batches(selected_items, auto_create_folders)
                
        except Exception as e:
            logger.exception("Import process failed")
            self.show_console_output(
                f"Critical error during import process: {str(e)}",
                "Error"
            )

    def _check_prerequisites(self):
        """Check if system meets requirements for import."""
        if not UNREAL_AVAILABLE:
            self.show_console_output(
                "Unreal Engine is not available. Please run this tool from within Unreal Editor.",
                "Error"
            )
            return False
        return True

    def _process_batches(self, selected_items, auto_create_folders):
        """Process items in batches for better memory management."""
        batch_size = 100
        total_batches = math.ceil(len(selected_items) / batch_size)
        
        for batch_num in range(total_batches):
            if not self._process_single_batch(
                selected_items, batch_num, batch_size, 
                total_batches, auto_create_folders
            ):
                break

    def _show_confirmation_dialog(self, display_path):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setText(f"The folder '{display_path}' does not exist.")
        msg_box.setInformativeText("Do you want to create the folder?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.Yes)
        
        result = msg_box.exec_()
        if result == QMessageBox.No:
            self.log_updated.emit("Folder creation cancelled by user.", "Info")
            return False
        return True

    def cleanup(self):
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
        self.io_worker = None
        self.thread = None

class IOWorker(QObject):
    io_completed = Signal(list)
    log_updated = Signal(str, str)

    def __init__(self, selected_paths):
        super().__init__()
        self.selected_paths = selected_paths

    def run(self):
        import_list = []
        for item in self.selected_paths:
            try:
                source_path, ue_path, texture_set, master_path, display_ue_path = item
                
                if not os.path.exists(master_path):
                    self.log_updated.emit(f"Master path does not exist: {master_path}", "Error")
                    continue

                texture_files = self.get_texture_files(master_path, texture_set)
                if not texture_files:
                    self.log_updated.emit(f"No texture files found for set {texture_set} in {master_path}", "Warning")
                    continue

                import_list.append((source_path, ue_path, texture_set, master_path, display_ue_path))

            except Exception as e:
                self.log_updated.emit(f"Error preparing import for path {item}: {str(e)}", "Error")
        
        self.io_completed.emit(import_list)

    def get_texture_files(self, master_path, texture_set):
        texture_files = [f for f in os.listdir(master_path) if f.startswith(texture_set) and f.lower().endswith(('.png', '.jpg', '.jpeg', '.tga', '.exr'))]
        return texture_files

class TextureImporterClass:
    def __init__(self, core=None):
        self.core = core
        self.version = "v1.2.1"
        self.progress_dialog = None
        self._import_lock = Lock()

        if self.core:
            self.core.registerCallback("onProjectBrowserStartup", self.onProjectBrowserStartup, plugin=self)
            self.core.registerCallback("postInitialize", self.postInitialize, plugin=self)
        else:
            if UNREAL_AVAILABLE:
                self.add_menu_to_unreal()

    def onProjectBrowserStartup(self, origin):
        tools_menu = next((menu for menu in origin.menubar.findChildren(QMenu) if menu.title() == "Tools"), None)
        
        if not tools_menu:
            tools_menu = QMenu("Tools")
            origin.menubar.addMenu(tools_menu)
        
        tools_menu.addAction("UE Texture Importer...", self.onActionTriggered)
        tools_menu.addAction("UE Material Instance Creator...", self.onActionTriggered)

    def postInitialize(self):
        if UNREAL_AVAILABLE:
            self.add_menu_to_unreal()

    def add_menu_to_unreal(self, max_attempts=10, delay=1):
        for attempt in range(max_attempts):
            tool_menus = unreal.ToolMenus.get()
            prism_menu = tool_menus.find_menu("LevelEditor.LevelEditorToolBar.AssetsToolBar.prism")
            
            if prism_menu is not None:
                entry = unreal.ToolMenuEntry(
                    name="TextureImporter",
                    type=unreal.MultiBlockType.MENU_ENTRY
                )
                entry.set_label("UE Texture Importer...")
                entry.set_tool_tip("Import or Update textures into Unreal Engine")
                
                script_string = "import TextureImporter_PUB; TextureImporter_PUB.run_texture_importer()"
                entry.set_string_command(
                    unreal.ToolMenuStringCommandType.PYTHON, 
                    "", 
                    script_string
                )
                
                try:
                    prism_menu.add_menu_entry("", entry)
                    tool_menus.refresh_all_widgets()
                    return True
                except Exception as e:
                    return False
            
            time.sleep(delay)
        
        return False

    def retry_add_menu_entry(self):
        if self.add_menu_to_unreal():
            pass
        else:
            unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_timer_manager().set_timer_for_next_tick(self.retry_add_menu_entry)

    def onActionTriggered(self):
        if UNREAL_AVAILABLE:
            try:
                descriptors = self.getAssetBuildsAndObjects(base_path)
                dialog = SelectionDialog(descriptors)
                if dialog.exec_():
                    selected_items = dialog.getSelectedItems()
                    if len(selected_items) > 100:
                        if not self.confirm_large_selection(len(selected_items)):
                            return
                    confirmation_dialog = ConfirmationDialog(None, selected_items)
                    if confirmation_dialog.exec_():
                        self.start_import(selected_items)
                    else:
                        self.show_console_output("User canceled the import process.", "Info")
            except Exception as e:
                self.show_console_output(f"Error during action trigger: {str(e)}", "Error")
        else:
            self.show_console_output("Unreal Engine is not available in this environment.", "Error")

    def confirm_large_selection(self, item_count):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(f"You have selected {item_count} items to import.")
        msg.setInformativeText("This may take a long time and consume significant resources. Do you want to continue?")
        msg.setWindowTitle("Large Selection Warning")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        return msg.exec_() == QMessageBox.Yes

    def start_import(self, selected_items, auto_create_folders=False):
        try:
            with self._import_lock:
                batch_size = 100
                total_batches = math.ceil(len(selected_items) / batch_size)
                
                if not UNREAL_AVAILABLE:
                    self.show_console_output(
                        "Unreal Engine is not available. Please run this tool from within Unreal Editor.",
                        "Error"
                    )
                    return
                
                for batch_num in range(total_batches):
                    start_idx = batch_num * batch_size
                    end_idx = min((batch_num + 1) * batch_size, len(selected_items))
                    batch_items = selected_items[start_idx:end_idx]
                    
                    self.worker = TextureImporterWorker(
                        self,
                        batch_items,
                        auto_create_folders=auto_create_folders
                    )
                    self.worker.progress_updated.connect(self.update_progress)
                    self.worker.log_updated.connect(self.show_console_output)
                    self.worker.task_completed.connect(self.on_batch_completed)

                    self.show_progress_dialog(f"Texture Import Progress (Batch {batch_num + 1}/{total_batches})", "Starting import...")
                    self.worker.start_import()
                    
                    loop = QEventLoop()
                    self.worker.task_completed.connect(loop.quit)
                    loop.exec_()
                
        except Exception as e:
            self.show_console_output(
                f"Critical error during import process: {str(e)}",
                "Error"
            )
            logger.exception("Import process failed")

    def on_batch_completed(self):
        if self.progress_dialog:
            self.progress_dialog.close()
        self.worker.cleanup()

    def on_task_completed(self):
        if self.progress_dialog:
            self.progress_dialog.close()
        QMessageBox.information(None, "Import Complete", "The texture import process has been completed successfully.")

    def getAssetBuildsAndObjects(self, base_path):
        descriptors = {}
        for descriptor in os.listdir(base_path):
            descriptor_path = os.path.join(base_path, descriptor, "01_TEXTURES")
            if os.path.isdir(descriptor_path):
                builds = {}
                for build in os.listdir(descriptor_path):
                    build_path = os.path.join(descriptor_path, build, "Textures")
                    if os.path.isdir(build_path):
                        objects = {}
                        for obj in os.listdir(build_path):
                            obj_path = os.path.join(build_path, obj)
                            if os.path.isdir(obj_path):
                                objects[obj] = obj_path
                        if objects:
                            builds[build] = objects
                if builds:
                    descriptors[descriptor] = builds
        return descriptors

    def update_progress(self, value):
        if self.progress_dialog:
            self.progress_dialog.progress_bar.setValue(value)
            if value == 100:
                self.progress_dialog.label.setText("Process completed")

    def show_progress_dialog(self, title, initial_message):
        self.progress_dialog = ProgressDialog(title, initial_message)
        self.progress_dialog.show()

    def show_console_output(self, message, level):
        print(f"[{level}] {message}")

    def getUEPath(self, asset_path, object_name):
        try:
            path_parts = asset_path.split(os.sep)
            category = path_parts[-5]
            asset_type = path_parts[-3]
            ue_path = f"/Game/Assets/Internal/{category}/{asset_type}/{asset_type}/{object_name}/master"
            return ue_path.replace("\\", "/")
        except Exception as e:
            self.show_console_output(f"Error mapping path: {str(e)}", "Error")
            return None

    def on_batch_completed(self):
        if self.progress_dialog:
            self.progress_dialog.close()
        self.worker.cleanup()
        self.check_material_instances()

    def check_material_instances(self):
        if not UNREAL_AVAILABLE:
            return

        missing_material_instances = []
        for item in self.worker.import_list:
            source_path, ue_path, texture_set, master_path, _ = item
            material_instance_path = f"{ue_path}/{texture_set}_MaterialInstance"
            if not unreal.EditorAssetLibrary.does_asset_exist(material_instance_path):
                missing_material_instances.append(texture_set)

        if missing_material_instances:
            message = f"The following texture sets do not have material instances:\n\n"
            message += "\n".join(missing_material_instances)
            message += "\n\nWould you like to launch the material instance creator now?"

            reply = QMessageBox.question(None, "Missing Material Instances", message, 
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

            if reply == QMessageBox.Yes:
                self.launch_material_instance_creator(missing_material_instances)

    def launch_material_instance_creator(self, missing_texture_sets):
        try:
            # Close the current progress dialog if it exists
            if self.progress_dialog:
                self.progress_dialog.close()
                self.progress_dialog = None

            # Clean up any remaining workers
            if hasattr(self, 'worker'):
                self.worker.cleanup()
                self.worker = None

            # Run the material instance creator
            import MatInsCreator_PUB
            MatInsCreator_PUB.run_material_instance_creator()

        except Exception as e:
            self.show_console_output(f"Error launching material instance creator: {str(e)}", "Error")

class SelectionDialog(QDialog):
    def __init__(self, descriptors, parent=None):
        super(SelectionDialog, self).__init__(parent)
        self.setWindowTitle("Select Asset Builds and Object Names")
        self.selected_items = []

        layout = QVBoxLayout()

        self.treeWidget = QTreeWidget()
        self.treeWidget.setHeaderLabels(["Asset"])
        self.treeWidget.setSelectionMode(QTreeWidget.MultiSelection)
        layout.addWidget(self.treeWidget)

        for descriptor, builds in descriptors.items():
            descriptor_item = QTreeWidgetItem([descriptor])
            self.treeWidget.addTopLevelItem(descriptor_item)
            for build, objects in builds.items():
                build_item = QTreeWidgetItem(descriptor_item, [build])
                for obj, obj_path in objects.items():
                    obj_item = QTreeWidgetItem(build_item, [obj])
                    master_path = os.path.join(obj_path, 'master')
                    texture_sets = self.get_texture_sets(master_path)
                    for texture_set in texture_sets:
                        texture_set_item = QTreeWidgetItem(obj_item, [texture_set])

        self.treeWidget.expandAll()
        self.treeWidget.resizeColumnToContents(0)

        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        self.setLayout(layout)

    def get_texture_sets(self, master_path):
        texture_sets = set()
        if os.path.exists(master_path):
            for file in os.listdir(master_path):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.tga', '.exr')):
                    set_name = '_'.join(file.split('_')[:-1])
                    texture_sets.add(set_name)
        return texture_sets

    def getSelectedItems(self):
        selected_items = []
        for item in self.treeWidget.selectedItems():
            self.collectSelectedItems(item, selected_items)
        return selected_items

    def collectSelectedItems(self, item, selected_items):
        if item.parent() is None:  # Descriptor level
            descriptor = item.text(0)
            self.addDescriptorItems(descriptor, selected_items)
        elif item.parent().parent() is None:  # Asset Build level
            descriptor = item.parent().text(0)
            build = item.text(0)
            self.addBuildItems(descriptor, build, selected_items)
        elif item.parent().parent().parent() is None:  # Object Name level
            descriptor = item.parent().parent().text(0)
            build = item.parent().text(0)
            obj = item.text(0)
            self.addObjectItems(descriptor, build, obj, selected_items)
        else:  # Texture set level
            self.addTextureSetItem(item, selected_items)

    def addDescriptorItems(self, descriptor, selected_items):
        descriptor_path = os.path.join(base_path, descriptor, "01_TEXTURES")
        for build in os.listdir(descriptor_path):
            build_path = os.path.join(descriptor_path, build, "Textures")
            if os.path.isdir(build_path):
                for obj in os.listdir(build_path):
                    obj_path = os.path.join(build_path, obj)
                    if os.path.isdir(obj_path):
                        master_path = os.path.join(obj_path, 'master')
                        if os.path.isdir(master_path):
                            self.addMasterFolderItems(descriptor, build, obj, master_path, selected_items)

    def addBuildItems(self, descriptor, build, selected_items):
        build_path = os.path.join(base_path, descriptor, "01_TEXTURES", build, "Textures")
        for obj in os.listdir(build_path):
            obj_path = os.path.join(build_path, obj)
            if os.path.isdir(obj_path):
                master_path = os.path.join(obj_path, 'master')
                if os.path.isdir(master_path):
                    self.addMasterFolderItems(descriptor, build, obj, master_path, selected_items)

    def addObjectItems(self, descriptor, build, obj, selected_items):
        master_path = os.path.join(base_path, descriptor, "01_TEXTURES", build, "Textures", obj, 'master')
        if os.path.isdir(master_path):
            self.addMasterFolderItems(descriptor, build, obj, master_path, selected_items)

    def addMasterFolderItems(self, descriptor, build, obj, master_path, selected_items):
        texture_sets = self.get_texture_sets(master_path)
        for texture_set in texture_sets:
            source_path = f"{obj} / {texture_set}"
            ue_path = f"/Game/Assets/Internal/{descriptor}/{build}/{build}/{obj}/master"
            display_ue_path = display_path(ue_path)
            selected_items.append((source_path, ue_path, texture_set, master_path, display_ue_path))

    def addTextureSetItem(self, item, selected_items):
        texture_set = item.text(0)
        obj = item.parent().text(0)
        build = item.parent().parent().text(0)
        descriptor = item.parent().parent().parent().text(0)
        
        source_path = f"{obj} / {texture_set}"
        ue_path = f"/Game/Assets/Internal/{descriptor}/{build}/{build}/{obj}/master"
        display_ue_path = display_path(ue_path)
        master_path = os.path.join(base_path, descriptor, "01_TEXTURES", build, "Textures", obj, "master")
        selected_items.append((source_path, ue_path, texture_set, master_path, display_ue_path))

class ConfirmationDialog(QDialog):
    def __init__(self, parent, selected_items):
        super().__init__(parent)
        self.setWindowTitle("Confirm Import")
        layout = QVBoxLayout(self)

        self.table = QTableWidget(self)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Source", "Destination", "Texture Set"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        for source_path, ue_path, texture_set, _, display_ue_path in selected_items:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(source_path))
            self.table.setItem(row, 1, QTableWidgetItem(display_ue_path))
            self.table.setItem(row, 2, QTableWidgetItem(texture_set))

        layout.addWidget(self.table)

        button_layout = QHBoxLayout()
        confirm_button = QPushButton("Confirm")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(confirm_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        confirm_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

class ProgressDialog(QDialog):
    def __init__(self, title, initial_message, parent=None):
        super(ProgressDialog, self).__init__(parent)
        self.setWindowTitle(title)
        layout = QVBoxLayout()

        self.label = QLabel(initial_message)
        layout.addWidget(self.label)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)
        self.setMinimumWidth(500)

def run_texture_importer():
    texture_importer = TextureImporterClass(None)
    texture_importer.onActionTriggered()

def register(core):
    importer = TextureImporterClass(core)
    if not importer.add_menu_to_unreal():
        unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_timer_manager().set_timer_for_next_tick(importer.retry_add_menu_entry)
    return importer
