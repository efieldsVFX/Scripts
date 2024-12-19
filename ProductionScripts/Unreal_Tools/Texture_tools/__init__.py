"""
Unreal Engine Texture Tools - Advanced texture and material management system.

Author: Eric Fields (efieldsvfx@gmail.com)
"""

__version__ = "1.0.0"
__author__ = "Eric Fields <efieldsvfx@gmail.com>"

from .material_creator import run_material_instance_creator
from .texture_import import run_texture_importer

__all__ = ['run_material_instance_creator', 'run_texture_importer']
