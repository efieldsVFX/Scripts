"""Asset processor for handling Unreal Engine assets."""

import unreal
from ..utils.logging_config import logger
from ..utils.constants import (
    NAME_PATTERNS,
    ACTOR_CHARACTER_MAPPING,
    SEQUENCE_MAPPING,
    MHID_MAPPING,
    MOCAP_BASE_PATH
)

class AssetProcessor:
    def __init__(self):
        self.asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
        self.asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        self.name_patterns = NAME_PATTERNS
        self.actor_character_mapping = ACTOR_CHARACTER_MAPPING

    def get_sub_paths(self, base_path, recurse=True):
        """Get all sub paths from a base path."""
        return self.asset_registry.get_sub_paths(base_path, recurse=recurse)

    def get_assets_by_path(self, path, recursive=True):
        """Get all assets in a path."""
        return self.asset_registry.get_assets_by_path(path, recursive)

    def get_available_folders(self):
        logger.info("Fetching available folders...")
        # Use the method signature as in Batch_Face_Importer_PUB_updated_v4.py
        full_paths = self.get_sub_paths(MOCAP_BASE_PATH, recurse=True)

        # Filter and clean paths to only show from "Mocap" forward
        cleaned_paths = []
        for path in full_paths:
            if "Mocap" in path:
                # Find the index of "Mocap" in the path
                mocap_index = path.find("Mocap")
                # Get everything from "Mocap" forward
                cleaned_path = path[mocap_index:]
                if self.folder_has_capture_data(path):  # Still check using full path
                    cleaned_paths.append(cleaned_path)

        logger.info(f"Found {len(cleaned_paths)} folders with capture data")
        return cleaned_paths

    def get_capture_data_assets(self, folder):
        """Get all capture data assets from a folder."""
        logger.info(f"Searching for assets in folder: {folder}")

        # Ensure the folder path is properly formatted
        folder_path = str(folder)
        # Remove base path prefix if it exists
        if folder_path.startswith(f'{MOCAP_BASE_PATH}/'):
            folder_path = folder_path[len(f'{MOCAP_BASE_PATH}/'):]

        # Add the proper base path prefix
        folder_path = f"{MOCAP_BASE_PATH}/{folder_path.strip('/')}"

        logger.info(f"Searching with formatted path: {folder_path}")

        search_filter = unreal.ARFilter(
            package_paths=[folder_path],
            class_names=["FootageCaptureData"],
            recursive_paths=True,  # Enable recursive search
            recursive_classes=True
        )

        try:
            assets = self.asset_registry.get_assets(search_filter)
            logger.info(f"Found {len(assets)} assets in {folder_path}")

            # Log each found asset for debugging
            for asset in assets:
                logger.info(f"Found asset: {asset.asset_name}")  # Use 'asset_name' property

            if not assets:
                # Try alternative path format
                alt_folder_path = folder_path.replace(MOCAP_BASE_PATH, '/Game/')
                logger.info(f"Trying alternative path: {alt_folder_path}")
                search_filter.package_paths = [alt_folder_path]
                assets = self.asset_registry.get_assets(search_filter)
                logger.info(f"Found {len(assets)} assets with alternative path")

            return assets
        except Exception as e:
            logger.error(f"Error getting assets: {str(e)}")
            return []