"""Helper utilities for animation processing."""

import re
import unreal
from ..base.base_helper import BaseHelper
from ...utils.constants import ASSET_BASE_PATH, SKELETAL_MESH_MAPPING
from ...utils.logging_config import logger


class AnimationHelper(BaseHelper):
    """Provides helper functions for animation processing."""

    def __init__(self):
        """Initialize the animation helper."""
        super().__init__()
        self.skeletal_mesh_mapping = SKELETAL_MESH_MAPPING

    def parse_file_components(self, file_path: str) -> dict:
        """
        Extract components from animation file name.

        Args:
            file_path: Path to the animation file

        Returns:
            dict: Extracted name components
        """
        try:
            pattern = r"(?P<character>[A-Za-z]+)_(?P<section>\d+)_(?P<shot>\d+)_(?P<version>\w+)"
            match = re.search(pattern, file_path)

            if not match:
                raise ValueError(f"Invalid filename format: {file_path}")

            return match.groupdict()

        except Exception as e:
            logger.error(f"Filename parsing failed: {str(e)}")
            return {}