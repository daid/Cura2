import numpy
import wx

from Cura.geometry.plane import Plane
from Cura.scene.displayableObject import DisplayableObject
from Cura.gui.tools.tool import Tool


class SelectAndMoveTool(Tool):
    """
    Tool which handles the selection and dragging of 3D objects in the 3D window.
    Also handles the view rotation. This is the last tool that gets mouse events, so other tools can override this behaviour.
    """
    def __init__(self, app):
        super(SelectAndMoveTool, self).__init__(app)
        self._state = ''

    def onKeyDown(self, key_code):
        if key_code == wx.WXK_DELETE:
            for o in self._app.getScene().getObjects():
                if o.isSelected():
                    self._app.getScene().removeObject(o)
            return True
        return False

    def onMouseDown(self, x, y, button):
        if button == 3:
            self._state = 'rotateView'
        elif button == 1:
            obj = self._app.getView().getFocusObject()
            self._dragPos3D = self._app.getView().getMousePos3D()
            if obj is not None and isinstance(obj, DisplayableObject):
                self._state = 'dragObjectOrSelect'
            else:
                self._state = 'panView'
        return True

    def onMouseMove(self, x, y, dx, dy):
        if self._state == 'rotateView':
            self._app.getView().setYaw(self._app.getView().getYaw() + dx)
            self._app.getView().setPitch(self._app.getView().getPitch() - dy)
        if self._state == 'panView':
            mouse_ray0 = self._app.getView().projectScreenPositionToRay(x - dx, y - dy)
            mouse_ray1 = self._app.getView().projectScreenPositionToRay(x, y)
            plane_z = Plane(numpy.array([0, 0, 1], numpy.float32), 0)
            cursor0_on_plane = plane_z.intersectRay(mouse_ray0)
            cursor1_on_plane = plane_z.intersectRay(mouse_ray1)
            pan_amount = cursor0_on_plane - cursor1_on_plane
            pan_amount[2] = 0.0
            self._app.getView().setViewTarget(self._app.getView().getViewTarget() + pan_amount)
        if self._state == 'dragObjectOrSelect':
            obj = self._app.getView().getFocusObject()
            if obj is not None and isinstance(obj, DisplayableObject) and not obj.isSelected():
                if not wx.GetKeyState(wx.WXK_CONTROL):
                    self._app.getScene().deselectAll()
                obj.setSelected(True)
            self._state = 'dragObject'
        if self._state == 'dragObject':
            mouse_ray = self._app.getView().projectScreenPositionToRay(x, y)
            plane_z = Plane(numpy.array([0, 0, 1], numpy.float32), self._dragPos3D[2])

            cursor_on_plane = plane_z.intersectRay(mouse_ray)
            delta = numpy.array(cursor_on_plane[0:2] - self._dragPos3D[0:2], numpy.float32)
            self._dragPos3D[0:2] = cursor_on_plane[0:2]

            for obj in self._app.getScene().getObjects():
                if obj.isSelected():
                    obj.setPosition(obj.getPosition() + delta, False)

    def onMouseUp(self, x, y, button):
        if self._state == 'dragObjectOrSelect':
            obj = self._app.getView().getFocusObject()
            if obj is not None and isinstance(obj, DisplayableObject):
                if not wx.GetKeyState(wx.WXK_CONTROL):
                    self._app.getScene().deselectAll()
                obj.setSelected(not obj.isSelected())
                if obj.isSelected():
                    self._app.getView().setViewTarget(numpy.append(obj.getPosition(), [obj.getSize()[2] / 2.0]))
                self._app.getView().refresh()
            self._state = ''
        if self._state == 'dragObject':
            for obj in self._app.getScene().getObjects():
                if obj.isSelected():
                    obj.setPosition(obj.getPosition())
        if button == 3 and self._state == 'rotateView':
            self._state = ''
