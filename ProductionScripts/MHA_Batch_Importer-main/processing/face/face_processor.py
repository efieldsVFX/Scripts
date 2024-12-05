"""Processor for facial animation data."""

import unreal
from ..base.base_processor import BaseProcessor
from ..asset_processor import AssetProcessor
from .face_helper import FacialHelper
from ...utils.logging_config import logger
from ...utils.constants import CAPTURE_BASE_PATH


class AssetReference:
    """Wrapper for asset references with path information."""

    def __init__(self, asset_obj, full_path: str):
        """
        Initialize asset reference.

        Args:
            asset_obj: The asset object
            full_path: Full path to the asset
        """
        self.asset = asset_obj
        self.package_name = full_path
        self.asset_name = asset_obj.get_name()
        self.package_path = '/'.join(full_path.split('/')[:-1])

    def get_name(self) -> str:
        """Get asset name."""
        return self.asset_name


class FacialProcessor(BaseProcessor):
    """Processes facial animation data."""

    def __init__(self):
        """Initialize the facial processor."""
        super().__init__()
        self.asset_processor = AssetProcessor()
        self.helper = FacialHelper()

    def get_available_folders(self) -> list:
        """
        Get all available folders containing capture data.

        Returns:
            list: List of folder paths containing capture data
        """
        try:
            capture_folders = set()
            all_paths = self.asset_registry.get_sub_paths(CAPTURE_BASE_PATH, recurse=True)

            for path in all_paths:
                folder_path = str(path.path_name) if hasattr(path, 'path_name') else str(path)
                if "Capture" in folder_path:
                    capture_folders.add(folder_path)

            return sorted(list(capture_folders))

        except Exception as e:
            logger.error(f"Folder retrieval failed: {str(e)}")
            return []

    def get_capture_assets(self) -> list:
        """
        Get all capture data assets.

        Returns:
            list: List of capture data assets
        """
        try:
            assets = []
            all_assets = self.asset_registry.get_assets_by_path(
                CAPTURE_BASE_PATH,
                recursive=True
            )

            for asset in all_assets:
                if self._is_valid_capture_asset(asset):
                    path_name = asset.get_full_name()
                    assets.append(AssetReference(asset, path_name))

            return assets

        except Exception as e:
            logger.error(f"Asset retrieval failed: {str(e)}")
            return []

    def _is_valid_capture_asset(self, asset) -> bool:
        """
        Validate if asset is a capture data asset.

        Args:
            asset: Asset to validate

        Returns:
            bool: True if asset is valid capture data
        """
        try:
            if not asset:
                return False
            class_name = asset.get_class().get_name()
            return 'CaptureData' in class_name
        except Exception:
            return False
        
        