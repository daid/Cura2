
class Tool(object):
    """
    Base class for tools used in the 3D window.
    Every tool receives mouse events, and a tool can say on the MouseDown event that it wants to handle this event,
        at which point the other tools do not receive updates till this tool is done with the mouse.
    """
    def __init__(self, app):
        self.active = True
        self.visible = False
        self._app = app

    def onMouseDown(self, x, y, button):
        return False

    def onMouseMove(self, x, y, dx, dy):
        pass

    def onMouseUp(self, x, y, button):
        pass
