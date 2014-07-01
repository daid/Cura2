__author__ = 'Jaime van Kessel'

from Cura.gui.view3D.view3D import View3D
from Cura.gui.view3D.printableObjectRenderer import PrintableObjectRenderer
from Cura.gui.view3D.toolpathRenderer import ToolpathRenderer


class PrinterView3D(View3D):
    def __init__(self):
        super(PrinterView3D, self).__init__()

        self._printable_object_renderer = PrintableObjectRenderer()
        self._toolpath_renderer = ToolpathRenderer()
        self._toolpath_renderer.active = False
        self.addRenderer(self._printable_object_renderer)
        self.addRenderer(self._toolpath_renderer)

    def setViewMode(self, mode):
        self._printable_object_renderer.active = (mode == 'Normal')
        self._toolpath_renderer.active = (mode == 'Toolpaths')
        self.refresh()
