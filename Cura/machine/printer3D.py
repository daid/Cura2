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
        self.addSettingCategory(SettingCategory('resolution'))
        self.addSetting('resolution', Setting('layer_height', 0.2, 'float'))

        self._disallowed_zones = []  # List of polys

    def getDisallowedZones(self):
        return self._disallowed_zones
