__author__ = 'Jaime van Kessel'
from Cura.gui.view3D.renderer import Renderer


class SelectionRenderer(Renderer):
    def __init__(self):
        super(SelectionRenderer,self).__init__()

    def render(self):
        super(SelectionRenderer,self).render()
        n = 0
        if self.scene is not None:
            for object in self.scene.getObjects():
                glColor4ub((n >> 16) & 0xFF, (n >> 8) & 0xFF, (n >> 0) & 0xFF, 0xFF)
                self._renderObject(object[0])
