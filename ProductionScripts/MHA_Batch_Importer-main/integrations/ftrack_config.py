"""FTrack configuration and integration settings."""

import os
import ftrack_api
from ..config.env_config import (
    FTRACK_SERVER,
    FTRACK_API_KEY,
    FTRACK_API_USER,
    PROJECT_ID,
    ASSET_BUILD_TYPE_NAME
)
from ..utils.logging_config import logger

class FTrackConfig:
    """Configuration for FTrack integration."""
    
    def __init__(self):
        self.session = None
        self.project = None
        self.initialize_session()
        
    def validate_environment(self):
        """Validate required environment variables."""
        required_vars = {
            'FTRACK_SERVER': FTRACK_SERVER,
            'FTRACK_API_KEY': FTRACK_API_KEY,
            'FTRACK_API_USER': FTRACK_API_USER,
            'PROJECT_ID': PROJECT_ID
        }
        
        missing_vars = [key for key, value in required_vars.items() if not value]
        
        if missing_vars:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )
    
    def initialize_session(self):
        """Initialize FTrack session."""
        try:
            self.validate_environment()
            
            self.session = ftrack_api.Session(
                server_url=FTRACK_SERVER,
                api_key=FTRACK_API_KEY,
                api_user=FTRACK_API_USER
            )
            
            # Get project
            self.project = self.session.query(
                f'Project where id is "{PROJECT_ID}"'
            ).first()
            
            if not self.project:
                raise ValueError(f"Project with ID {PROJECT_ID} not found")
                
        except Exception as e:
            logger.error(f"Failed to initialize FTrack session: {str(e)}")
            self.session = None
    
    def get_character_mapping(self):
        """Get character mapping from FTrack."""
        try:
            if not self.session or not self.project:
                return {}
            
            # Query for character assets in the project
            query = (
                f'AssetBuild where project.id is "{PROJECT_ID}" '
                f'and type.name is "{ASSET_BUILD_TYPE_NAME}"'
            )
            characters = self.session.query(query)
            
            mapping = {}
            for character in characters:
                custom_attributes = character['custom_attributes']
                
                # Get required attributes
                actor_names = custom_attributes.get('actor_names', '').split(',')
                character_name = character['name'].lower()
                
                # Get optional attributes with defaults
                mhid_path = custom_attributes.get('mhid_path', '')
                skeletal_mesh_path = custom_attributes.get('skeletal_mesh_path', '')
                
                # Additional metadata
                metadata = {
                    'id': character['id'],
                    'status': character['status']['name'],
                    'created_at': character['created_at'].strftime('%Y-%m-%d'),
                    'thumbnail_url': self._get_thumbnail_url(character)
                }
                
                # Add to mapping
                for actor in actor_names:
                    actor = actor.strip().lower()
                    if actor:
                        mapping[actor] = {
                            'character': character_name,
                            'mhid_path': mhid_path,
                            'skeletal_mesh_path': skeletal_mesh_path,
                            'metadata': metadata
                        }
            
            return mapping
            
        except Exception as e:
            logger.error(f"Failed to get character mapping from FTrack: {str(e)}")
            return {}
            
    def _get_thumbnail_url(self, entity):
        """Get thumbnail URL for an entity."""
        try:
            thumbnail = entity['thumbnail']
            if thumbnail:
                return thumbnail['url']
        except Exception:
            pass
        return None