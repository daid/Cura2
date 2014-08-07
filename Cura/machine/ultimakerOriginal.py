import numpy

from Cura.machine.fdmprinter import FDMPrinter


class UltimakerOriginal(FDMPrinter):
    def __init__(self):
        super(UltimakerOriginal, self).__init__()

        self.getSettingByKey('machine_name').setDefault('Ultimaker').setVisible(False)
        self.getSettingByKey('machine_icon').setDefault('save_button.png').setVisible(False)
        self.getSettingByKey('display_model').setDefault('ultimaker_platform.obj').setVisible(False)
        self.getSettingByKey('machine_width').setDefault('205')
        self.getSettingByKey('machine_depth').setDefault('205')
        self.getSettingByKey('machine_height').setDefault('200')
        self.getSettingByKey('machine_heated_bed').setDefault('False')
        self.getSettingByKey('machine_center_is_zero').setDefault('False').setVisible(False)
        self.getSettingByKey('machine_build_area_shape').setVisible(False)

        self.getSettingByKey('machine_nozzle_size').setDefault('0.4')

        self.getSettingByKey('machine_head_shape_min_x').setDefault('75')
        self.getSettingByKey('machine_head_shape_min_y').setDefault('18')
        self.getSettingByKey('machine_head_shape_max_x').setDefault('18')
        self.getSettingByKey('machine_head_shape_max_y').setDefault('35')
        self.getSettingByKey('machine_nozzle_gantry_distance').setDefault('55')

        self.getSettingByKey('machine_nozzle_offset_x_1').setDefault('18.0')
        self.getSettingByKey('machine_nozzle_offset_y_1').setDefault('0.0')

        self._updateMachineShape()
