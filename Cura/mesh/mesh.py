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

    def getMetaData(self, key, default_value = None):
        if key in self.metaData:
            return self.metaData[key]
        return default_value
