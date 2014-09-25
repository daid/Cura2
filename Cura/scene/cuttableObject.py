import os
import math
import threading
import numpy

from Cura.geometry import polygon
from Cura.vectorLoaders.vectorLoader import loadVector
from Cura.scene.displayableObject import DisplayableObject


class CuttableObject(DisplayableObject):
    """
    A printable object is an object that can be printed and is on the build platform.
    It contains 1 or more Meshes. Where more meshes are used for multi-extrusion.

    Each object has a 3x3 transformation matrix to rotate/scale the object.
    This object also keeps track of the 2D boundary polygon used for object collision in the objectScene class.
    """
    def __init__(self, originFilename):
        super(CuttableObject,self).__init__()
        if originFilename is None:
            self._name = 'None'
        else:
            self._name = os.path.basename(originFilename)
        if '.' in self._name:
            self._name = os.path.splitext(self._name)[0]
        self._mesh = None
        self._vector = None
        self._info = {}

        self._vMin = numpy.array([-1, -1, -1], numpy.float32)
        self._vMax = numpy.array([1, 1, 1], numpy.float32)
        self._boundarySphere = 1
        self._drawOffset = numpy.zeros((3,), numpy.float32)

    def loadVector(self, filename):
        self._thread = threading.Thread(target=self._loadVectorThread, args=(filename,))
        self._thread.daemon = True
        self._thread.start()

    def getVector(self):
        return self._vector

    def _loadVectorThread(self, filename):
        self._mesh = None
        self._vector = None
        vector = loadVector(filename)
        self._vector = vector
        self._updated()
        self._updateMeshInfoThreadFunction()

    def setMatrix(self, matrix):
        super(CuttableObject, self).setMatrix(matrix)
        self._updateMeshInfo()

    def _updateMeshInfo(self):
        self._thread = threading.Thread(target=self._updateMeshInfoThreadFunction)
        self._thread.daemon = True
        self._thread.start()

    def _updateMeshInfoThreadFunction(self):
        transformedMin = numpy.array([999999999999,999999999999,999999999999], numpy.float32)
        transformedMax = numpy.array([-999999999999,-999999999999,-999999999999], numpy.float32)
        boundarySphere = 0.0
        hull = numpy.zeros((0, 2), numpy.int)
        if self._mesh is not None:
            for v in self._mesh.getVolumes():
                vertexData = (numpy.matrix(v.vertexData[::, 0:3], copy = False) * numpy.matrix(self._matrix, numpy.float32)).getA()
                hull = polygon.convexHull(numpy.concatenate((numpy.rint(vertexData[:,0:2]).astype(int), hull), 0))
                vertexMin = vertexData.min(0)
                vertexMax = vertexData.max(0)
                for n in xrange(0, 3):
                    transformedMin[n] = min(transformedMin[n], vertexMin[n])
                    transformedMax[n] = max(transformedMax[n], vertexMax[n])
            center = (transformedMin + transformedMax) / 2.0
            for v in self._mesh.getVolumes():
                vertexData = v.vertexData[::,0:3]
                centeredData = vertexData - center
                sphere = math.sqrt(numpy.max(centeredData[:, 0] ** 2 + centeredData[:, 1] ** 2 + centeredData[:, 2] ** 2))
                boundarySphere = max(boundarySphere, sphere)
        elif self._vector is not None:
            matrix2d = numpy.matrix(self._matrix.getA()[0:2,0:2], numpy.float32)
            for p in self._vector.getPaths():
                v = p.getPoints()
                vertexData = (numpy.matrix(v, copy = False) * matrix2d).getA()
                hull = polygon.convexHull(numpy.concatenate((numpy.rint(vertexData).astype(int), hull), 0))
                vertexMin = vertexData.min(0)
                vertexMax = vertexData.max(0)
                for n in xrange(0, 2):
                    transformedMin[n] = min(transformedMin[n], vertexMin[n])
                    transformedMax[n] = max(transformedMax[n], vertexMax[n])
                transformedMin[2] = -1.0
                transformedMax[2] = -1.0
            center = (transformedMin[0:2] + transformedMax[0:2]) / 2.0
            for p in self._vector.getPaths():
                vertexData = p.getPoints()
                centeredData = vertexData - center
                sphere = math.sqrt(numpy.max(centeredData[:, 0] ** 2 + centeredData[:, 1] ** 2))
                boundarySphere = max(boundarySphere, sphere)

        self._vMin = transformedMin
        self._vMax = transformedMax
        self._boundarySphere = boundarySphere
        self._drawOffset = numpy.array([-center[0], -center[1], -transformedMin[2]])

        self._updated()

    def getSize(self):
        return self._vMax - self._vMin

    def getMesh(self):
        return self._mesh

    def getDrawOffset(self):
        return self._drawOffset

    def clearInfo(self):
        self._info = {}

    def setInfo(self, key, value):
        self._info[key] = value

    def getInfoString(self):
        ret = ''
        keys = self._info.keys()
        keys.sort()
        for k in keys:
            ret += '%s: %s\n' % (k, self._info[k])
        return ret

    def getContextMenu(self):
        options = []
        options += [(_("Delete"), self.onDelete)]
        return options

    def onDelete(self):
        self._scene.removeObject(self)
