__author__ = 'Jaime van Kessel'

from Cura.gui.view3D.view3D import View3D
from Cura.gui.view3D.machineRenderer import MachineRenderer
from Cura.gui.view3D.printableObjectRenderer import PrintableObjectRenderer
from Cura.gui.view3D.selectionRenderer import SelectionRenderer


class PrinterView3D(View3D):
    def __init__(self):
        super(PrinterView3D, self).__init__()

        self._selection_renderer = SelectionRenderer()
        self.addRenderer(self._selection_renderer, True)
        printable_object_renderer = PrintableObjectRenderer()
        self.addRenderer(printable_object_renderer)

    def updateMousePos(self, x, y):
        self._selection_renderer.setMousePos(x, y)
