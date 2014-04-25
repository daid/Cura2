from Cura.machine.machine import Machine
from Cura.scene.scene import Scene
from Cura.gui import openGLUtils
from Cura.gui.view3D.renderer import Renderer
from Cura.gui.view3D.machineRenderer import MachineRenderer

import numpy

from OpenGL.GL import *
from OpenGL.GLU import *


class View3D(object):
    """
    view3D handles 3D viewing of an OpenGL viewport. It has multiple renderers which are called to render different
    objects in the 3D view.
    """

    def __init__(self):
        self._scene = None  # A view 3D has a scene responsible for data storage of what is in the 3D world.
        self._renderer_list = []  # The view holds a set of renderers, such as machine renderer or object renderer.
        self._machine = None  # Reference to the machine

        self._yaw = 30
        self._pitch = 60
        self._zoom = 300
        self._viewTarget = [0.0, 0.0, 0.0]

        self._min_pitch = -170
        self._max_pitch = -10
        self._min_zoom = 1.0
        self._max_zoom = 400

        self._viewport = None
        self._model_matrix = None
        self._proj_matrix = None

        machineRenderer = MachineRenderer()
        self.addRenderer(machineRenderer)
        self._focus_obj = None
        self._mouse_3D_pos = None

    def addRenderer(self, renderer, prepend = False):
        assert(isinstance(renderer, Renderer))
        if prepend:
            self._renderer_list.insert(0, renderer)
        else:
            self._renderer_list.append(renderer)
        renderer.parent = self
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

    def getMouseRay(self, x, y):
        if self._viewport is None:
            return numpy.array([0,0,0],numpy.float32), numpy.array([0,0,1],numpy.float32)
        p0 = openGLUtils.unproject(x, self._viewport[1] + self._viewport[3] - y, 0, self._model_matrix, self._proj_matrix, self._viewport)
        p1 = openGLUtils.unproject(x, self._viewport[1] + self._viewport[3] - y, 1, self._model_matrix, self._proj_matrix, self._viewport)
        p0 -= self._view_target
        p1 -= self._view_target
        return p0, p1

    def setPitch(self, value):
        self._pitch = max(min(value, self._max_pitch), self._min_pitch)

    def setYaw(self, value):
        self._yaw = value

    def render(self, panel):
        self._init3DProjection(panel.GetSize())

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        for renderer in self._renderer_list:
            if renderer.active:
                renderer.render()

    def _init3DProjection(self, size):
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

        glClearColor(0.8, 0.8, 0.8, 1.0)
        glClearStencil(0)
        glClearDepth(1.0)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = float(size.GetWidth()) / float(size.GetHeight())
        gluPerspective(45.0, aspect, 1.0, self._max_zoom * 2)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

        glTranslate(0,0,-self._zoom)
        glRotate(-self._pitch, 1,0,0)
        glRotate(self._yaw, 0,0,1)
        glTranslate(-self._viewTarget[0], -self._viewTarget[1], -self._viewTarget[2])

        self._viewport = glGetIntegerv(GL_VIEWPORT)
        self._modelMatrix = glGetDoublev(GL_MODELVIEW_MATRIX)
        self._projMatrix = glGetDoublev(GL_PROJECTION_MATRIX)
