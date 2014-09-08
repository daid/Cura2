import numpy

from OpenGL.GL import *
from OpenGL.GLU import *

from Cura.geometry.ray import Ray
from Cura.machine.machine import Machine
from Cura.scene.scene import Scene
from Cura.gui import openGLUtils
from Cura.gui.view3D.renderer import Renderer
from Cura.gui.view3D.machineRenderer import MachineRenderer

class View3D(object):
    """
    view3D handles 3D viewing of an OpenGL viewport. It has multiple renderers which are called to render different
    objects in the 3D view.
    """

    def __init__(self):
        self._scene = None  # A view 3D has a scene responsible for data storage of what is in the 3D world.
        self._renderer_list = []  # The view holds a set of renderers, such as machine renderer or object renderer.
        self._machine = None  # Reference to the machine
        self._openGLWindow = None
        self._focus_debug = False

        self._yaw = 30
        self._pitch = 60
        self._zoom = 300
        self._projection = 'perspective'
        self._view_target = [0.0, 0.0, 0.0]

        self._min_pitch = 10
        self._max_pitch = 170
        self._min_zoom = 1.0
        self._max_zoom = 400

        self._viewport = None
        self._model_matrix = None
        self._proj_matrix = None

        self._mousePos = None
        self._mousePos3D = numpy.zeros((3,), numpy.float32)
        self._focusObject = None
        self._focusIdx = None
        self._focusObjectList = None

        machineRenderer = MachineRenderer()
        self.addRenderer(machineRenderer)

    def setViewDirection(self, direction):
        if direction == '3D':
            self._yaw = 30
            self._pitch = 60
            self._zoom = 300
            self._projection = 'perspective'
        elif direction == 'Right':
            self._yaw = -90
            self._pitch = 90
            self._zoom = 300
            self._projection = 'orthogonal'
        elif direction == 'Front':
            self._yaw = 0
            self._pitch = 90
            self._zoom = 300
            self._projection = 'orthogonal'
        elif direction == 'Top':
            self._yaw = 0
            self._pitch = 0
            self._zoom = 300
            self._projection = 'orthogonal'
        self.refresh()

    def setViewTarget(self, point):
        self._view_target = point
        self.refresh()

    def addRenderer(self, renderer):
        assert(isinstance(renderer, Renderer))
        self._renderer_list.append(renderer)
        renderer.view = self
        renderer.scene = self._scene
        renderer.machine = self._machine

    def setScene(self,scene):
        assert(issubclass(type(scene), Scene))
        self._scene = scene
        for render in self._renderer_list:
            render.scene = scene

    def getScene(self):
        return self._scene

    def setMachine(self,machine):
        assert(isinstance(machine,Machine))
        self._machine = machine
        self._max_zoom = numpy.max(machine.getSize()) * 3
        for renderer in self._renderer_list:
            renderer.machine = machine

    def getMachine(self):
        return self._machine

    def setOpenGLWindow(self, window):
        self._openGLWindow = window

    def refresh(self):
        if self._openGLWindow is not None:
            self._openGLWindow.queueRefresh()

    def updateMousePos(self, x, y):
        self._mousePos = (x, y)
        self.refresh()

    def getPitch(self):
        return self._pitch

    def getYaw(self):
        return self._yaw

    def setPitch(self, value):
        self._pitch = max(min(value, self._max_pitch), self._min_pitch)
        self._projection = 'perspective'
        self.refresh()

    def setYaw(self, value):
        self._yaw = value
        self.refresh()

    def deltaZoom(self, delta):
        self.setZoom(self._zoom * (1.0 - delta / 10.0))

    def getZoom(self):
        return self._zoom

    def setZoom(self, zoom):
        self._zoom = zoom
        if self._zoom < self._min_zoom:
            self._zoom = self._min_zoom
        if self._zoom > self._max_zoom:
            self._zoom = self._max_zoom
        self.refresh()

    def render(self, panel):
        self._init3DProjection(panel.GetSize(), panel.isUpsideDown())

        if self._mousePos is not None:
            glClearColor(1, 1, 1, 0.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glDisable(GL_LIGHTING)
            glDisable(GL_BLEND)

            self._focusIdx = 0
            self._focusObjectList = []
            for renderer in self._renderer_list:
                if renderer.active:
                    renderer.focusRender()
            self._focusIdx = None

            n = glReadPixels(self._mousePos[0], self._viewport[1] + self._viewport[3] - 1 - self._mousePos[1], 1, 1, GL_RGBA, GL_UNSIGNED_INT_8_8_8_8)[0][0]
            f = glReadPixels(self._mousePos[0], self._viewport[1] + self._viewport[3] - 1 - self._mousePos[1], 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)[0][0]
            self._mousePos3D = self._unproject(self._mousePos[0], self._mousePos[1], f)
            if (n & 0xFF) == 0xFF and (n >> 8) < len(self._focusObjectList):   # If the Alpha is is not 0xFF we have read a pixel not on the rendering buffer.
                self._focusObject = self._focusObjectList[n >> 8]
            else:
                self._focusObject = None

            self._mousePos = None

        if self._focus_debug:
            glClearColor(1, 1, 1, 0.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glDisable(GL_LIGHTING)
            glDisable(GL_BLEND)

            self._focusIdx = 0
            self._focusObjectList = []
            for renderer in self._renderer_list:
                if renderer.active:
                    renderer.focusRender()
            self._focusIdx = None
            return

        glClearColor(0.8, 0.8, 0.8, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for renderer in self._renderer_list:
            if renderer.active:
                renderer.render()

    def _init3DProjection(self, size, upsideDown):
        glViewport(0, 0, size.GetWidth(), size.GetHeight())
        glLoadIdentity()

        glLightfv(GL_LIGHT0, GL_POSITION, [0.2, 0.2, 1.0, 0.0])

        glDisable(GL_RESCALE_NORMAL)
        glDisable(GL_LIGHTING)
        glDisable(GL_LIGHT0)
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        glDisable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glClearStencil(0)
        glClearDepth(1.0)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = float(size.GetWidth()) / float(size.GetHeight())
        if self._projection == 'perspective':
            gluPerspective(45.0, aspect, 1.0, self._max_zoom * 2)
        else:
            z = self._zoom / 2.0
            glOrtho(-z * aspect, z * aspect, -z, z, 1.0, self._max_zoom * 2)

        if upsideDown:
            glScale(1, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

        glTranslate(0,0,-self._zoom)
        glRotate(-self._pitch, 1,0,0)
        glRotate(self._yaw, 0,0,1)
        glTranslate(-self._view_target[0], -self._view_target[1], -self._view_target[2])

        self._viewport = glGetIntegerv(GL_VIEWPORT)
        self._modelMatrix = glGetDoublev(GL_MODELVIEW_MATRIX)
        self._projMatrix = glGetDoublev(GL_PROJECTION_MATRIX)

    def setCurrentFocusRenderObject(self, obj):
        assert self._focusIdx is not None
        glColor4ub((self._focusIdx >> 16) & 0xFF, (self._focusIdx >> 8) & 0xFF, self._focusIdx & 0xFF, 0xFF)
        self._focusObjectList.append(obj)
        if self._focus_debug:
            self._focusIdx += 64
        else:
            self._focusIdx += 1

    def getFocusObject(self):
        return self._focusObject

    def clearFocusObject(self):
        self._focusObject = None

    def getMousePos3D(self):
        return self._mousePos3D

    def _unproject(self, x, y, f):
        return openGLUtils.unproject(x, self._viewport[1] + self._viewport[3] - y, f, self._modelMatrix, self._projMatrix, self._viewport) - self._view_target

    def projectScreenPositionToRay(self, x, y):
        if self._viewport is None:
            return Ray(numpy.array([0, 0, 0], numpy.float32), numpy.array([0, 0, 0], numpy.float32))
        startPoint = self._unproject(x, y, 0.0)
        endPoint = self._unproject(x, y, 1.0)
        return Ray(startPoint, endPoint - startPoint)
