__author__ = 'Jaime van Kessel'

import os
import threading

from Cura.meshLoaders.meshLoader import loadMeshes
from Cura.scene.displayableObject import DisplayableObject

import numpy
numpy.seterr(all='ignore')


class PrintableObject(DisplayableObject):
    """
    A printable object is an object that can be printed and is on the build platform.
    It contains 1 or more Meshes. Where more meshes are used for multi-extrusion.

    Each object has a 3x3 transformation matrix to rotate/scale the object.
    This object also keeps track of the 2D boundary polygon used for object collision in the objectScene class.
    """
    def __init__(self, originFilename):
        super(PrintableObject,self).__init__()
        self._originFilename = originFilename
        if originFilename is None:
            self._name = 'None'
        else:
            self._name = os.path.basename(originFilename)
        if '.' in self._name:
            self._name = os.path.splitext(self._name)[0]
        self._mesh = None
        self._matrix = numpy.identity(3, numpy.float64)
        self._position = numpy.zeros((2,))

    def loadMesh(self, filename):
        self._thread = threading.Thread(target=self._loadMeshThread, args=(filename,))
        self._thread.daemon = True
        self._thread.start()

    def _loadMeshThread(self, filename):
        self._mesh = None
        mesh = loadMeshes(filename)[0]
        self._mesh = mesh

    def getMesh(self):
        return self._mesh
