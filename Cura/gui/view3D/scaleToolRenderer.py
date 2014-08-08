
import math
import numpy
from OpenGL.GL import *

from Cura.gui import openGLUtils
from Cura.gui.view3D.renderer import Renderer


class ScaleFocusObject(object):
    def __init__(self, axis, obj):
        self._axis = axis
        self._obj = obj

    def getAxis(self):
        return self._axis

    def getObject(self):
        return self._obj

    def getName(self):
        if self._axis == 'X':
            return 'Scale X: %0.2f (%0.1fmm)' % (self._obj.getScale()[0], self._obj.getSize()[0])
        if self._axis == 'Y':
            return 'Scale Y: %0.2f (%0.1fmm)' % (self._obj.getScale()[1], self._obj.getSize()[1])
        if self._axis == 'Z':
            return 'Scale Z: %0.2f (%0.1fmm)' % (self._obj.getScale()[2], self._obj.getSize()[2])
        scale = self._obj.getScale()
        if scale[0] == scale[1] and scale[0] == scale[2]:
            return 'Scale: %0.2f (%0.1fmm, %0.1fmm, %0.1fmm)' % (self._obj.getScale()[0], self._obj.getSize()[0], self._obj.getSize()[1], self._obj.getSize()[2])
        return 'Scale: %0.2f %0.2f %0.2f (%0.1fmm, %0.1fmm, %0.1fmm)' % (self._obj.getScale()[0], self._obj.getScale()[1], self._obj.getScale()[2], self._obj.getSize()[0], self._obj.getSize()[1], self._obj.getSize()[2])


class ScaleToolRenderer(Renderer):
    def __init__(self):
        super(ScaleToolRenderer,self).__init__()
        self._shader = openGLUtils.GLShader(filename='selectionCircleShader.glsl')
        points = numpy.array([
            [-1, -1, -1, -1, -1, -1],
            [ 1, -1, -1,  1, -1, -1],
            [-1,  1, -1, -1,  1, -1],
            [ 1,  1, -1,  1,  1, -1],
            [-1, -1,  1, -1, -1,  1],
            [ 1, -1,  1,  1, -1,  1],
            [-1,  1,  1, -1,  1,  1],
            [ 1,  1,  1,  1,  1,  1]
        ], numpy.float32)
        indices = numpy.array([
            0, 1, 3, 2,
            4, 5, 7, 6,
            0, 1, 5, 4,
            3, 2, 6, 7,
            2, 0, 4, 6,
            1, 3, 7, 5
        ], numpy.int32)
        self._box = openGLUtils.VertexRenderer(GL_QUADS, points, True, indices)

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
            glColor3f(1, 1, 1)
            glBegin(GL_LINES)
            glVertex3f(0, 0, 0)
            glVertex3f(10, 0, 0)
            glVertex3f(0, 0, 0)
            glVertex3f(0, 10, 0)
            glVertex3f(0, 0, 0)
            glVertex3f(0, 0, 10)
            glEnd()
            self._box.render()
            glPushMatrix()
            glColor3f(1, 0.5, 0.5)
            glTranslate(10, 0, 0)
            self._box.render()
            glPopMatrix()
            glPushMatrix()
            glTranslate(0, 10, 0)
            glColor3f(0.5, 0.5, 1)
            self._box.render()
            glPopMatrix()
            glPushMatrix()
            glColor3f(0.5, 1, 0.5)
            glTranslate(0, 0, 10)
            self._box.render()
            glPopMatrix()

            glDepthFunc(GL_LEQUAL)

            glColor3f(1, 1, 1)
            self._box.render()
            glPushMatrix()
            glColor3f(1, 0.5, 0.5)
            glTranslate(10, 0, 0)
            self._box.render()
            glPopMatrix()
            glPushMatrix()
            glTranslate(0, 10, 0)
            glColor3f(0.5, 0.5, 1)
            self._box.render()
            glPopMatrix()
            glPushMatrix()
            glColor3f(0.5, 1, 0.5)
            glTranslate(0, 0, 10)
            self._box.render()
            glPopMatrix()

            glPopMatrix()
        glEnable(GL_LIGHTING)
        glDepthFunc(GL_LESS)
        self._shader.unbind()

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
            self.setCurrentFocusRenderObject(ScaleFocusObject('uniform', obj))
            self._box.render()
            glPushMatrix()
            glColor3f(1, 0, 0)
            glTranslate(10, 0, 0)
            self.setCurrentFocusRenderObject(ScaleFocusObject('X', obj))
            self._box.render()
            glPopMatrix()
            glPushMatrix()
            glTranslate(0, 10, 0)
            glColor3f(0, 0, 1)
            self.setCurrentFocusRenderObject(ScaleFocusObject('Y', obj))
            self._box.render()
            glPopMatrix()
            glPushMatrix()
            glColor3f(0, 1, 0)
            glTranslate(0, 0, 10)
            self.setCurrentFocusRenderObject(ScaleFocusObject('Z', obj))
            self._box.render()
            glPopMatrix()
            glPopMatrix()
            glDepthFunc(GL_LEQUAL)
        glDepthFunc(GL_LESS)

