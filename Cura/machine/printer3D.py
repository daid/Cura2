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
        self.addSetting('resolution', Setting('layer_height', 0.2, 'float').setRange(0.0001).setLabel(_("Layer height (mm)"), _("Layer height in millimeters.\nThis is the most important setting to determine the quality of your print. Normal quality prints are 0.1mm, high quality is 0.06mm. You can go up to 0.25mm with an Ultimaker for very fast prints at low quality.")))

        self.addSettingCategory(SettingCategory('support', order=5).setLabel('Support Material'))
        self.addSetting('support', Setting('support_enable', False, 'bool'))
        self.addSetting('support_enable', Setting('support_type', '', {'': 'None', 'buildplate': 'Touching buildplate', 'everywhere': 'Everywhere'}).setLabel(_("Structure type"), _("The type of support structure.\nGrid is very strong and can come off in 1 piece, however, sometimes it is too strong.\nLines are single walled lines that break off one at a time. Which is more work to remove, but as it is less strong it does work better on tricky prints.")))
        self.addSetting('support_enable', Setting('support_angle', 60, 'float').setRange(0,90).setLabel(_("Overhang angle for support (deg)"), _("The minimal angle that overhangs need to have to get support. With 0 degree being horizontal and 90 degree being vertical.")))
        self.addSetting('support_enable', Setting('support_fill_rate', 15, 'float').setRange(0,100).setLabel(_("Fill amount (%)"), _("Amount of infill structure in the support material, less material gives weaker support which is easier to remove. 15% seems to be a good average.")))
        self.addSetting('support_enable', Setting('support_xy_distance', 0.7, 'float').setRange(0,10).setLabel(_("Distance X/Y (mm)"), _("Distance of the support material from the print, in the X/Y directions.\n0.7mm gives a nice distance from the print so the support does not stick to the print.")))
        self.addSetting('support_enable', Setting('support_z_distance', 0.15, 'float').setRange(0,10).setLabel(_("Distance Z (mm)"), _("Distance from the top/bottom of the support to the print. A small gap here makes it easier to remove the support but makes the print a bit uglier.\n0.15mm gives a good seperation of the support material.")))

        self._disallowed_zones = []  # List of polys

    def getDisallowedZones(self):
        return self._disallowed_zones
