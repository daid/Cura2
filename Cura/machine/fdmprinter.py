__author__ = 'Jaime van Kessel'

from Cura.machine import printer3D
from Cura.machine.setting import Setting
from Cura.machine.setting import SettingCategory
import numpy

class FDMPrinter(printer3D.Printer3D):
    """
    Class that holds settings for any kind of FDMPrinter
    """
    def __init__(self):
        super(FDMPrinter,self).__init__()

        self.addSetting('resolution', Setting('shell_thickness', 0.8, 'float'))
        self.addSetting('resolution', Setting('sparse_infill_density', 20.0, 'float'))
        self.addSettingCategory(SettingCategory('platform_adhesion', order=1))
        self.addSetting('platform_adhesion', Setting('initial_layer_height', 0.3, 'float'))
        self.addSetting('platform_adhesion', Setting('adhesion_type', 'None', ['None', 'Brim', 'Raft']))

        self.addSettingCategory(SettingCategory('speed', order=2))
        self.addSetting('speed', Setting('speed_print', 50.0, 'float'))
        self.addSetting('speed_print', Setting('speed_infill', 50.0, 'float'))

        size = self.getSize()
        ret = numpy.array([[-size[0]/2,-size[1]/2],[size[0]/2,-size[1]/2],[size[0]/2, size[1]/2], [-size[0]/2, size[1]/2]], numpy.float32)
        self._machine_shape = ret
