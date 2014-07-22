
import wx
import platform
import os
from ConfigParser import ConfigParser

from Cura.resources import getDefaultPreferenceStoragePath
from Cura.resources import getResourcePath
from Cura.gui.mainWindow import MainWindow
from Cura.scene.printer3DScene import Printer3DScene
from Cura.machine.settingsViewPreset import SettingsViewPreset
from Cura.machine.fdmprinter import FDMPrinter
from Cura.machine.translator.fdmPrinterTranslator import FDMPrinterTranslator
from Cura.gui.view3D.printerView3D import PrinterView3D
from Cura.gui.tools.rotateTool import RotateTool
from Cura.gui.tools.scaleTool import ScaleTool
from Cura.gui.tools.mirrorTool import MirrorTool
from Cura.gui.tools.selectAndMoveTool import SelectAndMoveTool


class CuraApp(wx.App):
    def __init__(self):
        self._toolbox = []

        self._scene = None
        self._view = None
        self._translator = None
        self._machine = None

        self._mainWindow = None

        if platform.system() == "Windows" and not 'PYCHARM_HOSTED' in os.environ:
            super(CuraApp, self).__init__(redirect=True, filename='output.txt')
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

        self._mainWindow = MainWindow(self)
        self._mainWindow.Show()
        self._mainWindow.Maximize()

    def finished(self):
        pass

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

    def showNotification(self, title, message, callback=None):
        self._mainWindow.showNotification(title, message, callback)


class CuraFDMApp(CuraApp):
    def __init__(self):
        super(CuraFDMApp, self).__init__()

    def OnInit(self):
        self._settings_view_presets = []

        self._scene = Printer3DScene()
        self._view = PrinterView3D()
        self._translator = FDMPrinterTranslator()
        self._machine = FDMPrinter()

        self._toolbox.append(RotateTool(self))
        self._toolbox.append(ScaleTool(self))
        self._toolbox.append(MirrorTool(self))
        self._toolbox.append(SelectAndMoveTool(self))

        self._machine.loadSettings(getDefaultPreferenceStoragePath('settings.ini'))

        svp = SettingsViewPreset()
        svp.setName('Normal')
        svp.importFromFile(getResourcePath('view_presets/normal_view.ini'))
        svp.setBuildIn()
        self.addSettingsViewPreset(svp)
        self.setActiveSettingsView(svp)

        cp = ConfigParser()
        cp.read(getDefaultPreferenceStoragePath('view_presets.ini'))
        n = 1
        while cp.has_section('ViewPreset_%d' % (n)):
            svp = SettingsViewPreset()
            svp.setName(cp.get('ViewPreset_%d' % (n), 'view_preset_name'))
            for key in cp.options('ViewPreset_%d' % (n)):
                svp.setSettingVisible(key, cp.get('ViewPreset_%d' % (n), key) == 'True')
            self.addSettingsViewPreset(svp)
            n += 1

        wx.CallAfter(self._scene.loadFile, 'C:/Models/D&D/Box.stl')

        return True

    def finished(self):
        self._machine.saveSettings(getDefaultPreferenceStoragePath('settings.ini'))
        cp = ConfigParser()
        n = 1
        for svp in self._settings_view_presets:
            if not svp.isBuildIn():
                svp.addToConfigParser(cp, 'ViewPreset_%d' % (n))
                cp.set('ViewPreset_%d' % (n), 'view_preset_name', svp.getName())
                n += 1
        with open(getDefaultPreferenceStoragePath('view_presets.ini'), "w") as f:
            cp.write(f)

    def getSettingsViewPresets(self):
        return self._settings_view_presets

    def addSettingsViewPreset(self, svp):
        self._settings_view_presets.append(svp)

    def getActiveSettingsViewPreset(self):
        return self._active_setting_view

    def setActiveSettingsView(self, settings_view):
        self._active_setting_view = settings_view
        settings_view.applyPreset(self._machine)
        if self._mainWindow is not None:
            self._mainWindow.refreshProfilePanel()

    def setViewMode(self, mode):
        self.getView().setViewMode(mode)
        self._mainWindow.setViewMode(mode)
