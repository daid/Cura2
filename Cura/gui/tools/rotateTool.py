import numpy
import wx

from Cura.gui.tools.tool import ToolboxTool
from Cura.gui.view3D.rotateToolRenderer import RotateToolRenderer


class RotateTool(ToolboxTool):
    """
    Tool which handles the selection and dragging of 3D objects in the 3D window.
    Also handles the view rotation. This is the last tool that gets mouse events, so other tools can override this behaviour.
    """
    def __init__(self, app):
        super(RotateTool, self).__init__(app, RotateToolRenderer())

    def onKeyDown(self, key_code):
        return False

    def onMouseDown(self, x, y, button):
        pass

    def onMouseMove(self, x, y, dx, dy):
        pass

    def onMouseUp(self, x, y, button):
        pass
