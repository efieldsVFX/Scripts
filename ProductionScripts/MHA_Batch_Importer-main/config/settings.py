"""Configuration settings for the batch metahuman importer."""

# Default configuration values
DEFAULT_CONFIG = {
    'MAX_RETRIES': 3,
    'RETRY_DELAY': 5,
    'MAX_WORKERS': 1,
    'USE_FTRACK': True  # Enable/disable FTrack integration
}

# Base paths - these can be overridden by environment variables or FTrack
MOCAP_BASE_PATH = "/Game/Mocap/"
METAHUMAN_BASE_PATH = "/Game/Metahumans/MHID"

# Fallback mappings - used when FTrack is not available
LEGACY_ACTORS = set()  # Moved to FTrack
MHID_MAPPING = {}      # Moved to FTrack
SKELETAL_MESH_MAPPING = {}  # Moved to FTrack
ACTOR_CHARACTER_MAPPING = {}  # Moved to FTrack

# Window settings
WINDOW_SETTINGS = {
    'TITLE': "MHA Batch Processor",
    'GEOMETRY': {
        'x': 300,
        'y': 300,
        'width': 400,
        'height': 200
    }
}
