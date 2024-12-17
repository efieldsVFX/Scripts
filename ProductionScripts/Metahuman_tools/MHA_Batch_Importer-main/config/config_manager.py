"""Configuration manager for the batch metahuman importer."""

from ..integrations.ftrack_config import FTrackConfig
from ..utils.logging_config import logger

class ConfigManager:
    """Manages configuration and integrations."""
    
    def __init__(self):
        self.ftrack_config = None
        self.character_mapping = {}
        self.initialize_integrations()
    
    def initialize_integrations(self):
        """Initialize available integrations."""
        try:
            # Initialize FTrack if available
            self.ftrack_config = FTrackConfig()
            if self.ftrack_config.session:
                self.character_mapping = self.ftrack_config.get_character_mapping()
            else:
                logger.warning("FTrack integration not available, using fallback mappings")
                self.use_fallback_mappings()
        except ImportError:
            logger.warning("FTrack not installed, using fallback mappings")
            self.use_fallback_mappings()
    
    def use_fallback_mappings(self):
        """Use fallback mappings from settings.py."""
        from .settings import (
            LEGACY_ACTORS,
            MHID_MAPPING,
            SKELETAL_MESH_MAPPING,
            ACTOR_CHARACTER_MAPPING
        )
        
        # Convert legacy mappings to new format
        for actor, character in ACTOR_CHARACTER_MAPPING.items():
            self.character_mapping[actor.lower()] = {
                'character': character.lower(),
                'mhid_path': MHID_MAPPING.get(character.lower(), ''),
                'skeletal_mesh_path': SKELETAL_MESH_MAPPING.get(character.lower(), '')
            } 