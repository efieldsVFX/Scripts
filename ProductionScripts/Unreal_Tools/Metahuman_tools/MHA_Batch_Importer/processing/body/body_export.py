"""Provides functionality for animation data export."""

import unreal
from ...utils.logging_config import logger


def export_animation_sequence(file_path: str, target_skeleton: str, output_path: str):
    """
    Import and process animation sequence from file.

    Args:
        file_path: Path to the animation file
        target_skeleton: Path to the target skeleton
        output_path: Destination path for the processed animation

    Returns:
        unreal.AnimSequence or None: The processed animation sequence
    """
    try:
        import_settings = _create_import_settings()
        imported_asset = _import_animation_file(file_path, output_path, import_settings)

        if not imported_asset:
            raise RuntimeError("Animation import failed")

        animation_sequence = imported_asset.get_asset()
        _retarget_animation(animation_sequence, target_skeleton)

        unreal.EditorAssetLibrary.save_loaded_asset(animation_sequence)
        return animation_sequence

    except Exception as e:
        logger.error(f"Animation export failed: {str(e)}")
        return None


def _create_import_settings():
    """Create and configure import settings."""
    settings = unreal.FbxImportUI()
    settings.set_editor_property("skeleton", unreal.load_asset("/Game/Common/Base_Skeleton"))
    settings.set_editor_property("import_as_skeletal", True)
    settings.skeleton_import_data.set_editor_property("snap_to_closest_frame", True)
    settings.anim_sequence_import_data.set_editor_property("import_custom_attribute", True)
    return settings


def _import_animation_file(file_path: str, output_path: str, settings):
    """Import animation file using specified settings."""
    return unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([
        unreal.AssetImportTask(
            filename=file_path,
            destination_path=output_path,
            options=settings
        )
    ])[0]


def _retarget_animation(sequence, target_skeleton: str):
    """Retarget animation to specified skeleton."""
    target = unreal.load_asset(target_skeleton)
    if not target:
        raise ValueError(f"Failed to load target skeleton: {target_skeleton}")
    sequence.set_editor_property("target_skeleton", target.skeleton) 