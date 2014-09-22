
import wx
import platform
import os

from Cura.resources import getDefaultPreferenceStoragePath
from Cura.gui.mainWindow import MainWindow


class CuraApp(wx.App):
    def __init__(self):
        self._toolbox = []

        self._scene = None
        self._view = None
        self._translator = None
        self._machine = None
        self._machine_list = []

        self._main_window = None

        if platform.system() == "Windows" and not 'PYCHARM_HOSTED' in os.environ:
            super(CuraApp, self).__init__(redirect=True, filename=getDefaultPreferenceStoragePath('output.log'))
        else:
            super(CuraApp, self).__init__(redirect=False)

        self._view.setScene(self._scene)
        self._view.setMachine(self._machine)
        self._scene.setView(self._view)
        self._machine.setTranslator(self._translator)
        self._scene.setTranslator(self._translator)
        self._scene.setMachine(self._machine)
        self._translator.setScene(self._scene)
        self._translator.setMachine(self._machine)

        self._main_window = MainWindow(self)
        self._main_window.Show()
        self._main_window.Maximize()

    def finished(self):
        pass

    def addMachine(self, machine):
        self._machine_list.append(machine)
        if self._machine is None:
            self.setMachine(machine)

    def setMachine(self, machine):
        self._machine = machine
        self._view.setMachine(self._machine)
        self._scene.setMachine(self._machine)
        self._translator.setMachine(self._machine)

    def getMachine(self):
        return self._machine

    def getMachineList(self):
        return self._machine_list

    def getScene(self):
        return self._scene

    def getView(self):
        return self._view

    def getTranslator(self):
        return self._translator

    def getMainWindow(self):
        return self._main_window

    def getTools(self):
        return self._toolbox

    def showNotification(self, title, message, callback=None):
        self._main_window.showNotification(title, message, callback)
