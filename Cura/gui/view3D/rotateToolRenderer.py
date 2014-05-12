
import math
import numpy
from OpenGL.GL import *

from Cura.gui import openGLUtils
from Cura.resources import getMesh
from Cura.gui.view3D.renderer import Renderer


def _generateCircle(pointCount=64, thickness=0.05):
    points = numpy.zeros((pointCount*4, 6), numpy.float32)
    for n in xrange(0, pointCount):
        px = math.cos(n / float(pointCount) * math.pi * 2)
        py = math.sin(n / float(pointCount) * math.pi * 2)
        points[n * 4 + 0] = [px, py, thickness, 0, 0, 1]
        points[n * 4 + 1] = [px, py, -thickness, 0, 0, -1]
        points[n * 4 + 2] = [px * (1.0 + thickness), py * (1.0 + thickness), 0.0, px, py, 0]
        points[n * 4 + 3] = [px * (1.0 - thickness), py * (1.0 - thickness), 0.0, -px, -py, 0]
    indices = numpy.zeros((pointCount * 8, 3), numpy.int32)

    for n in xrange(0, pointCount):
        i = n * 4
        j = (n * 4 + 4) % len(points)
        indices[n * 8 + 0] = [i + 0, i + 2, j + 0]
        indices[n * 8 + 1] = [i + 0, i + 3, j + 0]
        indices[n * 8 + 2] = [i + 1, i + 2, j + 1]
        indices[n * 8 + 3] = [i + 1, i + 3, j + 1]
        indices[n * 8 + 4] = [i + 2, j + 0, j + 2]
        indices[n * 8 + 5] = [i + 2, j + 1, j + 2]
        indices[n * 8 + 6] = [i + 3, j + 0, j + 3]
        indices[n * 8 + 7] = [i + 3, j + 1, j + 3]

    return openGLUtils.VertexRenderer(GL_TRIANGLES, points, indices=indices)


class RotateToolRenderer(Renderer):
    def __init__(self):
        super(RotateToolRenderer,self).__init__()
        self._shader = openGLUtils.GLShader(filename='selectionCircleShader.glsl')
        self._circle = _generateCircle()
        self._z_axis = None
        self._x_axis = None
        self._y_axis = None

    def render(self):
        glClear(GL_DEPTH_BUFFER_BIT)
        for obj in self.scene.getObjects():
            if not obj.isSelected():
                continue
            centerPosition = [obj.getPosition()[0], obj.getPosition()[1], obj.getSize()[2] / 2.0]
            glPushMatrix()
            glTranslatef(centerPosition[0], centerPosition[1], centerPosition[2])
            s = self.view.getZoom() / 10.0
            glScalef(s, s, s)
            self._shader.bind()
            glColor3f(0.5, 0.5, 1)
            self._circle.render()
            glColor3f(0.5, 1, 0.5)
            glRotatef(90, 1, 0, 0)
            self._circle.render()
            glColor3f(1.0, 0.5, 0.5)
            glRotatef(90, 0, 1, 0)
            self._circle.render()
            self._shader.unbind()
            glPopMatrix()

    def focusRender(self):
        glClear(GL_DEPTH_BUFFER_BIT)
        centerPosition = numpy.zeros((3,), numpy.float32)
        count = 0
        for obj in self.scene.getObjects():
            centerPosition += [obj.getPosition()[0], obj.getPosition()[1], obj.getSize()[2] / 2.0]
            count += 1
        if count < 1:
            return
        centerPosition /= count

        glPushMatrix()
        glTranslatef(centerPosition[0], centerPosition[1], centerPosition[2])
        s = self.view.getZoom() / 10.0
        glScalef(s, s, s)
        self.setCurrentFocusRenderObject(self._z_axis)
        self._circle.render()
        glRotatef(90, 1, 0, 0)
        self.setCurrentFocusRenderObject(self._y_axis)
        self._circle.render()
        glRotatef(90, 0, 1, 0)
        self.setCurrentFocusRenderObject(self._x_axis)
        self._circle.render()
        glPopMatrix()
