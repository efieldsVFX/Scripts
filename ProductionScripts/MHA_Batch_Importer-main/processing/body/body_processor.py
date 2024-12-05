"""Handles processing of animation assets."""

import unreal
from ..base.base_processor import BaseProcessor
from .body_helper import AnimationHelper
from ...utils.logging_config import logger


class AnimationProcessor(BaseProcessor):
    """Manages processing of animation assets."""

    def __init__(self):
        """Initialize the animation processor."""
        super().__init__()
        self.helper = AnimationHelper()
        self.import_settings = self._configure_import_settings()

    def _configure_import_settings(self):
        """Configure default import settings for animations."""
        settings = unreal.FbxImportUI()
        settings.set_editor_property("skeleton", unreal.load_asset("/Game/Common/Base_Skeleton"))
        settings.set_editor_property("import_as_skeletal", True)
        settings.set_editor_property("automated_import_should_detect_type", False)

        settings.set_editor_property("import_animations", True)
        anim_settings = settings.get_editor_property("anim_sequence_import_data")
        anim_settings.set_editor_property("import_custom_attribute", True)
        anim_settings.set_editor_property("animation_length", 
                                        unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME)
        anim_settings.set_editor_property("remove_redundant_keys", True)

        return settings
