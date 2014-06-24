__author__ = 'Jaime van Kessel'

from Cura.gui.view3D.renderer import Renderer
from Cura.resources import getMesh
from Cura.gui import openGLUtils

from OpenGL.GL import *


class MachineRenderer(Renderer):
    """
    Renderer responsible for rendering the 3D model of the machine
    """
    def __init__(self):
        super(MachineRenderer,self).__init__()
        self._shader = openGLUtils.GLShader(filename='objectShader.glsl')
        self._backgroundTexture = openGLUtils.GLTexture('background.png')
        self._platformTexture = openGLUtils.GLTexture('checkerboard.png', filter='nearest')

    def render(self):
        self._backgroundTexture.bind()
        glDisable(GL_DEPTH_TEST)
        glColor3f(1, 1, 1)
        glPushMatrix()
        glLoadIdentity()
        glBegin(GL_TRIANGLE_FAN)
        glTexCoord2f(0, 0)
        glVertex3f(-1, -1, -1)
        glTexCoord2f(1, 0)
        glVertex3f(-1, 1, -1)
        glTexCoord2f(1, 1)
        glVertex3f(1, 1, -1)
        glTexCoord2f(0, 1)
        glVertex3f(1, -1, -1)
        glEnd()
        glPopMatrix()
        glEnable(GL_DEPTH_TEST)
        self._backgroundTexture.unbind()
        if self.machine is None:
            return

        h = self.machine.getSettingValueByKeyFloat('machine_height')
        shape = self.machine.getShape()

        glColor3f(1, 1, 1)
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glEnable(GL_CULL_FACE)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self._platformTexture.bind()
        glBegin(GL_TRIANGLE_FAN)
        for point in shape:
            glTexCoord2f(point[0] / 20.0, point[1] / 20.0)
            glVertex3f(point[0], point[1], 0.02)
        glEnd()
        self._platformTexture.unbind()
        glDisable(GL_CULL_FACE)

        mesh = getMesh('ultimaker2_platform.obj')
        self._shader.bind()
        glColor3f(1, 1, 1)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0, 0, 0, 0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [0, 0, 0, 0])
        for v in mesh.getVolumes():
            if 'VertexRenderer' not in v.metaData:
                v.metaData['VertexRenderer'] = openGLUtils.VertexRenderer(GL_TRIANGLES, v.vertexData)
            v.metaData['VertexRenderer'].render()
        self._shader.unbind()
