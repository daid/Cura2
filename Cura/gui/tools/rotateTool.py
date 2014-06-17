import numpy
import math

from Cura.geometry.plane import Plane
from Cura.gui.tools.tool import ToolboxTool
from Cura.gui.view3D.rotateToolRenderer import RotateToolRenderer
from Cura.gui.view3D.rotateToolRenderer import RotateFocusObject


class RotateTool(ToolboxTool):
    """
    Tool which handles the rotation of 3D objects, gives a rotation handle which can be used to rotate the object around the X/Y/Z axis
    """
    def __init__(self, app):
        super(RotateTool, self).__init__(app, RotateToolRenderer())

    def getButtonIconName(self):
        return 'rotate_button.png'

    def onKeyDown(self, key_code):
        return False

    def onMouseDown(self, x, y, button):
        obj = self._app.getView().getFocusObject()
        if isinstance(obj, RotateFocusObject):
            self._renderer._axisInfo = obj
            self._mouse_start = (x, y)
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
        self._renderer._axisInfo = None

    def calculateMatrix(self, x, y):
        objectCenterPos = numpy.append(self._renderer._axisInfo.getObject().getPosition(), [self._renderer._axisInfo.getObject().getSize()[2] / 2.0])
        plane = Plane(self._renderer._axisInfo.getAxis(), 0)
        mousePoint0 = plane.intersectRay(self._app.getView().projectScreenPositionToRay(*self._mouse_start))
        mousePoint1 = plane.intersectRay(self._app.getView().projectScreenPositionToRay(x, y))
        centerPoint = plane.pointOnPlane(objectCenterPos)
        mouseVector0 = mousePoint0 - centerPoint
        mouseVector0 /= numpy.linalg.norm(mouseVector0)
        mouseVector1 = mousePoint1 - centerPoint
        mouseVector1 /= numpy.linalg.norm(mouseVector1)
        angle = max(-1.0, min(1.0, numpy.dot(mouseVector0, mouseVector1)))
        angle = math.acos(angle)
        angleStepSize = 15.0
        angle = round(angle / math.pi * 180.0 / angleStepSize) * math.pi / 180.0 * angleStepSize
        if numpy.dot(mouseVector1, numpy.cross(mouseVector0, plane.normal)) > 0:
            angle = -angle

        d = numpy.array(self._renderer._axisInfo.getAxis(), dtype=numpy.float64)
        d /= numpy.linalg.norm(d)

        eye = numpy.eye(3, dtype=numpy.float64)
        ddt = numpy.outer(d, d)
        skew = numpy.array([
            [0, d[2], -d[1]],
            [-d[2], 0, d[0]],
            [d[1], -d[0], 0]],
            numpy.float64)

        matrix = ddt + numpy.cos(angle) * (eye - ddt) + numpy.sin(angle) * skew
        return matrix
