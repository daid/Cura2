__author__ = 'Jaime van Kessel'

from OpenGL.GL import *

from Cura.gui import openGLUtils
from Cura.resources import getMesh
from Cura.gui.view3D.renderer import Renderer


class PrintableObjectRenderer(Renderer):
    def __init__(self):
        super(PrintableObjectRenderer,self).__init__()
        self._shader = openGLUtils.GLShader(filename='objectShader.glsl')

    def render(self):
        self._shader.bind()
        for obj in self.scene.getObjects():
            mesh = obj.getMesh()
            glPushMatrix()
            offset = obj.getDrawOffset()
            glTranslatef(obj.getPosition()[0], obj.getPosition()[1], obj.getSize()[2] / 2.0)
            openGLUtils.glMultiplyMatrix(obj.getTempMatrix())
            openGLUtils.glMultiplyMatrix(obj.getMatrix())
            glTranslatef(offset[0], offset[1], offset[2] - obj.getSize()[2] / 2.0)
            colorStrength = 0.8
            if obj.isSelected():
                colorStrength = 1.0
            if mesh is not None:
                for v in mesh.getVolumes():
                    if 'VertexRenderer' not in v.metaData:
                        v.metaData['VertexRenderer'] = openGLUtils.VertexRenderer(GL_TRIANGLES, v.vertexData)
                    glColor3f(1 * colorStrength, 0.5 * colorStrength, 1 * colorStrength)
                    v.metaData['VertexRenderer'].render()
            else:
                mesh = getMesh('loading_mesh.stl')
                for v in mesh.getVolumes():
                    if 'VertexRenderer' not in v.metaData:
                        v.metaData['VertexRenderer'] = openGLUtils.VertexRenderer(GL_TRIANGLES, v.vertexData)
                    glColor3f(0.5 * colorStrength, 0.5 * colorStrength, 0.5 * colorStrength)
                    v.metaData['VertexRenderer'].render()
            glPopMatrix()
        self._shader.unbind()

    def focusRender(self):
        objIdx = 0
        for obj in self.scene.getObjects():
            glPushMatrix()
            offset = obj.getDrawOffset()
            glTranslatef(obj.getPosition()[0], obj.getPosition()[1], 0)
            glTranslatef(offset[0], offset[1], offset[2])
            self.setCurrentFocusRenderObject(obj)

            mesh = obj.getMesh()
            if mesh is not None:
                volumeIdx = 0
                for v in mesh.getVolumes():
                    if 'VertexRenderer' not in v.metaData:
                        v.metaData['VertexRenderer'] = openGLUtils.VertexRenderer(GL_TRIANGLES, v.vertexData)
                    v.metaData['VertexRenderer'].render()
                    volumeIdx += 1
            else:
                volumeIdx = 0
                mesh = getMesh('loading_mesh.stl')
                for v in mesh.getVolumes():
                    if 'VertexRenderer' not in v.metaData:
                        v.metaData['VertexRenderer'] = openGLUtils.VertexRenderer(GL_TRIANGLES, v.vertexData)
                    v.metaData['VertexRenderer'].render()
                    volumeIdx += 1
            objIdx += 1
            glPopMatrix()
