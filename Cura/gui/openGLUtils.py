import numpy
import os

from OpenGL.GL import *
from OpenGL.GL import shaders
from ctypes import c_void_p
from Cura.resources import getResourcePath

legacyMode = False


class GLShader(object):
    def __init__(self, vertexProgram=None, fragmentProgram=None, filename=None):
        super(GLShader, self).__init__()
        if filename is not None:
            vertexProgram = ''
            fragmentProgram = ''
            type = 'BOTH'
            for line in open(os.path.join(getResourcePath('shaders'), filename), "r"):
                if line.startswith('--'):
                    type = line[2:].strip()
                if type == 'BOTH':
                    vertexProgram += line
                    fragmentProgram += line
                elif type == 'VERTEX':
                    vertexProgram += line
                elif type == 'FRAGMENT':
                    fragmentProgram += line
        self._vertexString = vertexProgram
        self._fragmentString = fragmentProgram

    def bind(self):
        if self._program is None and self._vertexString is not None:
            try:
                vertexShader = shaders.compileShader(self._vertexString, GL_VERTEX_SHADER)
                fragmentShader = shaders.compileShader(self._fragmentString, GL_FRAGMENT_SHADER)
                self._vertexString = None

                #shader.compileProgram tries to return the shader program as a overloaded int. But the return value of a shader does not always fit in a int (needs to be a long). So we do raw OpenGL calls.
                # This is to ensure that this works on intel GPU's
                # self._program = shaders.compileProgram(self._vertexProgram, self._fragmentProgram)
                self._program = glCreateProgram()
                glAttachShader(self._program, vertexShader)
                glAttachShader(self._program, fragmentShader)
                glLinkProgram(self._program)
                # Validation has to occur *after* linking
                glValidateProgram(self._program)
                if glGetProgramiv(self._program, GL_VALIDATE_STATUS) == GL_FALSE:
                    raise RuntimeError("Validation failure: %s"%(glGetProgramInfoLog(self._program)))
                if glGetProgramiv(self._program, GL_LINK_STATUS) == GL_FALSE:
                    raise RuntimeError("Link failure: %s" % (glGetProgramInfoLog(self._program)))
                glDeleteShader(vertexShader)
                glDeleteShader(fragmentShader)
            except RuntimeError, e:
                print str(e)
                self._program = None
        if self._program is not None:
            shaders.glUseProgram(self._program)

    def unbind(self):
        shaders.glUseProgram(0)

    def release(self):
        if self._program is not None:
            glDeleteProgram(self._program)
            self._program = None

    def setUniform(self, name, value):
        if self._program is not None:
            if type(value) is float:
                glUniform1f(glGetUniformLocation(self._program, name), value)
            elif type(value) is numpy.matrix:
                glUniformMatrix3fv(glGetUniformLocation(self._program, name), 1, False, value.getA().astype(numpy.float32))
            else:
                print 'Unknown type for setUniform: %s' % (str(type(value)))

    def isValid(self):
        return self._program is not None

    def getVertexShader(self):
        return self._vertexString

    def getFragmentShader(self):
        return self._fragmentString


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

    def release(self):
        if not legacyMode and self._buffers is not None:
            for info in self._buffers:
                glDeleteBuffers(1, [info['buffer']])
            self._buffers = None

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
