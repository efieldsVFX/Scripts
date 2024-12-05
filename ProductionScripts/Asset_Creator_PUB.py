import json
import logging
import os
import sys
from os import environ

import ftrack_api
import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets
from dotenv import load_dotenv

# Constants
ASSET_CATEGORIES = ['Character', 'Prop', 'Set', 'Vehicle', 'Weapon']

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Environment setup
load_dotenv()
SERVER_URL = environ.get('TRACKING_SERVER')
API_KEY = environ.get('TRACKING_KEY')
API_USER = environ.get('TRACKING_USER')

if not all([SERVER_URL, API_KEY, API_USER]):
    raise EnvironmentError('Missing tracking system credentials')

def load_config(config_path):
    """Load configuration from JSON file.

    Args:
        config_path (str): Path to configuration file

    Returns:
        dict: Configuration data or None if error occurs
    """
    try:
        with open(config_path, 'r') as config_file:
            return json.load(config_file)
    except Exception as exc:
        logger.error('Error loading config: %s', exc)
        return None

def create_ftrack_entities(session, project_id, entities):
    """Create tracking system entities.
    
    Args:
        session: Database session
        project_id: Project identifier
        entities: List of entity definitions
    """
    created = {project_id: session.get('Project', project_id)}
    versions = []

    try:
        for entity in entities:
            pid = entity['parent_id']
            parent = session.get('Context', pid)

            logger.info('Creating %s: %s', entity['type'], entity['name'])

            existing_entity = session.query(
                f"{entity['type']} where name is '{entity['name']}' "
                f"and parent.id is '{parent['id']}'"
            ).first()

            if existing_entity:
                logger.info(
                    'Entity "%s" already exists with ID %s. Using existing entity.',
                    entity['name'], existing_entity['id']
                )
                created_entity = existing_entity
            else:
                created_entity = session.create(
                    entity['type'],
                    {'name': entity['name'], 'parent': parent}
                )
                session.commit()

            created[entity['name']] = created_entity

            if entity['type'] == 'AssetBuild':
                asset_version = _create_asset_version(session, created_entity, project_id)
                if asset_version:
                    versions.append(asset_version)

        return created, versions

    except Exception as exc:
        logger.error('Error creating Ftrack entities: %s', exc)
        return None, None

def _create_asset_version(session, asset_entity, project_id):
    """Create asset version for given asset entity.

    Args:
        session: Ftrack session
        asset_entity: Asset entity to create version for
        project_id (str): Project identifier

    Returns:
        AssetVersion or None if creation fails
    """
    try:
        default_task = session.query(
            f'Task where parent.id is "{project_id}"'
        ).first()
        
        if not default_task:
            logger.warning(
                'No default task found for project ID %s. AssetVersion not created.',
                project_id
            )
            return None

        asset_version = session.create('AssetVersion', {
            'asset': asset_entity,
            'task': default_task
        })
        session.commit()
        return asset_version

    except Exception as exc:
        logger.error('Error creating asset version: %s', exc)
        return None

