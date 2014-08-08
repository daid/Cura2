import math
import numpy
from OpenGL.GL import *

from Cura.gui import openGLUtils
from Cura.gui.view3D.renderer import Renderer


class MirrorFocusObject(object):
    def __init__(self, axis, obj):
        self._axis = axis
        self._obj = obj

    def getAxis(self):
        return self._axis

    def getObject(self):
        return self._obj

    def getName(self):
        return 'Mirror along %s' % (self._axis)


class MirrorToolRenderer(Renderer):
    def __init__(self):
        super(MirrorToolRenderer,self).__init__()
        self._shader = openGLUtils.GLShader(filename='selectionCircleShader.glsl')
        points = numpy.zeros((66, 6), numpy.float32)
        indices = numpy.zeros((64 * 3), numpy.int32)
        for n in xrange(0, 32):
            x = math.cos(n*math.pi*2/32.0)
            y = math.sin(n*math.pi*2/32.0)
            points[n] = [x * 2, y * 2, 4, x, y, 0]
            points[n+32] = [x * 2, y * 2, -4, x, y, 0]
            indices[n * 6] = n
            indices[n * 6 + 1] = (n + 1) % 32
            indices[n * 6 + 2] = 64
            indices[n * 6 + 3] = n + 32
            indices[n * 6 + 4] = (n + 1) % 32 + 32
            indices[n * 6 + 5] = 65
        points[64] = [0, 0, 10, 0, 0, 1]
        points[65] = [0, 0, -10, 0, 0, -1]
        self._arrow = openGLUtils.VertexRenderer(GL_TRIANGLES, points, True, indices)

    def render(self):
        glDisable(GL_LIGHTING)
        self._shader.bind()
        for obj in self.scene.getObjects():
            if not obj.isSelected():
                continue
            centerPosition = [obj.getPosition()[0], obj.getPosition()[1], obj.getSize()[2] / 2.0]
            glDepthFunc(GL_ALWAYS)
            glPushMatrix()
            glTranslatef(centerPosition[0], centerPosition[1], centerPosition[2])
            s = self.view.getZoom() / 150.0
            glScalef(s, s, s)
            self._renderArrows()
            glDepthFunc(GL_LEQUAL)
            self._renderArrows()
            glPopMatrix()
        self._shader.unbind()
        glDepthFunc(GL_LESS)
        glEnable(GL_LIGHTING)

    def focusRender(self):
        for obj in self.scene.getObjects():
            if not obj.isSelected():
                continue
            centerPosition = [obj.getPosition()[0], obj.getPosition()[1], obj.getSize()[2] / 2.0]
            glDepthFunc(GL_ALWAYS)
            glPushMatrix()
            glTranslatef(centerPosition[0], centerPosition[1], centerPosition[2])
            s = self.view.getZoom() / 150.0
            glScalef(s, s, s)
            self._renderArrows(obj)
            glPopMatrix()
        glDepthFunc(GL_LESS)

    def _renderArrows(self, as_focus=False):
        glPushMatrix()
        if as_focus:
            self.setCurrentFocusRenderObject(MirrorFocusObject('Z', as_focus))
        else:
            glColor3f(0.5, 1, 0.5)
        self._arrow.render()
        glRotate(90, 1, 0, 0)
        if as_focus:
            self.setCurrentFocusRenderObject(MirrorFocusObject('Y', as_focus))
        else:
            glColor3f(0.5, 0.5, 1)
        self._arrow.render()
        glRotate(90, 0, 1, 0)
        if as_focus:
            self.setCurrentFocusRenderObject(MirrorFocusObject('X', as_focus))
        else:
            glColor3f(1, 0.5, 0.5)
        self._arrow.render()
        glPopMatrix()
