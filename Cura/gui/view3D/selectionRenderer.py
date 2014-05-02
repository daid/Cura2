__author__ = 'Jaime van Kessel'

from OpenGL.GL import *

from Cura.gui import openGLUtils
from Cura.resources import getMesh
from Cura.gui.view3D.renderer import Renderer


class SelectionRenderer(Renderer):
    def __init__(self):
        super(SelectionRenderer,self).__init__()

    def render(self):
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
