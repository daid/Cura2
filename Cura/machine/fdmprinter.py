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

        self.addSetting('machine', Setting('machine_nozzle_size', 0.4, 'float'))

        self.addSetting('layer_height', Setting('layer_height_0', 0.3, 'float'))

        self.addSetting('resolution', Setting('shell_thickness', 0.8, 'float'))
        self.addSetting('resolution', Setting('sparse_infill_density', 20.0, 'float'))

        self.addSetting('shell_thickness', Setting('wall_thickness', 0.8, 'float'))
        self.addSetting('wall_thickness', Setting('wall_line_count', 2, 'int'))
        self.addSetting('wall_thickness', Setting('wall_line_width', 0.4, 'float'))
        self.addSetting('wall_line_width', Setting('wall_line_width_0', 0.4, 'float'))
        self.addSetting('wall_line_width', Setting('wall_line_width_1', 0.4, 'float'))

        self.addSetting('shell_thickness', Setting('top_bottom_thickness', 0.8, 'float'))
        self.addSetting('top_bottom_thickness', Setting('top_thickness', 0.8, 'float'))
        self.addSetting('top_bottom_thickness', Setting('bottom_thickness', 0.8, 'float'))

        self.addSettingCategory(SettingCategory('material', order=2).setLabel('Material'))
        self.addSetting('material', Setting('material_print_temperature', 220.0, 'float'))
        self.addSetting('material', Setting('material_bed_temperature', 70.0, 'float'))
        self.addSetting('material', Setting('material_diameter', 2.85, 'float'))
        self.addSetting('material', Setting('material_flow', 100.0, 'float'))

        self.addSetting('material', Setting('retraction_enable', True, 'bool'))
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
        self.addSetting('platform_adhesion', Setting('initial_layer_height', 0.3, 'float'))
        self.addSetting('platform_adhesion', Setting('adhesion_type', '', {'': 'None', 'brim': 'Brim', 'raft': 'Raft'}))
        self.addSetting('platform_adhesion', Setting('skirt_line_count', 1, 'int'))
        self.addSetting('platform_adhesion', Setting('skirt_gap', 3.0, 'float'))
        self.addSetting('platform_adhesion', Setting('skirt_minimal_length', 150, 'float'))
        self.addSetting('platform_adhesion', Setting('brim_line_count', 30, 'float'))
        self.addSetting('platform_adhesion', Setting('raft_margin', 5.0, 'float'))
        self.addSetting('platform_adhesion', Setting('raft_line_spacing', 5.0, 'float'))
        self.addSetting('platform_adhesion', Setting('raft_base_thickness', 0.3, 'float'))
        self.addSetting('platform_adhesion', Setting('raft_base_linewidth', 1.0, 'float'))
        self.addSetting('platform_adhesion', Setting('raft_interface_thickness', 0.27, 'float'))
        self.addSetting('platform_adhesion', Setting('raft_interface_linewidth', 0.4, 'float'))
        self.addSetting('platform_adhesion', Setting('raft_airgap', 0.22, 'float'))
        self.addSetting('platform_adhesion', Setting('raft_surface_layers', 2, 'float'))

        self.addSettingCategory(SettingCategory('speed', order=7).setLabel('Speed'))
        self.addSetting('speed', Setting('speed_print', 50.0, 'float'))
        self.addSetting('speed', Setting('speed_travel', 150.0, 'float'))
        self.addSetting('speed_print', Setting('speed_layer_0', 50.0, 'float'))
        self.addSetting('speed_print', Setting('speed_infill', 50.0, 'float'))
        self.addSetting('speed_print', Setting('speed_wall', 50.0, 'float'))
        self.addSetting('speed_wall', Setting('speed_wall_0', 50.0, 'float'))
        self.addSetting('speed_wall', Setting('speed_wall_1', 50.0, 'float'))

        self.addSettingCategory(SettingCategory('cool', order=17).setLabel('Fan/Cool'))
        self.addSetting('cool', Setting('cool_fan_enabled', True, 'bool'))
        self.addSetting('cool_fan_enabled', Setting('cool_fan_speed', 100, 'float'))
        self.addSetting('cool_fan_enabled', Setting('cool_fan_full_at_height', 0.5, 'float'))
        self.addSetting('cool_fan_speed', Setting('cool_fan_speed_min', 100, 'float'))
        self.addSetting('cool_fan_speed', Setting('cool_fan_speed_max', 100, 'float'))
        self.addSetting('cool', Setting('cool_min_layer_time', 5.0, 'float'))
        self.addSetting('cool', Setting('cool_min_speed', 10.0, 'float'))
        self.addSetting('cool', Setting('cool_lift_head', False, 'bool'))

        self.addSettingCategory(SettingCategory('blackmagic', order=100).setLabel('Black Magic'))
        self.addSetting('blackmagic', Setting('spiralize', False, 'bool'))

        size = self.getSize()
        ret = numpy.array([[-size[0]/2,-size[1]/2],[size[0]/2,-size[1]/2],[size[0]/2, size[1]/2], [-size[0]/2, size[1]/2]], numpy.float32)
        self._machine_shape = ret
