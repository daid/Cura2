__author__ = 'Jaime van Kessel'
from Cura.gui.view3D.renderer import Renderer

class PrintableObjectRenderer(Renderer):
    def __int__(self):
        super(PrintableObjectRenderer,self).__init__()

    def _update(self, instructions):
        for model in self.scene.getObjects():
            pass
