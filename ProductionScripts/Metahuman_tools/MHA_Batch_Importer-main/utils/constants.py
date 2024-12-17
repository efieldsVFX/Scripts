"""Constants used throughout the batch face importer package."""

# Base paths
MOCAP_BASE_PATH = "/Game/01_ASSETS/External/Mocap/"
METAHUMAN_BASE_PATH = "/Game/01_ASSETS/Internal/Metahumans/MHID"
LEGACY_MHID_PATH = "/Game/PROJECT/LIVELINK/MHID"

# Default configuration
DEFAULT_CONFIG = {
    'MAX_RETRIES': 3,
    'RETRY_DELAY': 5,
    'MAX_WORKERS': 1,  # Set to 1 to avoid multithreading issues
}

# Legacy actor list
LEGACY_ACTORS = {
    'bev',              # Barb character (primary)
    'ralph',           # Tiny character
    'lewis', 'luis',  # Tim character
    'erwin',           # Andre character
    'mark'             # Flike character
}

# MHID Mappings
MHID_MAPPING = {
    # Legacy actors (using old path)
    'bev': f'{LEGACY_MHID_PATH}/MHID_Bev.MHID_Bev',
    'barb': f'{LEGACY_MHID_PATH}/MHID_Bev.MHID_Bev',
    'ralph': f'{LEGACY_MHID_PATH}/MHID_Ralph.MHID_Ralph',
    'tim': f'{LEGACY_MHID_PATH}/MHID_Luis.MHID_Luis',  # Default Tim mapping to Luis
    'tim_mark': f'{LEGACY_MHID_PATH}/MHID_Mark.MHID_Mark',  # Special case for Tim played by Mark
    'lewis': f'{LEGACY_MHID_PATH}/MHID_Luis.MHID_Luis',  # Map Lewis to Luis MHID
    'luis': f'{LEGACY_MHID_PATH}/MHID_Luis.MHID_Luis',
    'erwin': f'{LEGACY_MHID_PATH}/MHID_Erwin.MHID_Erwin',
    'mark': f'{LEGACY_MHID_PATH}/MHID_Mark.MHID_Mark',

    # Character mappings
    'tiny': f'{LEGACY_MHID_PATH}/MHID_Ralph.MHID_Ralph',
    'tim_lewis': f'{LEGACY_MHID_PATH}/MHID_Luis.MHID_Luis',  # Map Tim_Lewis to Luis
    'tim_luis': f'{LEGACY_MHID_PATH}/MHID_Luis.MHID_Luis',
    'andre': f'{LEGACY_MHID_PATH}/MHID_Erwin.MHID_Erwin',
    'flike': f'{LEGACY_MHID_PATH}/MHID_Mark.MHID_Mark',

    # New pipeline actors
    'michael': f'{METAHUMAN_BASE_PATH}/Skeezer/MHID_Michael.MHID_Michael',
    'mike': f'{METAHUMAN_BASE_PATH}/Skeezer/MHID_Mike.MHID_Mike',
    'ricardo': f'{METAHUMAN_BASE_PATH}/Doctor/MHID_Ricardo.MHID_Ricardo',
    'robert': f'{METAHUMAN_BASE_PATH}/ParoleOfficer/MHID_Robert.MHID_Robert',
    'therese': f'{METAHUMAN_BASE_PATH}/Sonia/MHID_Therese.MHID_Therese',
    'clara': f'{METAHUMAN_BASE_PATH}/Shell/MHID_Clara.MHID_Clara',

    # Character mappings
    'skeezer': f'{METAHUMAN_BASE_PATH}/Skeezer/MHID_Michael.MHID_Michael',
    'doctor': f'{METAHUMAN_BASE_PATH}/Doctor/MHID_Ricardo.MHID_Ricardo',
    'paroleofficer': f'{METAHUMAN_BASE_PATH}/ParoleOfficer/MHID_Robert.MHID_Robert',
    'sonia': f'{METAHUMAN_BASE_PATH}/Sonia/MHID_Therese.MHID_Therese',
    'shell': f'{METAHUMAN_BASE_PATH}/Shell/MHID_Deborah.MHID_Deborah',

    # Add Hurricane/Tori mappings
    'hurricane': f'{METAHUMAN_BASE_PATH}/Hurricane/MHID_Tori.MHID_Tori',
    'tori': f'{METAHUMAN_BASE_PATH}/Hurricane/MHID_Tori.MHID_Tori',

    # Shell/Deborah/Clara mappings
    'shell_deborah': f'{METAHUMAN_BASE_PATH}/Shell/MHID_Deborah.MHID_Deborah',
    'shell_clara': f'{METAHUMAN_BASE_PATH}/Shell/MHID_Clara.MHID_Clara',
    'deborah': f'{METAHUMAN_BASE_PATH}/Shell/MHID_Deborah.MHID_Deborah',
    'debbie': f'{METAHUMAN_BASE_PATH}/Shell/MHID_Deborah.MHID_Deborah',
}

# Actor to Character mapping (for display purposes)
ACTOR_CHARACTER_MAPPING = {
    'bev': 'Barb',
    'barb': 'Barb',
    'ralph': 'Tiny',
    'tim': 'Tim',
    'lewis': 'Tim',
    'luis': 'Tim',
    'erwin': 'Andre',
    'mark': 'Flike',
    'ricardo': 'Doctor',
    'robert': 'Parole Officer',
    'clara': 'Shell',
    'michael': 'Skeezer',
    'mike': 'Skeezer',
    'therese': 'Sonia',
    'hurricane': 'Hurricane',
    'tori': 'Hurricane',
    'deborah': 'Shell',
    'debbie': 'Shell'
}

# Table column indices
COLUMN_INDICES = {
    'FOLDER': 0,
    'CHARACTER': 1,
    'SLATE': 2,
    'SEQUENCE': 3,
    'ACTOR': 4,
    'TAKE': 5,
    'PROCESS_STATUS': 6,
    'EXPORT_STATUS': 7,
    'ERROR': 8
}

# Status messages
STATUS_MESSAGES = {
    'WAITING': "Waiting",
    'PROCESSING': "Processing",
    'COMPLETE': "Complete",
    'FAILED': "Failed",
    'EXPORTING': "Exporting"
}

# Window geometry settings
WINDOW_GEOMETRY = {
    'MAIN_X': 100,
    'MAIN_Y': 100,
    'MAIN_WIDTH': 800,
    'MAIN_HEIGHT': 600,
    'PROGRESS_X': 300,
    'PROGRESS_Y': 300,
    'PROGRESS_WIDTH': 1200,
    'PROGRESS_HEIGHT': 500
}

# Column widths for progress table
COLUMN_WIDTHS = {
    'FOLDER': 250,
    'CHARACTER': 100,
    'SLATE': 80,
    'SEQUENCE': 100,
    'ACTOR': 100,
    'TAKE': 80,
    'PROCESS_STATUS': 120,
    'EXPORT_STATUS': 120,
    'ERROR': 200
}
# Name patterns for asset parsing
NAME_PATTERNS = [
    # Quad actor pattern (4 actors)
    r"^(?:(\w+)_)?(S\d+)_(\d+)_(\w+)_(\w+)_(\w+)_(\w+)_(\d+)(?:_\d+)?$",
    # Triple actor pattern (3 actors)
    r"^(?:(\w+)_)?(S\d+)_(\d+)_(\w+)_(\w+)_(\w+)_(\d+)(?:_\d+)?$",
    # Dual actor pattern (2 actors)
    r"^(?:(\w+)_)?(S\d+)_(\d+)_(\w+)_(\w+)_(\d+)(?:_\d+)?$",
    # Single actor pattern (1 actor)
    r"^(?:(\w+)_)?(S\d+)_(\d+)_(\w+)_(\d+)(?:_\d+)?$",
    # TT format pattern
    r"^TT-(\w+)-(\d+)_(\d+)$"
]

# Add any missing sequence mappings
SEQUENCE_MAPPING = {
    '0030': ('0030_Parole_Officer_Visit', 'POV'),
    '0040': ('0040_Andre_Work', 'ANW'),
    '0050': ('0050_Barb_Shell_Pool_Time', 'BSP'),
    '0060': ('0060_Barb_Shell_Kitchen_Toast', 'BSK'),
    '0070': ('0070_Walking_To_Flike', 'WTF'),
    '0080': ('0080_Meeting_Flike', 'MEF'),
    '0090': ('0090_Speaking_To_Tim', 'STT'),
    '0100': ('0100_Back_Alley_Walk', 'BAW'),
    '0110': ('0110_SoniaX_Ad', 'SXA'),
    '0120': ('0120_Andre_Bike_Ride', 'ABR'),
    '0130': ('0130_Flike_Vets', 'FLV'),
    '0140': ('0140_Barb_Shell_Meet_Tiny', 'BST'),
    '0150': ('0150_Andre_Eating', 'ANE'),
    '0160': ('0160_Hurricane_Twerking', 'HUT'),
    '0170': ('0170_Pray_Leprechaun', 'PRL'),
    '0180': ('0180_Andre_Thinking', 'ANT'),
    '0190': ('0190_Andre_Refuses_Job', 'ARJ'),
    '0200': ('0200_Doctor_Visit', 'DRV'),
    '0210': ('0210_Flikes_Tap_Dance', 'FTP'),
    '0220': ('0220_Whore_House_Inspection', 'WHI'),
    '0230': ('0230_Andre_Stargazing', 'AST'),
    '0240': ('0240_Molotov_Walk', 'MOW'),
    '0250': ('0250_Molotov_Cocktail', 'MOC'),
    '0260': ('0260_Picking_Up_Tim', 'PUT'),
    '0270': ('0270_Andre_Listens_Heart', 'ALH'),
    '0280': ('0280_Andre_Takes_Job', 'ATJ'),
    '0290': ('0290_Barb_Shell_Meet_Andre', 'BMA'),
    '0300': ('0300_Andre_Self_Reflects', 'ASR'),
    '0310': ('0310_Basketball_Match', 'BBM'),
    '0320': ('0320_Tims_House', 'TMH'),
    '0330': ('0330_Andre_Runs_Home', 'ARH'),
    '0340': ('0340_Barb_Shell_Celebrate', 'BSC'),
    '0350': ('0350_Flike_Raps', 'FLR'),
    '0360': ('0360_Sonia_Limo_Ride', 'SLR'),
    '0370': ('0370_Andre_Sonia', 'ASO'),
    '0380': ('0380_Flike_Molotov_Cocktail', 'FMC'),
    '0390': ('0390_The_Fairy_Costume', 'TFC'),
    '0400': ('0400_Barb_Shell_Dance', 'BSD'),
    '0410': ('0410_Andres_Death', 'ADE'),
    '0420': ('0420_Flikes_Fire_Dance', 'FFD'),
    '0430': ('0430_Andres_Burial', 'ABU'),
    '0440': ('0440_Andre_at_Church', 'AAC')
} 

# Import complete Skeletal Mesh mapping from constants
SKELETAL_MESH_MAPPING = {
    # Legacy actors (using old path)
    'bev': f'{LEGACY_MHID_PATH}/SK_MHID_Bev.SK_MHID_Bev',
    'barb': f'{LEGACY_MHID_PATH}/SK_MHID_Bev.SK_MHID_Bev',
    'ralph': f'{LEGACY_MHID_PATH}/SK_MHID_Ralph.SK_MHID_Ralph',
    'tim': f'{LEGACY_MHID_PATH}/SK_MHID_Lewis.SK_MHID_Lewis',
    'lewis': f'{LEGACY_MHID_PATH}/SK_MHID_Lewis.SK_MHID_Lewis',
    'luis': f'{LEGACY_MHID_PATH}/SK_MHID_Luis.SK_MHID_Luis',
    'erwin': f'{LEGACY_MHID_PATH}/SK_MHID_Erwin.SK_MHID_Erwin',
    'mark': f'{LEGACY_MHID_PATH}/SK_MHID_Mark.SK_MHID_Mark',
    'ricardo': f'{LEGACY_MHID_PATH}/SK_MHID_Ricardo.SK_MHID_Ricardo',
    'robert': f'{LEGACY_MHID_PATH}/SK_MHID_Robert.SK_MHID_Robert',
    'clara': f'{LEGACY_MHID_PATH}/SK_MHID_Clara.SK_MHID_Clara',

    # Character mappings
    'tiny': f'{LEGACY_MHID_PATH}/SK_MHID_Ralph.SK_MHID_Ralph',
    'tim_lewis': f'{LEGACY_MHID_PATH}/SK_MHID_Lewis.SK_MHID_Lewis',
    'tim_luis': f'{LEGACY_MHID_PATH}/SK_MHID_Luis.SK_MHID_Luis',
    'andre': f'{LEGACY_MHID_PATH}/SK_MHID_Erwin.SK_MHID_Erwin',
    'flike': f'{LEGACY_MHID_PATH}/SK_MHID_Mark.SK_MHID_Mark',
    'doctor': f'{LEGACY_MHID_PATH}/SK_MHID_Ricardo.SK_MHID_Ricardo',
    'paroleofficer': f'{LEGACY_MHID_PATH}/SK_MHID_Robert.SK_MHID_Robert',
    'shell': f'{LEGACY_MHID_PATH}/SK_MHID_Clara.SK_MHID_Clara',

    # New pipeline actors
    'michael': f'{METAHUMAN_BASE_PATH}/Skeezer/SK_MHID_Michael.SK_MHID_Michael',
    'mike': f'{METAHUMAN_BASE_PATH}/Skeezer/SK_MHID_Mike.SK_MHID_Mike',
    'therese': f'{METAHUMAN_BASE_PATH}/Sonia/SK_MHID_Therese.SK_MHID_Therese',

    # Character mappings for new pipeline
    'skeezer': f'{METAHUMAN_BASE_PATH}/Skeezer/SK_MHID_Michael.SK_MHID_Michael',
    'sonia': f'{METAHUMAN_BASE_PATH}/Sonia/SK_MHID_Therese.SK_MHID_Therese',

    # Add Hurricane/Tori mappings
    'hurricane': f'{METAHUMAN_BASE_PATH}/Hurricane/SK_MHID_Tori.SK_MHID_Tori',
    'tori': f'{METAHUMAN_BASE_PATH}/Hurricane/SK_MHID_Tori.SK_MHID_Tori',

    # Shell/Deborah/Clara mappings
    'shell_deborah': f'{METAHUMAN_BASE_PATH}/Shell/SK_MHID_Deborah.SK_MHID_Deborah',
    'shell_clara': f'{METAHUMAN_BASE_PATH}/Shell/SK_MHID_Clara.SK_MHID_Clara',
    'deborah': f'{METAHUMAN_BASE_PATH}/Shell/SK_MHID_Deborah.SK_MHID_Deborah',
    'debbie': f'{METAHUMAN_BASE_PATH}/Shell/SK_MHID_Deborah.SK_MHID_Deborah',
}

