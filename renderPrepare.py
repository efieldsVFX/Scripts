import maya.cmds as cmds
import maya.mel as mel
import maya.app.renderSetup.model.renderLayer as renderLayer
import maya.app.renderSetup.model.renderSetup as renderSetup
import os

def remMayaJunk():
    #maya junk
    if cmds.objExists('*Arnold*'):
        cmds.delete('*Arnold*')
    if cmds.objExists("uiConfigurationScriptNode"):
        bs = cmds.scriptNode("uiConfigurationScriptNode", q=True, bs=True)
    if bs:
        bs = re.sub(r"DCF_updateViewportList;", bs, "")
        cmds.scriptNode("uiConfigurationScriptNode", e=True, bs=bs)   
    if cmds.objExists('sceneConfigurationScriptNode'):
        cmds.delete('sceneConfigurationScriptNode')

def remBadLayers():
    if cmds.ls(type="rs_*"):
        cmds.delete(cmds.ls(type="RenderLayer"))
        print("Bye renderLayers")


def remJunkNodes():
    # deletes unnecessary nodes and misc. items
    if cmds.ls(type="nodeGraphEditorInfo"):
        cmds.delete(cmds.ls(type="nodeGraphEditorInfo"))
        print("Node Graph Editor nodes deleted")
    if cmds.ls(type="audio"):
        cmds.delete(cmds.ls(type="audio"))
        print("Audio Deleted")


def delRSlayer():
    # remove render setup layers
    if cmds.objExists("defualtRenderLayer"):
        defLayers = cmds.ls(type="renderLayer")
        for each in defLayers:
            cmds.delete(each)
        print("Render Setup Layers Deleted")
    else:
        print("No Render Setup Layers to Deleted")
    mel.eval('setAttr "defaultRenderLayer.renderable" 0')
    print("Default Render Layer set to OFF")


def remABC():
    # Remove ABCamera Plugin
    if cmds.unknownPlugin(q=True, l=True):
        cmds.unknownPlugin("ABCamera", r=True)
        print("Removed ABCamera")
    else:
        print("No ABCamera nodes to delete")

def remMTR():
    if cmds.unknownPlugin(q = True, l = True):
        cmds.unknownPlugin("Mayatomr", r = True)
        print('Removed Mental Ray')
    else:
        print('No Mental Ray nodes to delete')

def remRM():
    # remove Renderman Nodes
    if cmds.unknownPlugin(q=True, l=True):
        cmds.unknownPlugin("RenderMan_for_Maya", r=True)
        print("Removed RenderMan")
    else:
        print("No RenderMan nodes to delete")


def remDOFV():
    # removes depthOfFieldView Plugin
    if cmds.unknownPlugin(q=True, l=True):
        cmds.unknownPlugin("depthOfFieldView", r=True)
        print("Removed depthOfFieldView Plugin")
    else:
        print("No depthOfFieldView Plugin nodes to delete")


def remAttr():
    # removes attributeNode plugin
    if cmds.unknownPlugin(q=True, l=True):
        cmds.unknownPlugin("attributeNode.py", r=True)
        print("Removed Attribute Node")
    else:
        print("No Attribute nodes to delete")


def remMW():
    # removes maxwell plugin
    if cmds.unknownPlugin(q=True, l=True):
        cmds.unknownPlugin("maxwell", r=True)
        print("Removed maxwell")
    else:
        print("No maxwell nodes to delete")


def remCVSI():
    if cmds.unknownPlugin(q=True, l=True):
        cmds.unknownPlugin("cvShapeInverter.py", r=True)
        print("Removed cvShapeInverter")
    else:
        print("No cvShapeInverter nodes to delete")


def remMA():
    if cmds.unknownPlugin(q=True, l=True):
        cmds.unknownPlugin("mArny_maya50", r=True)
        print("Removed mArny_maya50")
    else:
        print("No mArny_maya50 nodes to delete")


def remMTOA():
    if cmds.unknownPlugin(q=True, l=True):
        cmds.unknownPlugin("mtoa", r=True)
        print("Removed mtoa")
    else:
        print("No mtoa nodes to delete")


def remSPC():
    if cmds.unknownPlugin(q=True, l=True):
        cmds.unknownPlugin("spCmptAsmbNd", r=True)
        print("Removed spCmptAsmbNd")
    else:
        print("No spCmptAsmbNd nodes to delete")


def remSPM():
    if cmds.unknownPlugin(q=True, l=True):
        cmds.unknownPlugin("spMapInfoShader", r=True)
        print("Removed spMapInfoShader")
    else:
        print("No spMapInfoShader nodes to delete")


def remSPR():
    if cmds.unknownPlugin(q=True, l=True):
        cmds.unknownPlugin("spRotoNode", r=True)
        print("Removed spRotoNode")
    else:
        print("No spRotoNode nodes to delete")


def remVR():
    if cmds.unknownPlugin(q=True, l=True):
        cmds.unknownPlugin("vrayformaya", r=True)
        print("Removed Vray")
    else:
        print("No Vray nodes to delete")


def adjustErrors():
    # fix render adjustments
    mel.eval("fixRenderLayerOutAdjustmentErrors()")


def delMats():
    # deleteLamberts
    lam = cmds.ls("lambert*")
    cmds.select(lam, noExpand=True)
    cmds.select("lambert1", d=True)
    stdLam = cmds.ls(sl=True)

    if stdLam:
        cmds.delete(stdLam)
        print("Extra Lamberts Deleted")
    else:
        print("No Extra Lamberts")


def remDLayers():
    # display layers
    if cmds.objExists("defaultLayer1"):
        dlayers = cmds.ls(type="*defaultLayer*")
        cmds.delete(dlayers)
    else:
        print("No extra Display Layers to delete")


def remDRLayer():
    if cmds.objExists("*displayRenderLayer*"):
        cmds.delete(cmds.ls("*displayRenderLayer*"))
        print("Display Render Layers have been deleted")
    else:
        print("No display Render Layers nodes Layers to Delete")


def remRenderSetup():
    if cmds.objExists("renderSetup"):
        cmds.delete(cmds.ls(type="renderSetup"))
        print("Render Setups have been deleted")
    else:
        print("No Render Setup nodes to Delete")


def remBlind():
    # remove render setup layers
    if cmds.objExists("blind*"):
        cmds.delete(cmds.ls("blind*"))
        print("Blind nodes have been deleted")
    else:
        print("No blind nodes Layers to Delete")


def remAOVs():
    # remove render setup layers
    if cmds.objExists("*Aov*"):
        cmds.delete(cmds.ls("*Aov*"))
        print("Aovs have been deleted nodes")
    else:
        print("No AOVs to be Deleted")


def remMR():
    gva = "globalVolumeAggregate"
    if cmds.objExists(gva):
        cmds.lockNode(gva, l=False)
        cmds.delete(gva)
        print("removed volume aggregate")
    else:
        print("no volume aggregate")
    un = cmds.unknownPlugin(q=True, l=True)
    it = 0
    if un == None:
        print("No Unknown Plugins to Remove")
    else:
        while it < len(un):
            print("Unknown Plugins Removed: " + un[it])
            cmds.unknownPlugin(un[it], r=True)
            it += 1

def refCleanup():
    all_ref_paths = (
        cmds.file(q=True, reference=True) or []
    )  # Get a list of all top-level references in the scene.

    for each in all_ref_paths:
        if cmds.referenceQuery(
            each, isLoaded=True
        ):  # Only reload references that are already loaded.
            cmds.file(each, loadReference=True)  # Reload the reference
    for ref_path in all_ref_paths:
        if cmds.referenceQuery(
            ref_path, isLoaded=True
        ):  # Only import it if it's loaded, otherwise it would throw an error.
            cmds.file(ref_path, importReference=True)  # Import the reference.
    
            new_ref_paths = cmds.file(
                q=True, reference=True
            )  # If the reference had any nested references they will now become top-level references, so recollect them.
            if new_ref_paths:
                for new_ref_path in new_ref_paths:
                    if (
                        new_ref_path not in all_ref_paths
                    ):  # Only add on ones that we don't already have.
                        all_ref_paths.append(new_ref_path)


def renderCleaner():
    os.environ["MAYA_TESTING_CLEANUP"] = "1"

    # mel.eval("cleanUpScene(0)")

    remMayaJunk()

    remDLayers()

    remDRLayer()

    delRSlayer()

    remMTR()

    remMR()

    remRenderSetup()

    remBlind()

    remAOVs()

    remABC()

    remRM()

    remDOFV()

    remAttr()

    remMW()

    remCVSI()

    remMA()

    remMTOA()

    remSPC()

    remSPM()

    remSPR()

    remVR()

    #adjustErrors()

    delMats()

    os.environ["MAYA_TESTING_CLEANUP"] = "0"

def animCleaner():
    refCleanup()
    
    mbEnable()
    
    renderCleaner()


def mbEnable():
    shapeList = cmds.ls(type="mesh")
    for mesh in shapeList:
        cmds.setAttr(mesh + ".rsMotionBlurDeformationEnable", 1)
        
def mipMapOn():
    mipList = cmds.ls(type='file')
    for mesh in mipList:
        cmds.setAttr(mesh + ".rsMipBias" , -4)
        
def mipMapOff():
    mipList = cmds.ls(type='file')
    for mesh in mipList:
        cmds.setAttr(mesh + ".rsMipBias" , 0)
        
def button1(ba):
    mbEnable()
    
def button2(bb):
    mipMapOn()
    
def button3(bc):
    mipMapOff()
    
def button4(bd):
    animCleaner()

def cleanerWindow():
    wHeight = int(225)
    wColumn = int(200)
    wBorder = int(125)
    wWide = int(25)
    bHeight = int(15)
    wWidth = wBorder + wColumn + wBorder

    window = cmds.window(title = 'Animation Submitter Prep', iconName = 'AC', widthHeight = (wWidth, wHeight))
    layout = cmds.rowColumnLayout(numberOfColumns=1, width = (wWidth))
    cmds.text(label = 'SAVE A NEW VERSION AND UNLOAD UNUSED REFS BEFORE RUNNING THE TOOL', align = 'center', height = (25))
    cmds.separator(style = 'none', height = (bHeight), width = (wWidth))
    
    layout = cmds.rowColumnLayout(numberOfColumns=3, columnWidth = [(1,wBorder),(2,wColumn),(3,wBorder)])
    cmds.separator(style = 'none' ,height = (bHeight), width = (wBorder)) #LefttBorder
    cmds.text(label = 'Step 1: **Please Choose One Option**', align = 'center', height = (5))
    cmds.separator(style = 'none' ,height = (bHeight), width = (wBorder)) #RightBorder
    
    cmds.separator(style = 'none' ,height = (bHeight), width = (wBorder)) #LefttBorder
    cmds.separator(style = 'none' ,height = (bHeight), width = (wColumn)) #MiddleBorder
    cmds.separator(style = 'none' ,height = (bHeight), width = (wBorder)) #RightBorder

    cmds.separator(style = 'none' ,height = (bHeight), width = (wBorder)) #LefttBorder
    cmds.button('my button', label = 'Mip Map for Lens Shader', command = button2)
    cmds.separator(style = 'none' ,height = (bHeight), width = (wBorder)) #RightBorder
    
    cmds.separator(style = 'none' ,height = (bHeight), width = (wBorder)) #LefttBorder
    cmds.separator(style = 'none' ,height = (bHeight), width = (wColumn)) #MiddleBorder
    cmds.separator(style = 'none' ,height = (bHeight), width = (wBorder)) #RightBorder
    
    cmds.separator(style = 'none' ,height = (bHeight), width = (wBorder)) #RightBorder
    cmds.button('my button', label = 'Mip Map Flat Screen', command = button3)
    cmds.separator(style = 'none' ,height = (bHeight), width = (wBorder)) #RightBorder

    cmds.separator(style = 'none' ,height = (bHeight), width = (wBorder)) #LefttBorder
    cmds.separator(style = 'none' ,height = (bHeight), width = (wColumn)) #MiddleBorder
    cmds.separator(style = 'none' ,height = (bHeight), width = (wBorder)) #RightBorder

    cmds.separator(style = 'none' ,height = (bHeight), width = (wBorder)) #LefttBorder
    cmds.text(label = 'Step 2: **Please Make Sure You Saved**', align = 'left', height = (5))
    cmds.separator(style = 'none' ,height = (bHeight), width = (wBorder)) #RightBorder

    cmds.separator(style = 'none' ,height = (bHeight), width = (wBorder)) #LefttBorder
    cmds.separator(style = 'none' ,height = (bHeight), width = (wColumn)) #MiddleBorder
    cmds.separator(style = 'none' ,height = (bHeight), width = (wBorder)) #RightBorder
    
    cmds.separator(style = 'none' ,height = (bHeight), width = (wBorder)) #LefttBorder
    cmds.button('my button', label = 'Render Scene Cleaner', command = button4)
    cmds.separator(style = 'none' ,height = (bHeight), width = (wBorder)) #RightBorder

    cmds.showWindow(window)
    
    
cleanerWindow()