import os
import math
import threading
from OpenGL.GL import *
from OpenGL.GLU import *

from Cura.geometry import polygon
from Cura.gui.openGLUtils import VertexRenderer
from Cura.meshLoaders.meshLoader import loadMeshes
from Cura.scene.displayableObject import DisplayableObject

import numpy
numpy.seterr(all='ignore')


class ToolpathLayer(object):
    def __init__(self, z_height, layer_height):
        self._z_height = z_height
        self._layer_height = layer_height
        self._polygons = {}

    def add(self, type, polygons):
        if type not in self._polygons:
            self._polygons[type] = []
        self._polygons[type] += polygons

    def getPathTypes(self):
        return self._polygons.keys()

    def getPolygons(self, type):
        if type in self._polygons:
            return self._polygons[type]
        return None


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
        self._info = {}
        self._toolpath_layers = []

        # Mesh information.
        self._vMin = numpy.array([-1, -1, -1], numpy.float32)
        self._vMax = numpy.array([1, 1, 1], numpy.float32)
        self._boundarySphere = 1
        self._drawOffset = numpy.zeros((3,), numpy.float32)

        self._convex2dBoundary = numpy.zeros((2, 1), numpy.float32)
        self._head_hit_shape = numpy.zeros((2, 1), numpy.float32)
        self._head_hit_shape_min = numpy.zeros((2, 1), numpy.float32)

    def loadMesh(self, filename):
        self._thread = threading.Thread(target=self._loadMeshThread, args=(filename,))
        self._thread.daemon = True
        self._thread.start()

    def _loadMeshThread(self, filename):
        self._mesh = None
        mesh = loadMeshes(filename)[0]
        self._mesh = mesh
        self._updated()
        self._updateMeshInfo()

    def setMatrix(self, matrix):
        super(PrintableObject, self).setMatrix(matrix)
        self._thread = threading.Thread(target=self._updateMeshInfo)
        self._thread.daemon = True
        self._thread.start()

    def _updateMeshInfo(self):
        transformedMin = numpy.array([999999999999,999999999999,999999999999], numpy.float64)
        transformedMax = numpy.array([-999999999999,-999999999999,-999999999999], numpy.float64)
        boundarySphere = 0.0
        hull = numpy.zeros((0, 2), numpy.int)
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

        self._vMin = transformedMin
        self._vMax = transformedMax
        size = transformedMax - transformedMin
        self._boundarySphere = boundarySphere
        self._drawOffset = numpy.array([-center[0], -center[1], -transformedMin[2]])
        self._convex2dBoundary = polygon.minkowskiHull((hull.astype(numpy.float32) + self._drawOffset[0:2]), numpy.array([[-1,-1],[-1,1],[1,1],[1,-1]],numpy.float32))

        head_shape = self._scene.getMachine().getHeadShape()
        head_min_x, head_min_y = self._scene.getMachine().getHeadSizeMin()
        self._head_hit_shape = polygon.minkowskiHull(self._convex2dBoundary, head_shape)
        square_x = head_min_x + size[0] / 2.0 + 1
        square_y = head_min_y + size[1] / 2.0 + 1
        square = numpy.array([[square_x, square_y], [square_x, -square_y], [-square_x, -square_y], [-square_x, square_y]])
        self._head_hit_shape_min = polygon.clipConvex(self._head_hit_shape, square)
        self._updated()

    def getSize(self):
        return self._vMax - self._vMin

    def getMesh(self):
        return self._mesh

    def getDrawOffset(self):
        return self._drawOffset

    def getObjectBoundary(self):
        """
        Return a 2D convex polygon which is a convex hull around the 2D X/Y projection of the object.
        """
        return self._convex2dBoundary + self._position

    def getHeadHitShape(self):
        """
        Return a 2D convex polygon which is a convex hull around the 2D X/Y projection of the object, increased by the size of the printer head.
        This are will be hit by the head while this object is printed.
        """
        return self._head_hit_shape + self._position

    def getHeadHitShapeMin(self):
        """
        Return a 2D convex polygon which is a convex hull around the 2D X/Y projection of the object, increased by the size of the printer head. But cut off by the minimal head size.
        This is the area that needs to be kept free if you want to print objects one-at-a-time
        """
        return self._head_hit_shape_min + self._position

    def clearInfo(self):
        self._info = {}
        self._toolpath_layers = []

    def setInfo(self, key, value):
        self._info[key] = value

    def getInfoString(self):
        ret = ''
        for k, v in self._info.items():
            ret += '%s: %s\n' % (k, v)
        return ret

    def addToolpathLayer(self, layer_nr, z_height, layer_height):
        while len(self._toolpath_layers) <= layer_nr:
            self._toolpath_layers.append(None)
        self._toolpath_layers[layer_nr] = ToolpathLayer(z_height, layer_height)

    def addToolpathPolygons(self, name, layer_nr, polygons):
        if layer_nr >= len(self._toolpath_layers):
            return
        self._toolpath_layers[layer_nr].add(name, polygons)

    def getToolpathLayerCount(self):
        return len(self._toolpath_layers)

    def getToolpathLayer(self, layer_nr):
        if layer_nr < len(self._toolpath_layers):
            return self._toolpath_layers[layer_nr]
        return None