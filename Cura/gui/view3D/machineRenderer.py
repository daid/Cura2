__author__ = 'Jaime van Kessel'

from Cura.gui.view3D.renderer import Renderer
from Cura.resources import getMesh
from Cura.gui import openGLUtils

import OpenGL
#OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *


class MachineRenderer(Renderer):
    """
    Renderer responsible for rendering the 3D model of the machine
    """
    def __init__(self):
        super(MachineRenderer,self).__init__()
        self._platform_mesh = None

    def render(self):
        if self.machine is None:
            return

        w = self.machine.getSettingValueByKeyFloat('machine_width')
        d = self.machine.getSettingValueByKeyFloat('machine_depth')
        h = self.machine.getSettingValueByKeyFloat('machine_height')
        shape = self.machine.getShape()

        glColor3f(0, 0, 0)
        glBegin(GL_TRIANGLE_FAN)
        for point in shape:
            glVertex3f(point[0], point[1], 0.01)
        glEnd()

        mesh = getMesh('ultimaker_platform.stl')
        glColor3f(1, 1, 1)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1,1,1,1])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0,0,0,0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [0,0,0,0])
        for v in mesh.getVolumes():
            if 'VertexRenderer' not in v.metaData:
                v.metaData['VertexRenderer'] = openGLUtils.VertexRenderer(GL_TRIANGLES, v.vertexData)
            v.metaData['VertexRenderer'].render()
