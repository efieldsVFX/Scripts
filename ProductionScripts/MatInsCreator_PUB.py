import os
import sys
import logging
from qtpy.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QTreeWidget, QTreeWidgetItem,
    QHBoxLayout, QMessageBox, QMenu, QHeaderView, QApplication
)
from qtpy.QtCore import Qt, QObject, Signal
from qtpy.QtGui import QScreen

# Quick hack to get UE path - replace this with your actual path
UE_PATH = r"C:\Program Files\Epic Games\UE_5.4"
UE_SITE_PACKAGES = os.path.join(
    UE_PATH, 
    "Engine/Binaries/ThirdParty/Python3/Win64/Lib/site-packages"
)
sys.path.append(UE_SITE_PACKAGES)

# Try to import unreal - we'll need this later
try:
    import unreal
    UNREAL_AVAILABLE = True
except ImportError:
    UNREAL_AVAILABLE = False
    print("Warning: Unreal module not found - limited functionality available")

logger = logging.getLogger(__name__)

class MaterialInstancePluginClass(QObject):
    # Signal for log updates - useful for debugging
    log_updated = Signal(str, str)

    def __init__(self, core=None):
        super().__init__()
        self.core = core
        self.version = "1.0.0"  # bump this when making changes
        
        # Hook into the core if available, otherwise try direct UE integration
        if self.core:
            self._setup_core_callbacks()
        elif UNREAL_AVAILABLE:
            self.add_menu_to_unreal()

    def _setup_core_callbacks(self):
        """Sets up core integration - only called if core is available"""
        self.core.registerCallback(
            "onProjectBrowserStartup", 
            self.onProjectBrowserStartup, 
            plugin=self
        )
        self.core.registerCallback(
            "postInitialize",
            self.postInitialize,
            plugin=self
        )

    def onProjectBrowserStartup(self, origin):
        """Adds our tool to the menu bar"""
        # Find or create Tools menu
        tools_menu = next(
            (menu for menu in origin.menubar.findChildren(QMenu) 
             if menu.title() == "Tools"),
            None
        )
        
        if not tools_menu:
            tools_menu = QMenu("Tools")
            origin.menubar.addMenu(tools_menu)
        
        # Add our action
        tools_menu.addAction(
            "Material Instance Creator", 
            self.onActionTriggered
        )

    def _get_filtered_assets(self, asset_registry):
        """Gets textures from the asset registry"""
        # TODO: Make these paths configurable
        filter_params = unreal.ARFilter(
            class_names=["Texture2D"],
            package_paths=["/Game/Assets"],
            recursive_paths=True  # careful with this on large projects
        )
        return asset_registry.get_assets(filter_params)

    def _gather_textures_for_sets(self, selected_sets):
        """Collects all textures for the selected sets"""
        results = []
        
        for category, asset_type, obj_name, tex_set in selected_sets:
            try:
                # Build the path - might need to make this more flexible
                parent_path = (
                    f"/Game/Assets/{category}/"
                    f"{asset_type}/{obj_name}/master"
                )
                
                assets = self._get_assets_in_folder(parent_path)
                textures = self._filter_textures_by_set(assets, tex_set)
                results.extend(textures)
                
            except Exception as e:
                # Log and continue - don't let one failure stop everything
                logger.warning(
                    f"Failed processing set {tex_set}: {str(e)}"
                )
                continue
                
        return results

    def _launch_material_maker(self, textures):
        """Fires up the material maker with selected textures"""
        try:
            # Sync the content browser to our selection
            unreal.EditorAssetLibrary.sync_browser_to_objects(textures)
            
            # FIXME: This path should probably be configurable
            maker_path = (
                "/Game/Tools/MaterialMaker/"
                "BP_BatchMaterialMaker.BP_BatchMaterialMaker_C"
            )
            blueprint_class = unreal.load_class(None, maker_path)
            
            if not blueprint_class:
                raise RuntimeError("Can't find the MaterialMaker blueprint!")
                
            # Fire it up
            cdo = unreal.get_default_object(blueprint_class)
            cdo.call_method("Create Instanced Materials")
            
        except Exception as e:
            raise RuntimeError(f"Material maker failed: {str(e)}")

# More code below...