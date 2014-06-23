from OpenGL.GL import *

from Cura.gui import openGLUtils
from Cura.resources import getMesh
from Cura.gui.view3D.renderer import Renderer


class ToolpathRenderer(Renderer):
    def __init__(self):
        super(ToolpathRenderer,self).__init__()

    def render(self):
        pass

    def focusRender(self):
        pass
