
from Cura.gui.view3D.view3D import View3D
from Cura.gui.view3D.cuttableObjectRenderer import CuttableObjectRenderer
from Cura.gui.view3D.cutPathRenderer import CutPathRenderer


class CutView3D(View3D):
    def __init__(self):
        super(CutView3D, self).__init__()

        self.addRenderer(CutPathRenderer())
        self.addRenderer(CuttableObjectRenderer())
