
import math
import numpy
from OpenGL.GL import *

from Cura.geometry.plane import Plane
from Cura.gui import openGLUtils
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


class RotateFocusObject(object):
    def __init__(self, axis, obj):
        self._axis = axis
        self._obj = obj

    def getAxis(self):
        return self._axis

    def getObject(self):
        return self._obj


class RotateToolRenderer(Renderer):
    def __init__(self):
        super(RotateToolRenderer,self).__init__()
        self._shader = openGLUtils.GLShader(filename='selectionCircleShader.glsl')
        self._circle = _generateCircle()
        self._axisInfo = None
        self._axisList = [
            numpy.array([0, 0, 1], numpy.float32),
            numpy.array([0, 1, 0], numpy.float32),
            numpy.array([1, 0, 0], numpy.float32),
        ]

    def render(self):
        glDepthFunc(GL_ALWAYS)
        for obj in self.scene.getObjects():
            if not obj.isSelected():
                continue
            if self._axisInfo is not None and self._axisInfo.getObject() != obj:
                continue
            centerPosition = [obj.getPosition()[0], obj.getPosition()[1], obj.getSize()[2] / 2.0]
            glPushMatrix()
            glTranslatef(centerPosition[0], centerPosition[1], centerPosition[2])
            s = self.view.getZoom() / 10.0
            glScalef(s, s, s)
            self._shader.bind()
            glColor3f(0.5, 0.5, 1)
            if self._axisInfo is None or self._axisInfo.getAxis() is self._axisList[0]:
                self._circle.render()
            glColor3f(0.5, 1, 0.5)
            glRotatef(90, 1, 0, 0)
            if self._axisInfo is None or self._axisInfo.getAxis() is self._axisList[1]:
                self._circle.render()
            glColor3f(1.0, 0.5, 0.5)
            glRotatef(90, 0, 1, 0)
            if self._axisInfo is None or self._axisInfo.getAxis() is self._axisList[2]:
                self._circle.render()
            self._shader.unbind()
            glPopMatrix()
        glDepthFunc(GL_LESS)
        for obj in self.scene.getObjects():
            if not obj.isSelected():
                continue
            if self._axisInfo is not None and self._axisInfo.getObject() != obj:
                continue
            centerPosition = [obj.getPosition()[0], obj.getPosition()[1], obj.getSize()[2] / 2.0]
            glPushMatrix()
            glTranslatef(centerPosition[0], centerPosition[1], centerPosition[2])
            s = self.view.getZoom() / 10.0
            glScalef(s, s, s)
            self._shader.bind()
            glColor3f(0.5, 0.5, 1)
            if self._axisInfo is None or self._axisInfo.getAxis() is self._axisList[0]:
                self._circle.render()
            glColor3f(0.5, 1, 0.5)
            glRotatef(90, 1, 0, 0)
            if self._axisInfo is None or self._axisInfo.getAxis() is self._axisList[1]:
                self._circle.render()
            glColor3f(1.0, 0.5, 0.5)
            glRotatef(90, 0, 1, 0)
            if self._axisInfo is None or self._axisInfo.getAxis() is self._axisList[2]:
                self._circle.render()
            self._shader.unbind()
            glPopMatrix()

    def focusRender(self):
        if self._axisInfo is not None:
            return
        glDepthFunc(GL_ALWAYS)
        for obj in self.scene.getObjects():
            if not obj.isSelected():
                continue
            centerPosition = [obj.getPosition()[0], obj.getPosition()[1], obj.getSize()[2] / 2.0]
            glPushMatrix()
            glTranslatef(centerPosition[0], centerPosition[1], centerPosition[2])
            s = self.view.getZoom() / 10.0
            glScalef(s, s, s)
            self.setCurrentFocusRenderObject(RotateFocusObject(self._axisList[0], obj))
            self._circle.render()
            self.setCurrentFocusRenderObject(RotateFocusObject(self._axisList[1], obj))
            glRotatef(90, 1, 0, 0)
            self._circle.render()
            self.setCurrentFocusRenderObject(RotateFocusObject(self._axisList[2], obj))
            glRotatef(90, 0, 1, 0)
            self._circle.render()
            glPopMatrix()
        glDepthFunc(GL_LESS)
        for obj in self.scene.getObjects():
            if not obj.isSelected():
                continue
            centerPosition = [obj.getPosition()[0], obj.getPosition()[1], obj.getSize()[2] / 2.0]
            glPushMatrix()
            glTranslatef(centerPosition[0], centerPosition[1], centerPosition[2])
            s = self.view.getZoom() / 10.0
            glScalef(s, s, s)
            self.setCurrentFocusRenderObject(RotateFocusObject(self._axisList[0], obj))
            self._circle.render()
            self.setCurrentFocusRenderObject(RotateFocusObject(self._axisList[1], obj))
            glRotatef(90, 1, 0, 0)
            self._circle.render()
            self.setCurrentFocusRenderObject(RotateFocusObject(self._axisList[2], obj))
            glRotatef(90, 0, 1, 0)
            self._circle.render()
            glPopMatrix()
