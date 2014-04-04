__author__ = 'Jaime van Kessel'

from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.resources import resource_find
from kivy.graphics.transformation import Matrix
from kivy.graphics.opengl import *
from kivy.graphics import *

from Cura.machine.machine import Machine
from Cura.scene.scene import Scene
from Cura.gui.view3D.renderer import Renderer
from Cura.gui.view3D.machineRenderer import MachineRenderer

import numpy


class view3DWidget(Widget):
    """
    view3D is a view panel that has an associated scene which are drawn by the renderers of the view.
    """

    _translate_zoom = Translate(0, 0, -300.0)
    _rotate_pitch = Rotate(-60, 1, 0, 0)
    _rotate_yaw = Rotate(30, 0, 0, 1)
    _translate_viewpoint = Translate(0, 0, 0)

    def __init__(self):
        self.canvas = RenderContext(compute_normal_mat=True)
        self.canvas.shader.source = resource_find('flat_texture.glsl')
        super(view3DWidget, self).__init__(size_hint=(1.0, 1.0), pos_hint={'x': 0, 'y': 0})

        self._scene = None  #A view 3D has a scene responsible for data storage of what is in the 3D world.
        self._renderer_list = []  #The view holds a set of renderers, such as machine renderer or object renderer.
        self._machine = None  # Reference to the machine

        self._min_pitch = -170
        self._max_pitch = -10
        self._min_zoom = 1.0
        self._max_zoom = None

        self._viewport = None
        self._model_matrix = None
        self._proj_matrix = None

        machineRenderer = MachineRenderer()
        self.addRenderer(machineRenderer)
        self._focus_obj = None
        self._mouse_3D_pos = None

        self.bind(size=self.onSize)
        self.update_renderer()

    def addRenderer(self, renderer, prepend = False):
        assert(isinstance(renderer, Renderer))
        if prepend:
            self._renderer_list.insert(0, renderer)
        else:
            self._renderer_list.append(renderer)
        renderer.parent = self
        renderer.scene = self._scene
        renderer.machine = self._machine
        self.update_renderer()

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
        p0 = unproject(x, self._viewport[1] + self._viewport[3] - y, 0, self._model_matrix, self._proj_matrix, self._viewport)
        p1 = unproject(x, self._viewport[1] + self._viewport[3] - y, 1, self._model_matrix, self._proj_matrix, self._viewport)
        p0 -= self._view_target
        p1 -= self._view_target
        return p0, p1

    def update_renderer(self):
        self.canvas.clear()
        with self.canvas:
            #Set the basic rendering
            Callback(self.setup_gl_context)
            ClearColor(0.8, 0.8, 0.8, 1.0)
            ClearBuffers()
            PushMatrix()
            self.canvas.add(self._translate_zoom)
            self.canvas.add(self._rotate_pitch)
            self.canvas.add(self._rotate_yaw)
            self.canvas.add(self._translate_viewpoint)
            for renderer in self._renderer_list:
                renderer.addInstructionsTo(self.canvas)
            PopMatrix()
            Callback(self.reset_gl_context)

    def onSize(self, instance, value):
        asp = self.width / float(self.height)
        proj = Matrix()
        proj.perspective(45, asp, 1.0, 1000.0)
        self.canvas['projection_mat'] = proj
        self.canvas['diffuse_light'] = (1.0, 1.0, 0.8)
        self.canvas['ambient_light'] = (0.1, 0.1, 0.1)

    def on_touch_move(self, touch):
        if touch.button == 'right':
            self.setYaw(self._rotate_yaw.angle + touch.dsx * 360.0)
            self.setPitch(self._rotate_pitch.angle - touch.dsy * 360.0)

    def on_touch_up(self, touch):
        if touch.button == 'scrolldown':
            self._translate_zoom.z /= 1.1
        if touch.button == 'scrollup':
            self._translate_zoom.z *= 1.1

    def setPitch(self, value):
        self._rotate_pitch.angle = max(min(value, self._max_pitch), self._min_pitch)

    def setYaw(self, value):
        self._rotate_yaw.angle = value

    def setup_gl_context(self, *args):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glViewport(self.pos[0], self.pos[1], self.width, self.height)

    def reset_gl_context(self, *args):
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        glViewport(0, 0, self.get_root_window().width, self.get_root_window().height)
