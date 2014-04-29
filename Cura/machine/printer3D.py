__author__ = 'Jaime van Kessel'

from Cura.machine import machine
from Cura.machine.setting import Setting
from Cura.machine.setting import SettingCategory

class Printer3D(machine.Machine):
    """
    Class that holds settings for any kind of 3D printers
    """
    def __init__(self):
        super(Printer3D,self).__init__()
        self.addSettingCategory(SettingCategory('resolution', order=0).setLabel('Resolution'))
        self.addSetting('resolution', Setting('layer_height', 0.2, 'float'))

        self.addSettingCategory(SettingCategory('support', order=5).setLabel('Support Material'))
        self.addSetting('support', Setting('support_enable', False, 'bool'))
        self.addSetting('support_enable', Setting('support_type', '', {'': 'None', 'buildplate': 'Touching buildplate', 'everywhere': 'Everywhere'}))
        self.addSetting('support_enable', Setting('support_angle', 60, 'float'))
        self.addSetting('support_enable', Setting('support_fill_rate', 15, 'float'))
        self.addSetting('support_enable', Setting('support_xy_distance', 0.7, 'float'))
        self.addSetting('support_enable', Setting('support_z_distance', 0.15, 'float'))

        self._disallowed_zones = []  # List of polys

    def getDisallowedZones(self):
        return self._disallowed_zones
