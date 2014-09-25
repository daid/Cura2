
import sys
from ConfigParser import ConfigParser

from Cura.preferences import getPreference
from Cura.preferences import setPreference
from Cura.resources import getDefaultPreferenceStoragePath
from Cura.app import CuraApp
from Cura.scene.cutScene import CutScene
from Cura.machine.translator.cutTranslator import CutTranslator
from Cura.gui.view3D.cutView3D import CutView3D
from Cura.gui.tools.rotateTool import RotateTool
from Cura.gui.tools.mirrorTool import MirrorTool
from Cura.gui.tools.selectAndMoveTool import SelectAndMoveTool


class CuraCutApp(CuraApp):
    def __init__(self):
        super(CuraCutApp, self).__init__()

    def OnInit(self):
        self._scene = CutScene()
        self._view = CutView3D()
        self._translator = CutTranslator()

        machine_storage = ConfigParser()
        machine_storage.read(getDefaultPreferenceStoragePath('cut_machines.ini'))
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
                machine = CutMachine()
            machine.loadSettingsFromConfigParser(machine_storage, 'machine_%d' % n)
            self.addMachine(machine)
            n += 1

        if len(self._machine_list) < 1:
            from Cura.machine.cutMachine import CutMachine
            self.addMachine(CutMachine())

        if len(self._machine_list) < 1:
            return False

        self._toolbox.append(RotateTool(self))
        self._toolbox.append(MirrorTool(self))
        self._toolbox.append(SelectAndMoveTool(self))

        idx = min(int(getPreference('active_machine', 0)), len(self._machine_list) - 1)
        self.setMachine(self._machine_list[idx])

        return True

    def finished(self):
        setPreference('active_machine', self._machine_list.index(self._machine))
        machine_storage = ConfigParser()
        for machine in self._machine_list:
            machine.saveSettingsToConfigParser(machine_storage, 'machine_%d' % (self._machine_list.index(machine)))
        with open(getDefaultPreferenceStoragePath('cut_machines.ini'), "w") as f:
            machine_storage.write(f)

    def setMachine(self, machine):
        super(CuraCutApp, self).setMachine(machine)
        machine.setTranslator(self._translator)
        self._view.refresh()
        self._translator.trigger()

    def setViewMode(self, mode):
        self.getView().setViewMode(mode)
        self._main_window.setViewMode(mode)
