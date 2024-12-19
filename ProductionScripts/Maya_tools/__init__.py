"""
Maya Tools package for production pipeline automation and scene management.

This package provides a comprehensive set of tools for Maya scene cleanup, frame range 
management, and integration with production tracking systems like Shotgun.

Key Features:
- Automated scene cleanup and optimization
- Production frame range synchronization with Shotgun
- Robust error handling and logging
- UI-driven workflow tools
"""

from . import Maya_Cleanup
from . import Maya_FrameRange

# Version using semantic versioning
__version__ = '1.0.0'

# Expose main classes and functions for direct import
from .Maya_Cleanup import (
    MayaCleanup,
    RenderCleanupUI,
    Config as CleanupConfig
)

from .Maya_FrameRange import (
    load_new_framerange,
    get_frame_range,
    FrameRangeError
)

__all__ = [
    'Maya_Cleanup',
    'Maya_FrameRange',
    'MayaCleanup',
    'RenderCleanupUI',
    'CleanupConfig',
    'load_new_framerange',
    'get_frame_range',
    'FrameRangeError'
] 