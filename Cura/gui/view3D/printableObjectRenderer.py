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
        self._shader.unbind()
