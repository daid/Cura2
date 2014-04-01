__author__ = 'Jaime van Kessel'

from Cura.gui.view3D.view3D import view3DWidget
from Cura.gui.view3D.machineRenderer import MachineRenderer
from Cura.gui.view3D.printableObjectRenderer import PrintableObjectRenderer
from Cura.gui.view3D.selectionRenderer import SelectionRenderer


class PrinterView3D(view3DWidget):
    def __init__(self):
        super(PrinterView3D, self).__init__()

        self.addRenderer(MachineRenderer())
        printable_object_renderer = PrintableObjectRenderer()
        self.addRenderer(printable_object_renderer,True)
        selection_renderer = SelectionRenderer()
        self.addRenderer(selection_renderer)
