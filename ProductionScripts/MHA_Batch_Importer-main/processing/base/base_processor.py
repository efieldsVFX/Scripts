"""Provides base functionality for asset processing operations."""

import unreal
from PySide6 import QtCore
from ...utils.logging_config import logger
from ...config.config_manager import ConfigManager


class BaseProcessor(QtCore.QObject):
    """Base processor class for asset handling operations."""

    progress_updated = QtCore.Signal(int, str, str, str)
    processing_finished = QtCore.Signal()
    error_occurred = QtCore.Signal(str)

    def __init__(self):
        """Initialize the base processor with required tools and configurations."""
        super().__init__()
        self.asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
        self.asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        self.all_assets = []
        self.current_index = 0
        self.config_manager = ConfigManager()
        self.character_mapping = self.config_manager.character_mapping

    def get_available_folders(self):
        """
        Get available folders for asset processing.

        Raises:
            NotImplementedError: Must be implemented by derived classes
        """
        raise NotImplementedError

    def process_asset(self, asset_path: str, target_mesh: str, output_path: str):
        """
        Process an individual asset.

        Args:
            asset_path: Path to the asset
            target_mesh: Target mesh identifier
            output_path: Output destination path

        Raises:
            NotImplementedError: Must be implemented by derived classes
        """
        raise NotImplementedError

    def get_target_skeletal_mesh(self, character_name: str):
        """
        Get target skeletal mesh for a character.

        Args:
            character_name: Name of the character

        Raises:
            NotImplementedError: Must be implemented by derived classes
        """
        raise NotImplementedError
