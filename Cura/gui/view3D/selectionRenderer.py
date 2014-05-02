__author__ = 'Jaime van Kessel'

from OpenGL.GL import *

from Cura.gui import openGLUtils
from Cura.resources import getMesh
from Cura.gui.view3D.renderer import Renderer


class SelectionRenderer(Renderer):
    def __init__(self):
        super(SelectionRenderer,self).__init__()
        self._mousePos = None

    def setMousePos(self, x, y):
        self._mousePos = (x, y)

    def render(self):
        if self._mousePos is not None:
            oldClearColor = glGetFloatv(GL_COLOR_CLEAR_VALUE)
            glClearColor(1, 1, 1, 1)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glDisable(GL_LIGHTING)
            glDisable(GL_BLEND)
            objIdx = 0
            for obj in self.scene.getObjects():
                glPushMatrix()
                offset = obj.getDrawOffset()
                glTranslatef(offset[0], offset[1], offset[2])
                mesh = obj.getMesh()
                if mesh is not None:
                    volumeIdx = 0
                    for v in mesh.getVolumes():
                        if 'VertexRenderer' not in v.metaData:
                            v.metaData['VertexRenderer'] = openGLUtils.VertexRenderer(GL_TRIANGLES, v.vertexData)
                        glColor3ub(0, volumeIdx, objIdx)
                        v.metaData['VertexRenderer'].render()
                        volumeIdx += 1
                else:
                    volumeIdx = 0
                    mesh = getMesh('loading_mesh.stl')
                    for v in mesh.getVolumes():
                        if 'VertexRenderer' not in v.metaData:
                            v.metaData['VertexRenderer'] = openGLUtils.VertexRenderer(GL_TRIANGLES, v.vertexData)
                        glColor3ub(0, volumeIdx, objIdx)
                        v.metaData['VertexRenderer'].render()
                        volumeIdx += 1
                objIdx += 1
                glPopMatrix()

            n = glReadPixels(self._mousePos[0], self._mousePos[1], 1, 1, GL_RGBA, GL_UNSIGNED_INT_8_8_8_8)[0][0]
            f = glReadPixels(self._mousePos[0], self._mousePos[1], 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)[0][0]
            if (n >> 24) == 0 and (n & 0xFF) == 255:
                self._focusObject = self.scene.getObjects()[(n >> 8) & 0xFF]
                if self._focusObject.getMesh() is not None:
                    self._focusVolume = self._focusObject.getMesh().getVolumes()[(n >> 16) & 0xFF]
                else:
                    self._focusVolume = None
            else:
                self._focusObject = None
                self._focusVolume = None

            glClearColor(oldClearColor[0], oldClearColor[1], oldClearColor[2], oldClearColor[3])
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def getFocusObject(self):
        return self._focusObject

    def getFocusVolume(self):
        return self._focusVolume
