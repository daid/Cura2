import numpy

from OpenGL.GL import *
from ctypes import c_void_p

legacyMode = False


class VertexRenderer(object):
    def __init__(self, renderType, vertexData, hasNormals = True):
        self._renderType = renderType
        self._vertexData = vertexData
        self._hasNormals = hasNormals
        self._buffers = None

    def render(self):
        if legacyMode:
            glEnableClientState(GL_VERTEX_ARRAY)
            if self._hasNormals:
                glEnableClientState(GL_NORMAL_ARRAY)
                glVertexPointer(3, GL_FLOAT, 2 * 3 * 4, self._vertexData)
                glNormalPointer(GL_FLOAT, 2 * 3 * 4, self._vertexData.reshape(len(self._vertexData) * 6)[3:])
            else:
                glVertexPointer(3, GL_FLOAT, 3 * 4, self._vertexData)
            glDrawArrays(GL_TRIANGLES, 0, len(self._vertexData))
            glDisableClientState(GL_VERTEX_ARRAY)
            glDisableClientState(GL_NORMAL_ARRAY)
        else:
            if self._buffers is None:
                self._buffers = []
                maxBufferLen = 30000
                bufferCount = ((len(self._vertexData)-1) / maxBufferLen) + 1
                for n in xrange(0, bufferCount):
                    bufferInfo = {}
                    bufferInfo['buffer'] = glGenBuffers(1)
                    bufferInfo['len'] = maxBufferLen
                    offset = n * maxBufferLen
                    if n == bufferCount - 1:
                        bufferInfo['len'] = len(self._vertexData) % maxBufferLen
                    glBindBuffer(GL_ARRAY_BUFFER, bufferInfo['buffer'])
                    glBufferData(GL_ARRAY_BUFFER, self._vertexData[offset:offset+bufferInfo['len']], GL_STATIC_DRAW)
                    self._buffers.append(bufferInfo)
                glBindBuffer(GL_ARRAY_BUFFER, 0)

            for bufferInfo in self._buffers:
                glBindBuffer(GL_ARRAY_BUFFER, bufferInfo['buffer'])
                glEnableClientState(GL_VERTEX_ARRAY)
                if self._hasNormals:
                    glEnableClientState(GL_NORMAL_ARRAY)
                    glVertexPointer(3, GL_FLOAT, 2 * 3 * 4, c_void_p(0))
                    glNormalPointer(GL_FLOAT, 2 * 3 * 4, c_void_p(3 * 4))
                else:
                    glVertexPointer(3, GL_FLOAT, 3 * 4, c_void_p(0))
                glDrawArrays(self._renderType, 0, bufferInfo['len'])
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            glDisableClientState(GL_VERTEX_ARRAY)
            glDisableClientState(GL_NORMAL_ARRAY)


def unproject(winx, winy, winz, modelMatrix, projMatrix, viewport):
    """
    Projects window position to 3D space. (gluUnProject). Reimplentation as some drivers crash with the original.
    """
    npModelMatrix = numpy.matrix(numpy.array(modelMatrix, numpy.float64).reshape((4,4)))
    npProjMatrix = numpy.matrix(numpy.array(projMatrix, numpy.float64).reshape((4,4)))
    finalMatrix = npModelMatrix * npProjMatrix
    finalMatrix = numpy.linalg.inv(finalMatrix)

    viewport = map(float, viewport)
    vector = numpy.array([(winx - viewport[0]) / viewport[2] * 2.0 - 1.0, (winy - viewport[1]) / viewport[3] * 2.0 - 1.0, winz * 2.0 - 1.0, 1]).reshape((1,4))
    vector = (numpy.matrix(vector) * finalMatrix).getA().flatten()
    ret = list(vector)[0:3] / vector[3]
    return ret
