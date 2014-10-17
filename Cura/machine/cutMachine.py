import numpy

from Cura.machine import machine
from Cura.machine.setting import Setting
from Cura.machine.setting import SettingCategory


class CutMachine(machine.Machine):
    """
    Class that holds settings for any kind of CNC milling machine
    """
    def __init__(self):
        super(CutMachine,self).__init__()
        self.addSettingCategory(SettingCategory('tool', order=0).setLabel('Tool'))
        self.addSetting('tool', Setting('tool_diameter', 8.0, 'float').setRange(0.0001).setLabel(_("Tool diameter (mm)"), _("?")))
        self.addSetting('tool', Setting('feedrate', 10.0, 'float').setRange(0.0001).setLabel(_("Feedrate (mm/sec)"), _("?")))
        self.addSetting('tool', Setting('cut_depth_step', 3, 'float').setRange(0.0001).setLabel(_("Cut step size (mm)"), _("Maximum depth the tool cuts at once")))
        self.addSettingCategory(SettingCategory('cutting', order=1).setLabel('Cut'))
        self.addSetting('cutting', Setting('cut_depth', 18, 'float').setRange(0.0001).setLabel(_("Cut depth (mm)"), _("?")))
        self.getSettingByKey('machine_width').setLabel(_('Cutting area width (mm)'))
        self.getSettingByKey('machine_depth').setLabel(_('Cutting area depth (mm)'))
        self.getSettingByKey('machine_height').setLabel(_('Cutting area height (mm)'))

        self.getSettingByKey('machine_width').addCallback(self._updateMachineShape)
        self.getSettingByKey('machine_depth').addCallback(self._updateMachineShape)

        self.addSetting('machine', Setting('machine_start_gcode', '', 'string').setLabel(_('Start GCode')))
        self.addSetting('machine', Setting('machine_end_gcode', '', 'string').setLabel(_('End GCode')))

        self._updateMachineShape()

    def _updateMachineShape(self):
        size = self.getSize()
        ret = numpy.array([[-size[0]/2,-size[1]/2],[size[0]/2,-size[1]/2],[size[0]/2, size[1]/2], [-size[0]/2, size[1]/2]], numpy.float32)
        self._machine_shape = ret

    def getExportExtension(self):
        return 'nc'