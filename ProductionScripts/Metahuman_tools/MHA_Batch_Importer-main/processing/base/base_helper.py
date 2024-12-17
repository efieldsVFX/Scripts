"""Provides base helper functionality for asset processing."""

import unreal
from ...utils.logging_config import logger
from ...utils.constants import SKELETAL_MESH_MAPPING


class BaseHelper:
    """Base helper class for asset processing operations."""

    def __init__(self):
        """Initialize the helper with skeletal mesh mappings."""
        self.skeletal_mesh_mapping = SKELETAL_MESH_MAPPING

    def get_target_skeletal_mesh(self, character_name: str) -> unreal.SkeletalMesh:
        """
        Retrieve the skeletal mesh asset for a given character.

        Args:
            character_name: Name of the character to fetch the mesh for

        Returns:
            unreal.SkeletalMesh or None: The loaded skeletal mesh asset
        """
        try:
            mesh_path = self.skeletal_mesh_mapping.get(character_name.lower())
            if not mesh_path:
                raise ValueError(f"Missing skeletal mesh mapping for: {character_name}")

            mesh = unreal.load_asset(mesh_path)
            if not mesh:
                raise ValueError(f"Unable to load skeletal mesh at: {mesh_path}")

            return mesh

        except Exception as e:
            logger.error(f"Skeletal mesh retrieval failed: {str(e)}")
            return None