"""Helper utilities for facial animation processing."""

import re
import unreal
from ..base.base_helper import BaseHelper
from ...utils.constants import ASSET_BASE_PATH, NAME_PATTERNS
from ...utils.logging_config import logger


class FacialHelper(BaseHelper):
    """Provides helper functions for facial animation processing."""

    def __init__(self):
        """Initialize the facial helper with name patterns."""
        super().__init__()
        self.name_patterns = NAME_PATTERNS

    def parse_asset_components(self, asset_name: str) -> dict:
        """
        Extract naming components from asset name.

        Args:
            asset_name: Name of the asset to parse

        Returns:
            dict: Dictionary containing parsed name components
        """
        try:
            for pattern in self.name_patterns:
                match = re.search(pattern, asset_name)
                if match:
                    return match.groupdict()
            return {}

        except Exception as e:
            logger.error(f"Asset name parsing failed: {str(e)}")
            return {}

    def get_character_data(self, name_components: dict) -> unreal.Object:
        """
        Retrieve character data asset.

        Args:
            name_components: Dictionary containing character information

        Returns:
            unreal.Object: Character data asset or None if not found
        """
        try:
            character = name_components.get('character', '').lower()
            data_path = f"{ASSET_BASE_PATH}/{character}/DATA_{character}"

            data_asset = unreal.load_asset(data_path)
            if not data_asset:
                raise ValueError(f"Unable to load character data at {data_path}")

            return data_asset

        except Exception as e:
            logger.error(f"Character data retrieval failed: {str(e)}")
            return None