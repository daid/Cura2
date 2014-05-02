__author__ = 'Jaime van Kessel'

from Cura.scene.displayableObject import DisplayableObject


class Scene(object):
    """
    Base scene class. Holds all objects (all objects on platform, etc) in the 3D world.
    """
    def __init__(self):
        self._machine = None  # Scene has a reference to the machine
        self._view = None
        self._object_list = []

    def getObjects(self):
        return self._object_list

    def setMachine(self, machine):
        self._machine = machine

    def addObject(self, object):
        self._object_list.append(object)
        object.setScene(self)
        self.sceneUpdated(object)

    def sceneUpdated(self, updatedObject=None):
        self._view.refresh()

    def setView(self, view):
        self._view = view
