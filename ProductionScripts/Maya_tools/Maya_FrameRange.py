from __future__ import print_function
import os
import logging
import sgtk
from typing import Optional, Tuple
import pymel.core as pm

# Define minimum required SGTK version
MIN_SGTK_VERSION = (0, 18, 172)

# Two blank lines before class definition
class FrameRangeError(Exception):
    pass

def setup_logging() -> logging.Logger:
    """Configure logging only if unconfigured.

    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(__name__)
    if logger.hasHandlers():
        return logger

    log_dir = os.path.join(
        os.environ.get("MAYA_APP_DIR", os.path.expanduser("~")),
        "logs", "framerange"
    )
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, "maya_framerange.log")
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)

    return logger

logger = setup_logging()

def get_engine() -> Optional[sgtk.platform.Engine]:
    """Fetch the current SGTK engine with version and availability checks.

    Returns:
        Optional[sgtk.platform.Engine]: The current SGTK engine or None
    """
    if not hasattr(sgtk, 'platform'):
        logger.warning("SGTK module not available - running in standalone mode")
        return None

    current_version = tuple(map(int, sgtk.__version__.split('.')))
    if current_version < MIN_SGTK_VERSION:
        raise RuntimeError(
            f"SGTK version {sgtk.__version__} is too old. "
            f"Minimum required: {'.'.join(map(str, MIN_SGTK_VERSION))}"
        )

    engine = sgtk.platform.current_engine()
    if not engine:
        raise FrameRangeError("No SGTK engine currently running")

    logger.debug(f"Using SGTK engine: {engine.name}")
    return engine

def get_frame_range() -> Optional[Tuple[int, int]]:
    """Retrieve frame range from Shotgun.

    Returns:
        Optional[Tuple[int, int]]: Tuple of (in_frame, out_frame) or None
    """
    engine = get_engine()
    if not engine:
        logger.warning("No SGTK engine - cannot retrieve Shotgun frame range")
        return None

    if 'tk-multi-setframerange' not in engine.apps:
        raise FrameRangeError("Required app 'tk-multi-setframerange' not found")

    context = engine.context
    task = context.sgtk.shotgun.find_one(
        "Task",
        [['id', 'is', context.task['id']]],
        ['sg_cut_in', 'sg_cut_out']
    )

    if not task:
        raise FrameRangeError(f"No task found with ID: {context.task['id']}")

    sg_in = task.get('sg_cut_in')
    sg_out = task.get('sg_cut_out')

    if sg_in is None or sg_out is None:
        raise FrameRangeError("Frame range data incomplete in Shotgun")

    logger.info(f"Retrieved frame range: {sg_in} - {sg_out}")
    return int(sg_in), int(sg_out)

def notify_user(message: str, title: str = "Frame Range Update"):
    """Non-blocking user notification.

    Args:
        message (str): Message to display
        title (str, optional): Title of notification. Defaults to "Frame Range Update"
    """
    import maya.cmds as cmds
    cmds.inViewMessage(
        assistMessage=message,
        position='midCenter',
        fadeStayTime=3000,
        fadeOutTime=1000
    )

def load_new_framerange(batch_mode: bool = False) -> bool:
    """Load a new frame range from Shotgun into Maya.

    Args:
        batch_mode (bool, optional): Whether to run in batch mode. Defaults to False.

    Returns:
        bool: True if frame range was updated, False otherwise.
    """
    try:
        frame_range = get_frame_range()
        if not frame_range:
            logger.warning("No valid frame range retrieved")
            return False

        sg_in, sg_out = frame_range
        if sg_in > sg_out:
            raise FrameRangeError(f"Invalid frame range: in ({sg_in}) > out ({sg_out})")

        original_in = int(pm.playbackOptions(query=True, ast=True))
        original_out = int(pm.playbackOptions(query=True, aet=True))

        if (original_in, original_out) == (sg_in, sg_out):
            logger.info("Frame range already matches Shotgun values")
            return False

        should_update = batch_mode
        if not batch_mode:
            message = (
                f"Current: {original_in} - {original_out}\n"
                f"New: {sg_in} - {sg_out}\n\nUpdate?"
            )
            response = pm.confirmDialog(
                title="Update Frame Range",
                message=message,
                button=["Yes", "No"],
                defaultButton="Yes",
                cancelButton="No"
            )
            should_update = response == "Yes"

        if should_update:
            pm.playbackOptions(
                minTime=sg_in,
                maxTime=sg_out,
                animationStartTime=sg_in,
                animationEndTime=sg_out
            )

            if pm.objExists("defaultRenderGlobals"):
                render_globals = pm.PyNode("defaultRenderGlobals")
                render_globals.startFrame.set(sg_in)
                render_globals.endFrame.set(sg_out)
                logger.info("Render globals updated successfully")

            if not batch_mode:
                notify_user(f"Frame range updated: {sg_in} - {sg_out}")
            else:
                logger.info(f"Frame range updated in batch mode: {sg_in} - {sg_out}")

            return True

        if batch_mode:
            logger.info("Frame range update cancelled by user")
        return False

    except (pm.MayaNodeError, pm.MayaAttributeError) as e:
        logger.error(f"Maya-specific error: {e}")
        raise
    except FrameRangeError as e:
        logger.error(f"Frame range error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

if __name__ == "__main__":
    try:
        if not pm.about(batch=True) and not pm.about(standalone=True):
            raise RuntimeError("This script must be run in Maya.")

        is_batch = pm.about(batch=True)
        logger.info(f"Running in {'batch' if is_batch else 'interactive'} mode")
        load_new_framerange(batch_mode=is_batch)

    except Exception as e:
        logger.error(f"Script execution failed: {e}")
        raise
