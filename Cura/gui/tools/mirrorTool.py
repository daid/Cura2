import numpy

from Cura.gui.tools.tool import ToolboxTool
from Cura.gui.view3D.mirrorToolRenderer import MirrorToolRenderer
from Cura.gui.view3D.mirrorToolRenderer import MirrorFocusObject


class MirrorTool(ToolboxTool):
    def __init__(self, app):
        super(MirrorTool, self).__init__(app, MirrorToolRenderer())

    def getButtonIconName(self):
        return 'mirror_button.png'

    def onKeyDown(self, key_code):
        return False

    def onMouseDown(self, x, y, button):
        obj = self._app.getView().getFocusObject()
        if isinstance(obj, MirrorFocusObject):
            matrix = numpy.eye(3, dtype=numpy.float64)
            if obj.getAxis() == "X":
                matrix[0][0] = -1
            elif obj.getAxis() == "Y":
                matrix[1][1] = -1
            elif obj.getAxis() == "Z":
                matrix[2][2] = -1
            for obj in self._app.getScene().getObjects():
                if obj.isSelected():
                    obj.applyMatrix(matrix)
            return True
        return False

    def onMouseMove(self, x, y, dx, dy):
        pass

    def onMouseUp(self, x, y, button):
        pass

    def getName(self):
        return "Mirror"