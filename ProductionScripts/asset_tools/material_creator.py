import os
import sys
import logging
from qtpy.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QTreeWidget, QTreeWidgetItem,
    QHBoxLayout, QMessageBox, QMenu, QHeaderView, QApplication
)
from qtpy.QtCore import Qt, QObject, Signal
from qtpy.QtGui import QScreen
from qtpy.QtWidgets import QApplication

# Simplify logging setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

# Defining constants
name = "MaterialInstancePlugin"
classname = "MaterialInstancePluginClass"
base_path = r"\\publicstore\CG_Team_NAS\Projects\TWINKLETWINKLE_MAIN\01_ASSETS\Internal"

sys.path.append(r"C:\Program Files\Epic Games\UE_5.4\Engine\Binaries\ThirdParty\Python3\Win64\Lib\site-packages")

# Check if Unreal is available
try:
    import unreal
    UNREAL_AVAILABLE = True
except ImportError:
    UNREAL_AVAILABLE = False
    logger.warning("Unreal module not available. Some functionality may be limited.")


class MaterialInstancePluginClass(QObject):
    log_updated = Signal(str, str)

    def __init__(self, core=None):
        super().__init__()
        self.core = core
        self.version = "v1.0.0"
        
        if self.core:
            self.core.registerCallback("onProjectBrowserStartup", self.onProjectBrowserStartup, plugin=self)
            self.core.registerCallback("postInitialize", self.postInitialize, plugin=self)
        elif UNREAL_AVAILABLE:
            self.add_menu_to_unreal()

    def onProjectBrowserStartup(self, origin):
        # Check if the EDGLRD menu already exists
        edglrd_menu = next((menu for menu in origin.menubar.findChildren(QMenu) if menu.title() == "EDGLRD"), None)
        
        # If the menu doesn't exist, create it
        if not edglrd_menu:
            edglrd_menu = QMenu("EDGLRD")
            origin.menubar.addMenu(edglrd_menu)
        
        # Add the plugin-specific action to the EDGLRD menu
        edglrd_menu.addAction("UE Material Instance Creator...", self.onActionTriggered)  # For MatInsCreator_PUB
        # OR
        edglrd_menu.addAction("UE Texture Importer...", self.onActionTriggered)  # For TextureImporter_PUB

    def postInitialize(self):
        """Callback function after plugin initialization."""
        if UNREAL_AVAILABLE:
            self.add_menu_to_unreal()

    def add_menu_to_unreal(self):
        """Adds the custom menu to Unreal Editor."""
        if not UNREAL_AVAILABLE:
            logger.warning("Unreal module not available. Cannot add menu to Unreal Editor.")
            return False

        tool_menus = unreal.ToolMenus.get()
        prism_menu = tool_menus.find_menu("LevelEditor.LevelEditorToolBar.AssetsToolBar.prism")
        
        if prism_menu is not None:
            entry = unreal.ToolMenuEntry(
                name="MaterialInstanceCreator",
                type=unreal.MultiBlockType.MENU_ENTRY
            )
            entry.set_label("Create Material Instances...")
            entry.set_tool_tip("Create Material Instances for selected textures")
            
            script_string = "import MatInsCreator_PUB; MatInsCreator_PUB.run_material_instance_creator()"
            entry.set_string_command(
                unreal.ToolMenuStringCommandType.PYTHON, 
                "", 
                script_string
            )
            
            prism_menu.add_menu_entry("", entry)
            tool_menus.refresh_all_widgets()
            return True
        
        return False

    def onActionTriggered(self):
        if UNREAL_AVAILABLE:
            try:
                texture_sets = self.get_texture_sets()
                dialog = SelectionDialog(texture_sets)
                if dialog.exec_():
                    selected_texture_sets = dialog.getSelectedItems()
                    if selected_texture_sets:
                        self.select_and_launch_batch_material_maker(selected_texture_sets)
            except Exception as e:
                logger.error(f"Error during action trigger: {str(e)}", exc_info=True)
        else:
            logger.error("Unreal Engine is not available in this environment")

    def get_texture_sets(self):
        """Get all textures that don't have material instances."""
        textures = []
        asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
        
        filter = unreal.ARFilter(
            class_names=["Texture2D"],
            package_paths=["/Game/01_ASSETS/Internal"],
            recursive_paths=True
        )
        
        asset_data_list = asset_registry.get_assets(filter)
        
        for asset_data in asset_data_list:
            texture_path = asset_data.package_name
            if isinstance(texture_path, unreal.Name):
                texture_path = str(texture_path)
            texture_name = texture_path.split('/')[-1]
            texture_set = self.get_texture_set_name(texture_name)
            material_path = self.get_material_instance_path(texture_path, texture_set)
            if not unreal.EditorAssetLibrary.does_asset_exist(material_path):
                textures.append((texture_path, material_path, texture_set))
        
        return textures

    def get_texture_set_name(self, asset_name):
        if isinstance(asset_name, unreal.Name):
            asset_name = str(asset_name)
        
        if asset_name.lower().endswith("_normal_directx"):
            return asset_name[:-15]
        elif asset_name.lower().endswith(("_base_color", "_basecolor")):
            return asset_name[:-11] if asset_name.lower().endswith("_base_color") else asset_name[:-10]
        else:
            return '_'.join(asset_name.split('_')[:-1])

    def get_material_instance_path(self, texture_path, texture_set):
        """Generate the material instance path based on the texture path."""
        path_parts = texture_path.split('/')
        material_path = '/'.join(path_parts[:-1])  # Remove the texture name
        return f"{material_path}/{texture_set}_MaterialInstance"

    def select_and_launch_batch_material_maker(self, selected_texture_sets):
        textures_to_select = []
        
        for descriptor, asset_build, object_name, texture_set in selected_texture_sets:
            parent_folder = f"/Game/01_ASSETS/Internal/{descriptor}/{asset_build}/{asset_build}/{object_name}/master"
            
            asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
            
            filter = unreal.ARFilter(
                class_names=["Texture2D", "VirtualTexture2D", "TextureRenderTarget2D"],
                package_paths=[parent_folder],
                recursive_paths=True
            )
            
            asset_data_list = asset_registry.get_assets(filter)
            
            if not asset_data_list:
                continue
            
            textures = []
            for asset_data in asset_data_list:
                asset_name = str(asset_data.package_name).split('/')[-1]
                current_texture_set = self.get_texture_set_name(asset_name)
                if texture_set is None or current_texture_set == texture_set:
                    textures.append(asset_data.package_name)
            
            if textures:
                textures_to_select.extend(textures)

        if textures_to_select:
            unreal.EditorAssetLibrary.sync_browser_to_objects(textures_to_select)
            self.open_batch_material_maker_ui(textures_to_select)
        else:
            self.show_no_textures_found_message()

    def show_no_textures_found_message(self):
        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Warning)
        message_box.setText("No textures were found in the selected folder(s).")
        message_box.setInformativeText("Please make another selection.")
        message_box.setWindowTitle("No Textures Found")
        message_box.setStandardButtons(QMessageBox.Ok)
        message_box.exec_()
        
        # Reload the UI for another selection
        self.onActionTriggered()

    def getSelectedItems(self):
        selected_items = []
        for item in self.treeWidget.selectedItems():
            if item.parent() and item.parent().parent():  # This is an object or texture set
                if item.text(3):  # If it's a texture set
                    texture_set = item.text(3)
                    object_name = item.parent().text(2)
                    asset_build = item.parent().parent().text(1)
                    descriptor = item.parent().parent().parent().text(0)
                    selected_items.append((descriptor, asset_build, object_name, texture_set))
                elif item.text(2):  # If it's an object
                    object_name = item.text(2)
                    asset_build = item.parent().text(1)
                    descriptor = item.parent().parent().text(0)
                    selected_items.append((descriptor, asset_build, object_name, None))
            # Invalid selections (descriptor or asset build level)
            elif not (item.text(2) or item.text(3)):
                return []

        return selected_items

    def open_batch_material_maker_ui(self, selected_textures):
        unreal.EditorAssetLibrary.sync_browser_to_objects(selected_textures)
        
        blueprint_class = unreal.load_class(None, "/Game/BatchMaterialMaker/EUBP_BatchMaterialMaker.EUBP_BatchMaterialMaker_C")
        
        if blueprint_class is None:
            logger.error("Failed to load the Blueprint class. Please check the asset path.")
            return
        
        cdo = unreal.get_default_object(blueprint_class)
        
        try:
            cdo.call_method("Create Instanced Materials")
        except Exception as e:
            logger.error(f"Failed to call 'Create Instanced Materials' function: {str(e)}", exc_info=True)


class SelectionDialog(QDialog):
    def __init__(self, texture_sets, parent=None):
        super(SelectionDialog, self).__init__(parent)
        self.setWindowTitle("Select Texture Sets")
        self.setMinimumSize(400, 300)
        self.resize(500, 400)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint)

        layout = QVBoxLayout()

        self.treeWidget = QTreeWidget()
        self.treeWidget.setHeaderLabels(["Descriptor", "Asset Build", "Object", "Texture Set"])
        self.treeWidget.setSelectionMode(QTreeWidget.ExtendedSelection)
        layout.addWidget(self.treeWidget)

        # Build the hierarchical structure
        hierarchy = self.build_hierarchy(texture_sets)

        # Populate the tree widget
        self.populate_tree_widget(hierarchy)

        button_layout = QHBoxLayout()
        ok_button = QPushButton("Create")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        ok_button.clicked.connect(self.validate_selection)
        cancel_button.clicked.connect(self.reject)

        # Initial column width adjustment
        self.adjust_column_widths()

        # Connect the itemExpanded signal to adjust column widths
        self.treeWidget.itemExpanded.connect(self.adjust_column_widths)
        self.treeWidget.itemCollapsed.connect(self.adjust_column_widths)

        self.setLayout(layout)

        # Add horizontal scrollbar if needed
        self.treeWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.adjustSize()

    def build_hierarchy(self, texture_sets):
        hierarchy = {}
        for texture_path, material_path, texture_set in texture_sets:
            material_path = material_path.lstrip('/')  # Clean up path
            path_parts = material_path.split('/')

            if len(path_parts) >= 7:
                descriptor = path_parts[3]
                asset_build = path_parts[4]
                object_name = path_parts[6]

                hierarchy.setdefault(descriptor, {}).setdefault(asset_build, {}).setdefault(object_name, {}).setdefault(texture_set, []).append((texture_path, material_path))

        return hierarchy

    def populate_tree_widget(self, hierarchy):
        for descriptor in sorted(hierarchy.keys()):
            descriptor_item = QTreeWidgetItem([descriptor, "", "", ""])
            self.treeWidget.addTopLevelItem(descriptor_item)
            for asset_build in sorted(hierarchy[descriptor].keys()):
                asset_build_item = QTreeWidgetItem(descriptor_item, ["", asset_build, "", ""])
                for object_name in sorted(hierarchy[descriptor][asset_build].keys()):
                    object_item = QTreeWidgetItem(asset_build_item, ["", "", object_name, ""])
                    for texture_set_name in sorted(hierarchy[descriptor][asset_build][object_name].keys()):
                        texture_set_item = QTreeWidgetItem(object_item, ["", "", "", texture_set_name])

    def validate_selection(self):
        selected_items = self.getSelectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Invalid Selection", "Please select a valid object or texture set.")
        else:
            self.accept()

    def getSelectedItems(self):
        selected_items = []
        for item in self.treeWidget.selectedItems():
            if item.parent() and item.parent().parent():  # This is an object or texture set
                if item.text(3):  # If it's a texture set
                    texture_set = item.text(3)
                    object_name = item.parent().text(2)
                    asset_build = item.parent().parent().text(1)
                    descriptor = item.parent().parent().parent().text(0)
                    selected_items.append((descriptor, asset_build, object_name, texture_set))
                elif item.text(2):  # If it's an object
                    object_name = item.text(2)
                    asset_build = item.parent().text(1)
                    descriptor = item.parent().parent().text(0)
                    selected_items.append((descriptor, asset_build, object_name, None))
            # Invalid selections (descriptor or asset build level)
            elif not (item.text(2) or item.text(3)):
                return []

        return selected_items

    def adjust_column_widths(self):
        header = self.treeWidget.header()
        total_width = 0

        for i in range(4):
            self.treeWidget.resizeColumnToContents(i)
            column_width = self.treeWidget.columnWidth(i)
            total_width += column_width
            
            if i < 3:  # For the first three columns
                header.setSectionResizeMode(i, QHeaderView.Interactive)
            else:  # For the Texture Set column
                header.setSectionResizeMode(i, QHeaderView.Fixed)
            
            header.resizeSection(i, column_width)

        # Add some padding to the total width
        total_width += 50  # Adjust this value as needed

        # Get the current screen size
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            max_width = screen_geometry.width() * 0.8  # Limit to 80% of screen width
        else:
            max_width = 1600  # Fallback value if screen info is not available

        # Resize the dialog, but don't exceed the maximum width
        new_width = min(total_width, max_width)
        self.resize(new_width, self.height())

        # Adjust dialog size if needed
        self.adjustSize()


def run_material_instance_creator():
    if UNREAL_AVAILABLE:
        plugin = MaterialInstancePluginClass()
        plugin.onActionTriggered()
    else:
        logger.error("Unreal Engine is not running. Please open Unreal Engine and try again.")


def register(core):
    return MaterialInstancePluginClass(core)