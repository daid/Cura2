import numpy
from OpenGL.GL import *

from Cura.gui import openGLUtils
from Cura.resources import getMesh
from Cura.gui.view3D.renderer import Renderer


class ToolpathRenderer(Renderer):
    def __init__(self):
        super(ToolpathRenderer,self).__init__()

    def render(self):
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
                    for path in layer._polygons[key]:
                        points = path
                        glBegin(GL_LINE_LOOP)
                        for p in points:
                            glVertex3f(p[0], p[1], z)
                        glEnd()
        glPopMatrix()

    def focusRender(self):
        pass
