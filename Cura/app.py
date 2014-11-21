
import wx
import platform
import os

from Cura.resources import getDefaultPreferenceStoragePath
from Cura.gui.mainWindow import MainWindow

##  Application object
#   Creates the main window and other important objects.
class CuraApp(wx.App):
    def __init__(self):
        self._toolbox = []

        self._scene = None
        self._view = None
        self._translator = None
        self._machine = None
        self._machine_list = []

        self._main_window = None

        # Do not redirect stdout if running in an IDE.
        if platform.system() == "Windows" and not 'PYCHARM_HOSTED' in os.environ:
            super(CuraApp, self).__init__(redirect=True, filename=getDefaultPreferenceStoragePath('output.log'))
        else:
            super(CuraApp, self).__init__(redirect=False)

        # Why? All of these are None or empty
        self._view.setScene(self._scene)
        self._view.setMachine(self._machine)
        self._scene.setView(self._view)
        self._machine.setTranslator(self._translator)
        self._scene.setTranslator(self._translator)
        self._scene.setMachine(self._machine)
        self._translator.setScene(self._scene)
        self._translator.setMachine(self._machine)

        # Create and show main window
        self._main_window = MainWindow(self)
        self._main_window.Show()
        self._main_window.Maximize()

    ## Called after the main loop exits so things can be cleaned up.
    def finished(self):
        pass

    ## Add a machine configuration
    def addMachine(self, machine):
        self._machine_list.append(machine)
        if self._machine is None:
            self.setMachine(machine)

    ## Set an active machine configuration
    def setMachine(self, machine):
        self._machine = machine
        self._view.setMachine(self._machine)
        self._scene.setMachine(self._machine)
        self._translator.setMachine(self._machine)

    ## Return the active machine configuration
    def getMachine(self):
        return self._machine

    ## Return a list of all machine configuration objects.
    def getMachineList(self):
        return self._machine_list

    ## Return the current scene.
    def getScene(self):
        return self._scene

    ## Return the current view.
    def getView(self):
        return self._view

    ## Return the current translator object.
    def getTranslator(self):
        return self._translator

    ## Return the MainWindow object.
    def getMainWindow(self):
        return self._main_window

    ## Get the list of tools
    def getTools(self):
        return self._toolbox

    ## Display a notication message.
    def showNotification(self, title, message, callback=None):
        self._main_window.showNotification(title, message, callback)
