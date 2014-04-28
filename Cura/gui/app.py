import sys

import wx
import platform
import os

from Cura.gui.mainWindow import MainWindow
from Cura.gui.view3D.renderer import Renderer
from Cura.scene.printer3DScene import Printer3DScene
from Cura.machine.fdmprinter import FDMPrinter
from Cura.gui.view3D.printerView3D import PrinterView3D


class CuraApp(wx.App):
    def __init__(self):
        if platform.system() == "Windows" and not 'PYCHARM_HOSTED' in os.environ:
            super(CuraApp, self).__init__(redirect=True, filename='output.txt')
        else:
            super(CuraApp, self).__init__(redirect=False)

        self._machine = FDMPrinter()
        self._scene = Printer3DScene()
        self._view = PrinterView3D()

        self._view.setScene(self._scene)
        self._view.setMachine(self._machine)

        self._mainWindow = MainWindow(self)
        self._mainWindow.Show()
        self._mainWindow.Maximize()

    def getMachine(self):
        return self._machine

    def getScene(self):
        return self._scene

    def getView(self):
        return self._view

    def getMainWindow(self):
        return self._mainWindow
