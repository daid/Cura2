import numpy

from Cura.geometry.ray import Ray
from Cura.gui.tools.tool import ToolboxTool
from Cura.gui.view3D.scaleToolRenderer import ScaleFocusObject
from Cura.gui.view3D.scaleToolRenderer import ScaleToolRenderer


class ScaleTool(ToolboxTool):
    def __init__(self, app):
        super(ScaleTool, self).__init__(app, ScaleToolRenderer())

    def getButtonIconName(self):
        return 'scale_button.png'

    def getName(self):
        return "Scale"

    def onKeyDown(self, key_code):
        return False

    def onMouseDown(self, x, y, button):
        obj = self._app.getView().getFocusObject()
        if isinstance(obj, ScaleFocusObject):
            self._scale_info = obj
            return True
        return False

    def onMouseMove(self, x, y, dx, dy):
        matrix = self.calculateMatrix(x, y)
        for obj in self._app.getScene().getObjects():
            if obj.isSelected():
                obj.setTempMatrix(matrix)

    def onMouseUp(self, x, y, button):
        matrix = self.calculateMatrix(x, y)
        for obj in self._app.getScene().getObjects():
            if obj.isSelected():
                obj.applyMatrix(matrix)
        self._renderer._scale_info = None

    def calculateMatrix(self, x, y):
        obj = self._scale_info.getObject()
        axis = self._scale_info.getAxis()
        center_position = numpy.array([obj.getPosition()[0], obj.getPosition()[1], obj.getSize()[2] / 2.0], numpy.float32)

        if axis == 'X':
            axisNr = 0
        elif axis == 'Y':
            axisNr = 1
        elif axis == 'Z':
            axisNr = 2
        else:
            axisNr = 2
            center_position[2] -= 10.0 * (self._app.getView().getZoom() / 150.0)
        direction = numpy.array([0, 0, 0], numpy.float32)
        direction[axisNr] = 1.0
        axisRay = Ray(center_position, direction)
        mouseRay = self._app.getView().projectScreenPositionToRay(x, y)
        intersection = mouseRay.intersectWithRay(axisRay)
        scale = (intersection[axisNr] - center_position[axisNr]) / 10.0 / (self._app.getView().getZoom() / 150.0)
        objScale = obj.getScale()
        if axis == 'uniform':
            objScale = (objScale[0] + objScale[1] + objScale[2]) / 3.0
        else:
            objScale = objScale[axisNr]
        scale = round(objScale * scale, 1) / objScale

        if axis == 'uniform':
            matrix = numpy.eye(3, dtype=numpy.float64) * scale
        else:
            matrix = numpy.eye(3, dtype=numpy.float64)
            matrix[axisNr, axisNr] = scale

        return matrix
