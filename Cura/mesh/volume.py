import numpy


class MeshVolume(object):
    """
    A mesh is a list of 3D triangles build from vertexes.
    Each triangle has 3 vertexes and 3 normals.

    The metaData field is used to associate other data with this volume.
    """
    def __init__(self, mesh):
        self._mesh = mesh
        self.vertexData = None
        self.vertexCount = 0
        self.metaData = {}

    def _addFace(self, x0, y0, z0, x1, y1, z1, x2, y2, z2):
        n = self.vertexCount
        self.vertexData[n][0] = x0
        self.vertexData[n][1] = y0
        self.vertexData[n][2] = z0
        n += 1
        self.vertexData[n][0] = x1
        self.vertexData[n][1] = y1
        self.vertexData[n][2] = z1
        n += 1
        self.vertexData[n][0] = x2
        self.vertexData[n][1] = y2
        self.vertexData[n][2] = z2
        self.vertexCount += 3

    def _prepareFaceCount(self, faceNumber):
        #Set the amount of faces before loading data in them. This way we can create the numpy arrays before we fill them.
        self.vertexData = numpy.zeros((faceNumber*3, 6), numpy.float32)
        self.vertexCount = 0

    def calculateNormals(self):
        vertexData = self.vertexData.reshape(self.vertexCount / 3, 6, 3)
        normals = numpy.cross(vertexData[::, 2] - vertexData[::, 0], vertexData[::, 4] - vertexData[::, 0])
        lens = numpy.sqrt(normals[:, 0] ** 2 + normals[:, 1] ** 2 + normals[:, 2] ** 2)

        normals[:, 0] /= lens
        normals[:, 1] /= lens
        normals[:, 2] /= lens

        vertexData[::, 1] = normals
        vertexData[::, 3] = normals
        vertexData[::, 5] = normals

    def getMesh(self):
        return self._mesh