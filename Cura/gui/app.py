
import wx
import platform
import os

from Cura.resources import getDefaultPreferenceStoragePath
from Cura.gui.mainWindow import MainWindow
from Cura.scene.printer3DScene import Printer3DScene
from Cura.machine.fdmprinter import FDMPrinter
from Cura.machine.translator.fdmPrinterTranslator import FDMPrinterTranslator
from Cura.gui.view3D.printerView3D import PrinterView3D
from Cura.gui.tools.rotateTool import RotateTool
from Cura.gui.tools.scaleTool import ScaleTool
from Cura.gui.tools.mirrorTool import MirrorTool
from Cura.gui.tools.selectAndMoveTool import SelectAndMoveTool


class CuraApp(wx.App):
    # TODO: Should be subclassed to provide different applications, with different scenes/machines/views/translators
    def __init__(self):
        if platform.system() == "Windows" and not 'PYCHARM_HOSTED' in os.environ:
            super(CuraApp, self).__init__(redirect=True, filename='output.txt')
        else:
            super(CuraApp, self).__init__(redirect=False)

        self._toolbox = []

        self._machine = FDMPrinter()
        self._scene = Printer3DScene()
        self._view = PrinterView3D()
        self._translator = FDMPrinterTranslator(self._scene, self._machine)

        self._toolbox.append(RotateTool(self))
        self._toolbox.append(ScaleTool(self))
        self._toolbox.append(MirrorTool(self))
        self._toolbox.append(SelectAndMoveTool(self))

        self._view.setScene(self._scene)
        self._view.setMachine(self._machine)
        self._scene.setView(self._view)
        self._machine.setTranslator(self._translator)
        self._scene.setTranslator(self._translator)

        self._machine.loadSettings(getDefaultPreferenceStoragePath('settings.ini'))

        self._mainWindow = MainWindow(self)
        self._mainWindow.Show()
        self._mainWindow.Maximize()

        self._scene.loadFile('C:/Models/D&D/Box.stl')

    def finished(self):
        self._machine.saveSettings(getDefaultPreferenceStoragePath('settings.ini'))

    def getMachine(self):
        return self._machine

    def getScene(self):
        return self._scene

    def getView(self):
        return self._view

    def getTranslator(self):
        return self._translator

    def getMainWindow(self):
        return self._mainWindow

    def getTools(self):
        return self._toolbox
