
import sys
import wx
from ConfigParser import ConfigParser

from Cura.preferences import getPreference
from Cura.preferences import setPreference
from Cura.resources import getDefaultPreferenceStoragePath
from Cura.resources import getResourcePath
from Cura.app import CuraApp
from Cura.gui.newFDMprinterWizard import NewDFMPrinterWizard
from Cura.scene.printer3DScene import Printer3DScene
from Cura.machine.settingsViewPreset import SettingsViewPreset
from Cura.machine.settingsViewPreset import loadSettingViewPresets
from Cura.machine.settingsViewPreset import saveSettingViewPresets
from Cura.machine.fdmprinter import FDMPrinter
from Cura.machine.translator.fdmPrinterTranslator import FDMPrinterTranslator
from Cura.gui.view3D.printerView3D import PrinterView3D
from Cura.gui.tools.rotateTool import RotateTool
from Cura.gui.tools.scaleTool import ScaleTool
from Cura.gui.tools.mirrorTool import MirrorTool
from Cura.gui.tools.selectAndMoveTool import SelectAndMoveTool


class CuraFDMApp(CuraApp):
    def __init__(self):
        super(CuraFDMApp, self).__init__()

    def OnInit(self):
        self._settings_view_presets = []
        self._active_setting_view = None

        self._scene = Printer3DScene()
        self._view = PrinterView3D()
        self._translator = FDMPrinterTranslator()

        machine_storage = ConfigParser()
        machine_storage.read(getDefaultPreferenceStoragePath('machines.ini'))
        n = 0
        while machine_storage.has_section('machine_%d' % n):
            machine = None
            if machine_storage.has_option('machine_%d' % n, 'machine_class'):
                try:
                    class_name = machine_storage.get('machine_%d' % n, 'machine_class')
                    module_name, class_name = class_name.rsplit('.', 1)
                    __import__(module_name)
                    module = sys.modules[module_name]
                    machine = getattr(module, class_name)()
                except:
                    import traceback
                    traceback.print_exc()
                    machine = None
            if machine is None:
                machine = FDMPrinter()
            machine.loadSettingsFromConfigParser(machine_storage, 'machine_%d' % n)
            self.addMachine(machine)
            n += 1

        if len(self._machine_list) < 1:
            wizard = NewDFMPrinterWizard()
            machine = wizard.run()
            if machine is not None:
                self.addMachine(machine)

        if len(self._machine_list) < 1:
            return False

        self._toolbox.append(RotateTool(self))
        self._toolbox.append(ScaleTool(self))
        self._toolbox.append(MirrorTool(self))
        self._toolbox.append(SelectAndMoveTool(self))

        svp = SettingsViewPreset()
        svp.setName('Normal')
        svp.importFromFile(getResourcePath('view_presets/normal_view.ini'))
        svp.setBuildIn()
        self.addSettingsViewPreset(svp)

        for svp in loadSettingViewPresets(getDefaultPreferenceStoragePath('view_presets.ini')):
            self.addSettingsViewPreset(svp)

        self.setActiveSettingsView(self._settings_view_presets[int(getPreference('active_view_preset', 0))])
        self.setMachine(self._machine_list[int(getPreference('active_machine', 0))])

        wx.CallAfter(self._scene.loadFile, 'C:/Models/D&D/Box.stl')

        return True

    def finished(self):
        setPreference('active_view_preset', self._settings_view_presets.index(self._active_setting_view))
        setPreference('active_machine', self._machine_list.index(self._machine))
        machine_storage = ConfigParser()
        for machine in self._machine_list:
            machine.saveSettingsToConfigParser(machine_storage, 'machine_%d' % (self._machine_list.index(machine)))
        with open(getDefaultPreferenceStoragePath('machines.ini'), "w") as f:
            machine_storage.write(f)
        saveSettingViewPresets(getDefaultPreferenceStoragePath('view_presets.ini'), self._settings_view_presets)

    def getSettingsViewPresets(self):
        return self._settings_view_presets

    def addSettingsViewPreset(self, svp):
        self._settings_view_presets.append(svp)

    def getActiveSettingsViewPreset(self):
        return self._active_setting_view

    def setMachine(self, machine):
        super(CuraFDMApp, self).setMachine(machine)
        if self._active_setting_view is not None:
            self._active_setting_view.applyPreset(self._machine)
        if self._main_window is not None:
            self._main_window.refreshProfilePanel()
        machine.setTranslator(self._translator)
        self._view.refresh()
        self._translator.trigger()

    def setActiveSettingsView(self, settings_view):
        self._active_setting_view = settings_view
        settings_view.applyPreset(self._machine)
        if self._main_window is not None:
            self._main_window.refreshProfilePanel()
        self._translator.trigger()

    def setViewMode(self, mode):
        self.getView().setViewMode(mode)
        self._main_window.setViewMode(mode)
