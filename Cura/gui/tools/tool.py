
class Tool(object):
    """
    Base class for tools used in the 3D window.
    Every tool receives mouse events, and a tool can say on the MouseDown event that it wants to handle this event,
        at which point the other tools do not receive updates till this tool is done with the mouse.
    """
    def __init__(self, app):
        self._active = True
        self._app = app

    def onKeyDown(self, key_code):
        return False

    def onMouseDown(self, x, y, button):
        return False

    def onMouseMove(self, x, y, dx, dy):
        pass

    def onMouseUp(self, x, y, button):
        pass

    def hasActiveButton(self):
        return False

    def isActive(self):
        return self._active

    def setActive(self, value):
        self._active = value


class ToolboxTool(Tool):
    """
    Base class for tools in the top toolbox, these can be activated or de-activated by pressing the tool button.
    They can have an associated renderer and focus-renderer with it.
    """
    def __init__(self, app, renderer=None):
        super(ToolboxTool, self).__init__(app)
        self._renderer = renderer
        self.setActive(False)
        if renderer is not None:
            app.getView().addRenderer(renderer)

    def hasActiveButton(self):
        return True

    def getButtonIconName(self):
        return 'rotate_button.png'

    def setActive(self, value):
        if self._renderer is not None:
            self._renderer.active = value
        super(ToolboxTool, self).setActive(value)
