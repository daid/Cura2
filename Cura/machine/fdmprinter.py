
import numpy
import math

from Cura.machine import printer3D
from Cura.machine.setting import Setting
from Cura.machine.setting import SettingCategory


def _calculateLineInfo(machine, value):
    nozzle_size = machine.getSettingValueByKeyFloat('machine_nozzle_size')
    wall_thickness = float(value)
    if wall_thickness <= 0.0:
        return 1, nozzle_size
    line_count = int(wall_thickness / (nozzle_size - 0.0001))
    if line_count == 0:
        return 1, nozzle_size
    line_width = wall_thickness / line_count
    line_width_alt = wall_thickness / (line_count + 1)
    if line_width > nozzle_size * 1.5:
        return line_count + 1, line_width_alt
    return line_count, line_width


class FDMPrinter(printer3D.Printer3D):
    """
    Class that holds settings for any kind of FDMPrinter
    """
    def __init__(self):
        super(FDMPrinter, self).__init__()
        self._timer = None

        self.addSetting('machine', Setting('machine_nozzle_size', 0.4, 'float').setRange(0.1,10).setLabel(_("Nozzle size (mm)"), _("The nozzle size is very important, this is used to calculate the line width of the infill, and used to calculate the amount of outside wall lines and thickness for the wall thickness you entered in the print settings.")))

        self.getSettingByKey('layer_height').setAlwaysVisible()
        self.addSetting('layer_height', Setting('layer_height_0', 0.3, 'float'))

        self.addSetting('resolution', Setting('shell_thickness', 0.8, 'float'))

        self.addSetting('shell_thickness', Setting('wall_thickness', 0.8, 'float'))
        self.addSetting('wall_thickness', Setting('wall_line_count', 2, 'int'))
        self.addSetting('wall_thickness', Setting('wall_line_width', 0.4, 'float'))
        self.addSetting('wall_line_width', Setting('wall_line_width_0', 0.4, 'float'))
        self.addSetting('wall_line_width', Setting('wall_line_width_x', 0.4, 'float'))
        self.getSettingByKey('wall_line_count').setCopyFromParentFunction(lambda m, v: _calculateLineInfo(m, v)[0])
        self.getSettingByKey('wall_line_width').setCopyFromParentFunction(lambda m, v: _calculateLineInfo(m, v)[1])

        self.addSetting('shell_thickness', Setting('top_bottom_thickness', 0.8, 'float').setRange(0).setLabel(_("Bottom/Top thickness (mm)"), _("This controls the thickness of the bottom and top layers, the amount of solid layers put down is calculated by the layer thickness and this value.\nHaving this value a multiple of the layer thickness makes sense. And keep it near your wall thickness to make an evenly strong part.")))
        self.addSetting('top_bottom_thickness', Setting('top_thickness', 0.8, 'float').setRange(0).setLabel(_("Top thickness (mm)"), _("This controls the thickness of the top layers, the amount of solid layers put down is calculated by the layer thickness and this value.\nHaving this value a multiple of the layer thickness makes sense. And keep it near your wall thickness to make an evenly strong part.")))
        self.addSetting('top_bottom_thickness', Setting('bottom_thickness', 0.8, 'float').setRange(0).setLabel(_("Bottom thickness (mm)"), _("This controls the thickness of the bottom layers, the amount of solid layers put down is calculated by the layer thickness and this value.\nHaving this value a multiple of the layer thickness makes sense. And keep it near your wall thickness to make an evenly strong part.")))
        self.addSetting('top_thickness', Setting('top_layers', 4, 'int').setRange(0).setLabel(_("Top layers"), _("This controls the amount of top layers.")))
        self.addSetting('bottom_thickness', Setting('bottom_layers', 4, 'int').setRange(0).setLabel(_("Bottom layers"), _("This controls the amount of bottom layers.")))
        self.getSettingByKey('top_layers').setCopyFromParentFunction(lambda machine, value: math.ceil(float(value) / machine.getSettingValueByKeyFloat('layer_height')))
        self.getSettingByKey('bottom_layers').setCopyFromParentFunction(lambda machine, value: math.ceil(float(value) / machine.getSettingValueByKeyFloat('layer_height')))

        self.addSettingCategory(SettingCategory('material', order=2).setLabel('Material'))
        self.addSetting('material', Setting('material_print_temperature', 220.0, 'float'))
        self.addSetting('material', Setting('material_bed_temperature', 70.0, 'float'))
        self.addSetting('material', Setting('material_diameter', 2.85, 'float'))
        self.addSetting('material', Setting('material_flow', 100.0, 'float'))

        self.addSetting('material', Setting('retraction_enable', True, 'bool').setLabel(_("Enable retraction"), _("Retract the filament when the nozzle is moving over a none-printed area. Details about the retraction can be configured in the advanced tab.")))
        self.addSetting('retraction_enable', Setting('retraction_speed', 40, 'float'))
        self.addSetting('retraction_enable', Setting('retraction_amount', 4.5, 'float'))
        self.addSetting('retraction_enable', Setting('retraction_min_travel', 4.5, 'float'))
        self.addSetting('retraction_enable', Setting('retraction_combing', True, 'bool'))
        self.addSetting('retraction_enable', Setting('retraction_minimal_extrusion', 0.02, 'float'))
        self.addSetting('retraction_enable', Setting('retraction_hop', 0.0, 'float'))

        self.addSettingCategory(SettingCategory('infill', order=15).setLabel('Infill'))
        self.addSetting('infill', Setting('fill_sparse_density', 20.0, 'float'))
        self.addSetting('infill', Setting('fill_overlap', 15.0, 'float'))

        self.addSettingCategory(SettingCategory('platform_adhesion', order=16).setLabel('Skirt/Brim/Raft'))
        self.addSetting('platform_adhesion', Setting('adhesion_type', '', {'': 'None', 'brim': 'Brim', 'raft': 'Raft'}))
        self.addSetting('platform_adhesion', Setting('skirt_line_count', 1, 'int'))
        self.addSetting('platform_adhesion', Setting('skirt_gap', 3.0, 'float'))
        self.addSetting('platform_adhesion', Setting('skirt_minimal_length', 150, 'float'))
        self.addSetting('platform_adhesion', Setting('brim_line_count', 30, 'float'))
        self.addSetting('platform_adhesion', Setting('raft_margin', 5.0, 'float'))
        self.addSetting('platform_adhesion', Setting('raft_line_spacing', 5.0, 'float'))
        self.addSetting('platform_adhesion', Setting('raft_base_thickness', 0.3, 'float'))
        self.addSetting('platform_adhesion', Setting('raft_base_linewidth', 1.0, 'float'))
        self.addSetting('platform_adhesion', Setting('raft_base_speed', 15.0, 'float'))
        self.addSetting('platform_adhesion', Setting('raft_interface_thickness', 0.27, 'float'))
        self.addSetting('platform_adhesion', Setting('raft_interface_linewidth', 0.4, 'float'))
        self.addSetting('platform_adhesion', Setting('raft_airgap', 0.22, 'float'))
        self.addSetting('platform_adhesion', Setting('raft_surface_layers', 2, 'float'))

        self.addSettingCategory(SettingCategory('speed', order=7).setLabel('Speed'))
        self.addSetting('speed', Setting('speed_print', 50.0, 'float').setRange(1).setLabel(_("Print speed (mm/s)"), _("Speed at which printing happens. A well adjusted Ultimaker can reach 150mm/s, but for good quality prints you want to print slower. Printing speed depends on a lot of factors. So you will be experimenting with optimal settings for this.")))
        self.addSetting('speed', Setting('speed_travel', 150.0, 'float'))
        self.addSetting('speed', Setting('speed_layer_0', 15.0, 'float'))
        self.addSetting('speed', Setting('speed_slowdown_layers', 4, 'int'))
        self.addSetting('speed_print', Setting('skirt_speed', 50.0, 'float'))
        self.addSetting('speed_print', Setting('speed_infill', 50.0, 'float'))
        self.addSetting('speed_print', Setting('speed_wall', 50.0, 'float'))
        self.addSetting('speed_print', Setting('speed_support', 50.0, 'float'))
        self.addSetting('speed_wall', Setting('speed_wall_0', 50.0, 'float'))
        self.addSetting('speed_wall', Setting('speed_wall_x', 50.0, 'float'))

        self.addSettingCategory(SettingCategory('cool', order=17).setLabel('Fan/Cool'))
        self.addSetting('cool', Setting('cool_fan_enabled', True, 'bool'))
        self.addSetting('cool_fan_enabled', Setting('cool_fan_speed', 100, 'float'))
        self.addSetting('cool_fan_enabled', Setting('cool_fan_full_at_height', 0.5, 'float'))
        self.addSetting('cool_fan_full_at_height', Setting('cool_fan_full_layer', 4, 'int'))
        self.addSetting('cool_fan_speed', Setting('cool_fan_speed_min', 100, 'float'))
        self.addSetting('cool_fan_speed', Setting('cool_fan_speed_max', 100, 'float'))
        self.addSetting('cool', Setting('cool_min_layer_time', 5.0, 'float'))
        self.addSetting('cool', Setting('cool_min_speed', 10.0, 'float'))
        self.addSetting('cool', Setting('cool_lift_head', False, 'bool'))

        self.addSettingCategory(SettingCategory('blackmagic', order=100).setLabel('Black Magic'))
        self.addSetting('blackmagic', Setting('magic_spiralize', False, 'bool'))

        size = self.getSize()
        ret = numpy.array([[-size[0]/2,-size[1]/2],[size[0]/2,-size[1]/2],[size[0]/2, size[1]/2], [-size[0]/2, size[1]/2]], numpy.float32)
        self._machine_shape = ret
