import numpy

from Cura.gui.tools.tool import Tool
from Cura.gui.view3D.selectionRenderer import SelectionRenderer


class SelectAndMoveTool(Tool):
    """
    Tool which handles the selection and dragging of 3D objects in the 3D window.
    Also handles the view rotation. This is the last tool that gets mouse events, so other tools can override this behaviour.
    """
    def __init__(self, app):
        super(SelectAndMoveTool, self).__init__(app)
        self._state = ''

        app.getView().addFocusRenderer(SelectionRenderer())

    def onMouseDown(self, x, y, button):
        if button == 3:
            self._state = 'rotateView'
        if button == 1:
            obj = self._app.getView().getFocusObject()
            if obj is not None:
                for o in self._app.getScene().getObjects():
                    o.setSelected(False)
                obj.setSelected(not obj.isSelected())
            self._dragPos3D = self._app.getView().getMousePos3D()
            self._state = 'dragObject'
        return True

    def onMouseMove(self, x, y, dx, dy):
        if self._state == 'rotateView':
            self._app.getView().setYaw(self._app.getView().getYaw() + dx)
            self._app.getView().setPitch(self._app.getView().getPitch() - dy)
        if self._state == 'dragObject':
            p0, p1 = self._app.getView().projectScreenPositionToRay(x, y)
            z = self._dragPos3D[2]
            if z < 0:
                self._dragPos3D = p0 - (p1 - p0) * (p0[2] / (p1[2] - p0[2]))
            else:
                p0[2] -= z
                p1[2] -= z
                cursorZ0 = p0 - (p1 - p0) * (p0[2] / (p1[2] - p0[2]))
                delta = numpy.array(cursorZ0[0:2] - self._dragPos3D[0:2], numpy.float32)
                self._dragPos3D[0:2] = cursorZ0[0:2]

                for obj in self._app.getScene().getObjects():
                    if obj.isSelected():
                        obj.setPosition(obj.getPosition() + delta)

    def onMouseUp(self, x, y, button):
        if button == 3 and self._state == 'rotateView':
            self._state = ''
