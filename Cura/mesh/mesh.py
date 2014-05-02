__author__ = 'Jaime van Kessel'

from Cura.mesh.volume import MeshVolume
import numpy


class Mesh(object):
    def __init__(self):
        self._volumes = []
        self.metaData = {}

    def newVolume(self):
        self._volumes.append(MeshVolume(self))
        return self._volumes[-1]

    def getVolumes(self):
        return self._volumes
