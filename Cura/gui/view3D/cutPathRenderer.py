import numpy
from OpenGL.GL import *

from Cura.gui import openGLUtils
from Cura.resources import getMesh
from Cura.gui.view3D.renderer import Renderer


class CutPathRenderer(Renderer):
    def __init__(self):
        super(CutPathRenderer,self).__init__()

    def render(self):
        results = self.scene.getResult()
        if not hasattr(results, 'renderers'):
            objects = results.getCutPathPolygons()
            if objects is None:
                return
            renderers = []
            for polygons in objects:
                renderer_list = []
                for points in polygons:
                    points = numpy.concatenate((points, numpy.zeros((len(points), 1), numpy.float32)), 1)
                    renderer_list.append(openGLUtils.VertexRenderer(GL_TRIANGLE_FAN, points, False))
                renderers.append(renderer_list)
            results.renderers = renderers

        for renderers in results.renderers:
            glPushMatrix()
            x = -self.machine.getSettingValueByKeyFloat('machine_width') / 2
            y = -self.machine.getSettingValueByKeyFloat('machine_depth') / 2
            glTranslatef(x, y, 1)
            glClear(GL_STENCIL_BUFFER_BIT)
            glEnable(GL_STENCIL_TEST)
            glStencilFunc(GL_ALWAYS, 0xFF, 0xFF)
            glStencilOp(GL_KEEP, GL_KEEP, GL_INCR_WRAP)
            glColorMask(False, False, False, False)
            glDisable(GL_DEPTH_TEST)
            for renderer in renderers:
                renderer.render()
            glColorMask(True, True, True, True)
            glStencilFunc(GL_EQUAL, 0x01, 0x01)
            glColor4f(0.3, 1.0, 0.5, 0.5)
            for renderer in renderers:
                renderer.render()
            glDisable(GL_STENCIL_TEST)
            glEnable(GL_DEPTH_TEST)
            glPopMatrix()

    def focusRender(self):
        pass
