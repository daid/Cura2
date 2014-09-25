import numpy
from OpenGL.GL import *

from Cura.gui import openGLUtils
from Cura.resources import getMesh
from Cura.gui.view3D.renderer import Renderer


class CuttableObjectRenderer(Renderer):
    def __init__(self):
        super(CuttableObjectRenderer,self).__init__()
        self._shader = openGLUtils.GLShader(filename='objectShader.glsl')

    def render(self):
        for obj in self.scene.getObjects():
            mesh = obj.getMesh()
            vector = obj.getVector()
            glPushMatrix()
            offset = obj.getDrawOffset()
            glTranslatef(obj.getPosition()[0], obj.getPosition()[1], obj.getSize()[2] / 2.0)

            openGLUtils.glMultiplyMatrix(obj.getTempMatrix())
            glTranslatef(offset[0], offset[1], offset[2] - obj.getSize()[2] / 2.0)
            openGLUtils.glMultiplyMatrix(obj.getMatrix())
            if mesh is not None:
                self._shader.bind()
                for v in mesh.getVolumes():
                    color = [1.0, 0.4, 0.6]
                    if not obj.isSelected():
                        color = map(lambda n: n * 0.8, color)
                    if 'VertexRenderer' not in v.metaData:
                        v.metaData['VertexRenderer'] = openGLUtils.VertexRenderer(GL_TRIANGLES, v.vertexData)
                    glColor3f(color[0], color[1], color[2])
                    v.metaData['VertexRenderer'].render()
                self._shader.unbind()
            elif vector is not None:
                for p in vector.getPaths():
                    if 'VertexRenderer' not in p.metaData:
                        points = p.getPoints()
                        points = numpy.concatenate((points, numpy.zeros((len(points), 1), numpy.float32)), 1)
                        if p.isClosed():
                            p.metaData['VertexRendererClosed'] = openGLUtils.VertexRenderer(GL_TRIANGLE_FAN, points, False)
                        p.metaData['VertexRenderer'] = openGLUtils.VertexRenderer(GL_LINE_STRIP, points, False)
                glClear(GL_STENCIL_BUFFER_BIT)
                glEnable(GL_STENCIL_TEST)
                glStencilFunc(GL_ALWAYS, 0xFF, 0xFF)
                glStencilOp(GL_KEEP, GL_KEEP, GL_INCR_WRAP)
                glColorMask(False, False, False, False)
                glDisable(GL_DEPTH_TEST)
                for p in vector.getPaths():
                    if p.isClosed():
                        p.metaData['VertexRendererClosed'].render()
                glColorMask(True, True, True, True)
                glStencilFunc(GL_EQUAL, 0x01, 0x01)
                glColor4f(1, 0.5, 0.3, 0.8)
                for p in vector.getPaths():
                    if p.isClosed():
                        p.metaData['VertexRendererClosed'].render()
                glDisable(GL_STENCIL_TEST)
                glColor3f(0, 0, 0)
                glLineWidth(3.0)
                for p in vector.getPaths():
                    p.metaData['VertexRenderer'].render()
                glEnable(GL_DEPTH_TEST)
            else:
                self._shader.bind()
                mesh = getMesh('loading_mesh.stl')
                if mesh is not None:
                    for v in mesh.getVolumes():
                        if 'VertexRenderer' not in v.metaData:
                            v.metaData['VertexRenderer'] = openGLUtils.VertexRenderer(GL_TRIANGLES, v.vertexData)
                        glColor3f(0.5, 0.5, 0.5)
                        v.metaData['VertexRenderer'].render()
                self._shader.unbind()
            glPopMatrix()

    def focusRender(self):
        for obj in self.scene.getObjects():
            glPushMatrix()
            offset = obj.getDrawOffset()
            glTranslatef(obj.getPosition()[0], obj.getPosition()[1], obj.getSize()[2] / 2.0)
            openGLUtils.glMultiplyMatrix(obj.getTempMatrix())
            glTranslatef(offset[0], offset[1], offset[2] - obj.getSize()[2] / 2.0)
            openGLUtils.glMultiplyMatrix(obj.getMatrix())

            mesh = obj.getMesh()
            vector = obj.getVector()
            if mesh is not None:
                for v in mesh.getVolumes():
                    self.setCurrentFocusRenderObject(obj, v)
                    if 'VertexRenderer' not in v.metaData:
                        v.metaData['VertexRenderer'] = openGLUtils.VertexRenderer(GL_TRIANGLES, v.vertexData)
                    v.metaData['VertexRenderer'].render()
            elif vector is not None:
                glClear(GL_STENCIL_BUFFER_BIT)
                glEnable(GL_STENCIL_TEST)
                glStencilFunc(GL_ALWAYS, 0xFF, 0xFF)
                glStencilOp(GL_KEEP, GL_KEEP, GL_INCR_WRAP)
                glColorMask(False, False, False, False)
                glDisable(GL_DEPTH_TEST)
                self.setCurrentFocusRenderObject(obj)
                for p in vector.getPaths():
                    if p.isClosed():
                        if 'VertexRendererClosed' in p.metaData:
                            p.metaData['VertexRendererClosed'].render()
                glColorMask(True, True, True, True)
                glStencilFunc(GL_EQUAL, 0x01, 0x01)
                glEnable(GL_DEPTH_TEST)
                for p in vector.getPaths():
                    if p.isClosed():
                        if 'VertexRendererClosed' in p.metaData:
                            p.metaData['VertexRendererClosed'].render()
                glDisable(GL_STENCIL_TEST)
                glLineWidth(10.0)
                for p in vector.getPaths():
                    self.setCurrentFocusRenderObject(obj, p)
                    if 'VertexRenderer' in p.metaData:
                        p.metaData['VertexRenderer'].render()
            else:
                mesh = getMesh('loading_mesh.stl')
                if mesh is not None:
                    self.setCurrentFocusRenderObject(obj)
                    for v in mesh.getVolumes():
                        if 'VertexRenderer' not in v.metaData:
                            v.metaData['VertexRenderer'] = openGLUtils.VertexRenderer(GL_TRIANGLES, v.vertexData)
                        v.metaData['VertexRenderer'].render()
            glPopMatrix()
