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
        glDepthMask(False)
        for obj in self.scene.getObjects():
            glColor4f(0, 0, 0, 0.2)
            glBegin(GL_TRIANGLE_FAN)
            for p in obj.getObjectBoundary():
                glVertex3f(p[0], p[1], 0.1)
            glEnd()
            if self.scene.getOneAtATimeActive():
                glBegin(GL_TRIANGLE_FAN)
                for p in obj.getHeadHitShapeMin():
                    glVertex3f(p[0], p[1], 0.1)
                glEnd()
        glDepthMask(True)

        self._shader.bind()
        for obj in self.scene.getObjects():
            mesh = obj.getMesh()
            glPushMatrix()
            offset = obj.getDrawOffset()
            glTranslatef(obj.getPosition()[0], obj.getPosition()[1], obj.getSize()[2] / 2.0)

            openGLUtils.glMultiplyMatrix(obj.getTempMatrix())
            glTranslatef(offset[0], offset[1], offset[2] - obj.getSize()[2] / 2.0)
            openGLUtils.glMultiplyMatrix(obj.getMatrix())
            if mesh is not None:
                for v in mesh.getVolumes():
                    color = [1.0, 0.4, 0.6]
                    extruder = mesh.getMetaData('setting_extruder_nr', 0)
                    extruder = int(v.getMetaData('setting_extruder_nr', extruder))
                    if extruder == 1:
                        color = [1.0, 0.1, 0.6]
                    elif extruder == 2:
                        color = [1.0, 0.6, 0.1]
                    elif extruder == 2:
                        color = [0.6, 1.0, 0.1]
                    if not self.scene.checkPlatform(obj):
                        color = map(lambda n: 0.3 + n * 0.3, color)
                    if not obj.isSelected():
                        color = map(lambda n: n * 0.8, color)
                    if 'VertexRenderer' not in v.metaData:
                        v.metaData['VertexRenderer'] = openGLUtils.VertexRenderer(GL_TRIANGLES, v.vertexData)
                    glColor3f(color[0], color[1], color[2])
                    v.metaData['VertexRenderer'].render()
            else:
                mesh = getMesh('loading_mesh.stl')
                if mesh is not None:
                    for v in mesh.getVolumes():
                        if 'VertexRenderer' not in v.metaData:
                            v.metaData['VertexRenderer'] = openGLUtils.VertexRenderer(GL_TRIANGLES, v.vertexData)
                        glColor3f(0.5, 0.5, 0.5)
                        v.metaData['VertexRenderer'].render()
            glPopMatrix()
        self._shader.unbind()

    def focusRender(self):
        for obj in self.scene.getObjects():
            glPushMatrix()
            offset = obj.getDrawOffset()
            glTranslatef(obj.getPosition()[0], obj.getPosition()[1], obj.getSize()[2] / 2.0)
            openGLUtils.glMultiplyMatrix(obj.getTempMatrix())
            glTranslatef(offset[0], offset[1], offset[2] - obj.getSize()[2] / 2.0)
            openGLUtils.glMultiplyMatrix(obj.getMatrix())

            mesh = obj.getMesh()
            if mesh is not None:
                for v in mesh.getVolumes():
                    self.setCurrentFocusRenderObject(obj, v)
                    if 'VertexRenderer' not in v.metaData:
                        v.metaData['VertexRenderer'] = openGLUtils.VertexRenderer(GL_TRIANGLES, v.vertexData)
                    v.metaData['VertexRenderer'].render()
            else:
                self.setCurrentFocusRenderObject(obj)
                mesh = getMesh('loading_mesh.stl')
                if mesh is not None:
                    for v in mesh.getVolumes():
                        if 'VertexRenderer' not in v.metaData:
                            v.metaData['VertexRenderer'] = openGLUtils.VertexRenderer(GL_TRIANGLES, v.vertexData)
                        v.metaData['VertexRenderer'].render()
            glPopMatrix()
