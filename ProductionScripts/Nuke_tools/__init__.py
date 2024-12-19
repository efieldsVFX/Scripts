"""
Nuke Production Tools Suite - A collection of high-performance tools for Nuke.

This package contains tools designed to enhance artist efficiency and troubleshoot 
common production issues in Nuke, specifically crafted for a fast-paced VFX 
production environment.

Components:
    NK_UI_fix - UI management tool for Nuke's Color Picker
    NKdebugging - Comprehensive debugging toolkit with:
        - Thread and memory optimization
        - Node management (ZDefocus, Postage Stamps)
        - Performance monitoring
        - System diagnostics
        - Automated logging
    NK_Node_Validator - Advanced node tree validation system

Author: Eric Fields (efieldsvfx@gmail.com)
Copyright © 2024. All rights reserved.
"""

from .nk_debugging import (
    DebugPanel,
    DebugController,
    NukeDebugError,
    DebugActions,
    logger
)
from .NK_UI_fix import main as fix_ui
from .NK_Node_Validator import run_validation

__version__ = '1.0.0'
__author__ = 'Eric Fields'
__email__ = 'efieldsvfx@gmail.com'

__all__ = [
    # Main tools
    'NK_UI_fix',
    'NKdebugging',
    'NK_Node_Validator',
    
    # Debugging components
    'DebugPanel',
    'DebugController',
    'NukeDebugError',
    'DebugActions',
    'logger',
    
    # Convenience functions
    'fix_ui',
    'run_validation'
]

# Version information for individual tools
tool_versions = {
    'NK_UI_fix': '1.0.0',
    'NKdebugging': '1.0.0',
    'NK_Node_Validator': '1.0.0'
} 