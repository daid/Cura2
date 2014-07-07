import numpy
from OpenGL.GL import *

from Cura.gui import openGLUtils
from Cura.gui.view3D.renderer import Renderer


class ToolpathLayerRenderer(object):
    COLORS = {
        'skirt': (0, 0.5, 0.5),
        'inset0': (0.5, 0, 0.5),
        'insetx': (0.5, 0.5, 0),
        'skin': (0.5, 0.5, 0),
        'support': (0.5, 0.5, 0),
    }

    def __init__(self, layer):
        self._renderer = {}
        self._layer = layer

    def render(self):
        for type in self._layer.getPathTypes():
            if not type in self._renderer:
                polygons = self._layer.getPolygons(type)
                point_count = 0
                indices_count = 0
                for poly in polygons:
                    point_count += len(poly)
                    indices_count += len(poly) * 4
                points = numpy.zeros((point_count, 2), numpy.float32)
                indices = numpy.zeros(indices_count, dtype=numpy.int32)
                point_index = 0
                indices_index = 0
                for poly in polygons:
                    n = len(poly)
                    points[point_index:point_index + n] = poly
                    i1 = numpy.arange(n, dtype=numpy.int32).reshape((n, 1)) + point_index
                    i2 = i1 + point_count
                    indices[indices_index:indices_index + (n * 4)] = numpy.concatenate((i1, i1 + 1, i2 + 1, i2), 1).reshape((n * 4))
                    indices[indices_index + (n * 4) - 3] = i1[0]
                    indices[indices_index + (n * 4) - 2] = i2[0]

                    point_index += n
                    indices_index += n * 4
                z_pos1 = numpy.zeros((point_count, 1), numpy.float32)
                z_pos2 = numpy.zeros((point_count, 1), numpy.float32)
                z_pos1.fill(self._layer._z_height)
                z_pos2.fill(self._layer._z_height - self._layer._layer_height)
                points1 = numpy.concatenate((points, z_pos1), 1)
                points2 = numpy.concatenate((points, z_pos2), 1)
                self._renderer[type] = openGLUtils.VertexRenderer(GL_QUADS, numpy.concatenate((points1, points2)), False, indices)
            glColor3fv(self.COLORS[type])
            self._renderer[type].render()


class ToolpathRenderer(Renderer):
    def __init__(self):
        super(ToolpathRenderer,self).__init__()

    def render(self):
        glPushMatrix()
        if self.machine.getSettingValueByKey('machine_center_is_zero') == 'False':
            glTranslatef(-self.machine.getSettingValueByKeyFloat('machine_width') / 2.0, -self.machine.getSettingValueByKeyFloat('machine_depth') / 2.0, 0.0)
        glDisable(GL_CULL_FACE)
        glDisable(GL_LIGHTING)
        for obj in self.scene.getObjects():
            for layer_nr in xrange(0, obj.getToolpathLayerCount()):
                layer = obj.getToolpathLayer(layer_nr)
                if layer is None:
                    continue
                if not hasattr(layer, 'renderer'):
                    layer.renderer = ToolpathLayerRenderer(layer)
                layer.renderer.render()
        glPopMatrix()

    def focusRender(self):
        pass
