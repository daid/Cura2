__author__ = 'Jaime van Kessel'
import math
import numpy


class DisplayableObject(object):
    #Base class for any object (save platform) in the scene.

    def __init__(self):
        self._position = numpy.zeros((2,))
        self._matrix = numpy.matrix(numpy.identity(3, numpy.float64))
        self._selected = False
        self._scene = None

    def setSelected(self,selected):
        self._selected = selected
        self._updated()

    def isSelected(self):
        return self._selected

    def getName(self):
        return self._name

    def getOriginFilename(self):
        return self._origin_filename

    def getPosition(self):
        return self._position

    def setPosition(self, new_pos):
        self._position = new_pos

    def setScene(self, scene):
        self._scene = scene

    def _updated(self):
        if self._scene is not None:
            self._scene.sceneUpdated(self)
