__author__ = 'Jaime van Kessel'

from kivy.properties import BooleanProperty
from kivy.properties import ObjectProperty
from kivy.graphics import InstructionGroup
from kivy.graphics import Callback
from kivy.graphics.shader import Shader
from kivy.event import EventDispatcher
from kivy.resources import resource_find

from Cura.scene.scene import Scene
from Cura.machine.machine import Machine


class Renderer(EventDispatcher):
    """
    Abstract renderer class
    """

    active = BooleanProperty(True)
    machine = ObjectProperty(None)
    scene = ObjectProperty(None)
    def __init__(self):
        super(Renderer, self).__init__()
        self._instructions = InstructionGroup()
        self.bind(active=lambda i, v: self.__update())
        self.bind(machine=lambda i, v: self.__update())
        self.bind(scene=lambda i, v: self.__update())

    def __update(self):
        self._instructions.clear()
        if self.active:
            self._update(self._instructions)

    def addInstructionsTo(self, canvas):
        canvas.add(self._instructions)

    def _update(self, instructions):
        pass
