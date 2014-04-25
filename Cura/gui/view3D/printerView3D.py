__author__ = 'Jaime van Kessel'

from Cura.gui.view3D.view3D import View3D
from Cura.gui.view3D.machineRenderer import MachineRenderer
from Cura.gui.view3D.printableObjectRenderer import PrintableObjectRenderer
from Cura.gui.view3D.selectionRenderer import SelectionRenderer


class PrinterView3D(View3D):
    def __init__(self):
        super(PrinterView3D, self).__init__()

        self.addRenderer(MachineRenderer())
        printable_object_renderer = PrintableObjectRenderer()
        self.addRenderer(printable_object_renderer, True)
        selection_renderer = SelectionRenderer()
        self.addRenderer(selection_renderer)
