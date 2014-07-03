import numpy
from OpenGL.GL import *

from Cura.gui import openGLUtils
from Cura.resources import getMesh
from Cura.gui.view3D.renderer import Renderer


class ToolpathRenderer(Renderer):
    def __init__(self):
        super(ToolpathRenderer,self).__init__()

    def render(self):
        colors = {
            'skirt': (0, 0.5, 0.5),
            'inset0': (0.5, 0, 0.5),
            'insetx': (0.5, 0.5, 0),
            'skin': (0.5, 0.5, 0),
            'support': (0.5, 0.5, 0),
        }
        glPushMatrix()
        if self.machine.getSettingValueByKey('machine_center_is_zero') == 'False':
            glTranslatef(-self.machine.getSettingValueByKeyFloat('machine_width') / 2.0, -self.machine.getSettingValueByKeyFloat('machine_depth') / 2.0, 0.0)
        glDisable(GL_LIGHTING)
        for obj in self.scene.getObjects():
            for layer_nr in xrange(0, obj.getToolpathLayerCount()):
                layer = obj.getToolpathLayer(layer_nr)
                if layer is None:
                    continue
                z = layer._z_height
                for key in layer._polygons.keys():
                    if key in colors:
                        glColor3fv(colors[key])
                    else:
                        print key
                    layer.getVertexRenderer(key).render()
        glPopMatrix()

    def focusRender(self):
        pass
