from __future__ import print_function
import os

def get_engine():
    """
    Get current engine through SG toolkit

    Returns:
        [type]: [description]
    """
    try:
        import sgtk
    except ImportError as e:
        print("No toolkit engine found: {0}".format(e))
        engine = None
    else:
        engine = sgtk.platform.engine.current_engine()
    return engine

def get_frame_range():
    import sgtk

    sg_in = None
    sg_out = None
    engine = get_engine()

    if 'tk-multi-setframerange' not in engine.apps:
        raise ValueError("Not in a shot, no framerange to load")
    framerange_app = engine.apps['tk-multi-setframerange']
    current_settings = framerange_app.settings
    new_settings = current_settings.copy()

    context = engine.context
    task = context.sgtk.shotgun.find_one(
        "Task",
        [
            ['id', 'is', context.task['id']]
        ],
        ['sg_cut_in', 'sg_cut_out']
    )

    if task:
        sg_in = task.get('sg_cut_in')
        sg_out = task.get('sg_cut_out')
        if sg_in is not None and sg_out is not None:
            return sg_in, sg_out

    try:
        new_settings['sg_in_frame_field'] = 'sg_head_in'
        new_settings['sg_out_frame_field'] = 'sg_head_out'
        framerange_app._set_settings(new_settings)
        sg_in, sg_out = framerange_app.get_frame_range_from_shotgun()
    except sgtk.TankError as exc:
        pass
    if sg_in is None or sg_out is None:
        try:
            new_settings['sg_in_frame_field'] = 'sg_cut_in'
            new_settings['sg_out_frame_field'] = 'sg_cut_out'
            framerange_app._set_settings(new_settings)
            sg_in, sg_out = framerange_app.get_frame_range_from_shotgun()
        except sgtk.TankError as exc:
            return False

    return sg_in, sg_out

def load_new_framerange():
    import sgtk
    import pymel.core as pm  # pylint: disable=import-error

    sg_in, sg_out = get_frame_range()

    try:
        current_in = int(pm.playbackOptions(query=True, ast=True))
        current_out = int(pm.playbackOptions(query=True, aet=True))
    except BaseException:
        return False
    if current_in == sg_in and current_out == sg_out:
        return False
    else:
        window = cmds.confirmDialog(
            title="Timings Have Changed!",
            message="New Shotgun Timings Found:\n    Old Range:  {0} - {1}\n    New Range:  {2} - {3}\n Do you want to update?".format(
                current_in, current_out, sg_in, sg_out
            ),
            messageAlign="center",
            button=["Import", "Cancel"],
            defaultButton="Import",
            cancelButton="Cancel",
            backgroundColor=[0, 0, 0],
        )
        if window == "Import":
            pm.playbackOptions(
                minTime=sg_in,
                maxTime=sg_out,
                animationStartTime=sg_in,
                animationEndTime=sg_out,
            )
            defaultRenderGlobals = pm.PyNode("defaultRenderGlobals")
            defaultRenderGlobals.startFrame.set(sg_in)
            defaultRenderGlobals.endFrame.set(sg_out)
            return True
        return False


load_new_framerange()
