import numpy

from Cura.gui.tools.tool import ToolboxTool


class MirrorTool(ToolboxTool):
    def __init__(self, app):
        super(MirrorTool, self).__init__(app, None)

    def getButtonIconName(self):
        return 'mirror_button.png'

    def onKeyDown(self, key_code):
        return False

    def onMouseDown(self, x, y, button):
        return False

    def onMouseMove(self, x, y, dx, dy):
        pass

    def onMouseUp(self, x, y, button):
        pass
