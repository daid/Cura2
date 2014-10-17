import numpy

from Cura.machine.fdmprinter import FDMPrinter


class Ultimaker2(FDMPrinter):
    def __init__(self):
        super(Ultimaker2, self).__init__()

        self.getSettingByKey('machine_name').setDefault('Ultimaker2').setVisible(False)
        self.getSettingByKey('machine_icon').setDefault('icon_ultimaker2.png').setVisible(False)
        self.getSettingByKey('display_model').setDefault('ultimaker2_platform.obj').setVisible(False)
        self.getSettingByKey('machine_width').setDefault('230').setVisible(False)
        self.getSettingByKey('machine_depth').setDefault('225').setVisible(False)
        self.getSettingByKey('machine_height').setDefault('205').setVisible(False)
        self.getSettingByKey('machine_heated_bed').setDefault('True').setVisible(False)
        self.getSettingByKey('machine_center_is_zero').setDefault('False').setVisible(False)
        self.getSettingByKey('machine_build_area_shape').setVisible(False)

        self.getSettingByKey('machine_nozzle_size').setDefault('0.4')

        self.getSettingByKey('machine_head_shape_min_x').setDefault('40').setVisible(False)
        self.getSettingByKey('machine_head_shape_min_y').setDefault('10').setVisible(False)
        self.getSettingByKey('machine_head_shape_max_x').setDefault('60').setVisible(False)
        self.getSettingByKey('machine_head_shape_max_y').setDefault('30').setVisible(False)
        self.getSettingByKey('machine_nozzle_gantry_distance').setDefault('55').setVisible(False)

        self.getSettingByKey('machine_nozzle_offset_x_1').setDefault('18.0')
        self.getSettingByKey('machine_nozzle_offset_y_1').setDefault('0.0')

        self.getSettingByKey('machine_start_gcode').setDefault('; On the Ultimaker 2 the start and end sequence is controlled by the firmware.\n; You can add your own custom GCode here which is ran after the firmware start code.')
        self.getSettingByKey('machine_end_gcode').setDefault('; On the Ultimaker 2 the start and end sequence is controlled by the firmware.\n; You can add your own custom GCode here which is ran before the firmware end code.')
        self.getSettingByKey('machine_gcode_flavor').setDefault('UltiGCode')

        self.getSettingByKey('material_diameter').setDefault('1.128')

        self._updateMachineShape()

    def _updateMachineShape(self):
        # Update the Ultimaker 2 no-go-zones
        self._disallowed_zones = []
        w = 25
        h = 10
        size = self.getSize()
        self._disallowed_zones.append(numpy.array([[-size[0]/2,-size[1]/2],[-size[0]/2+w+2,-size[1]/2], [-size[0]/2+w,-size[1]/2+h], [-size[0]/2,-size[1]/2+h]], numpy.float32))
        self._disallowed_zones.append(numpy.array([[ size[0]/2-w-2,-size[1]/2],[ size[0]/2,-size[1]/2], [ size[0]/2,-size[1]/2+h],[ size[0]/2-w,-size[1]/2+h]], numpy.float32))
        self._disallowed_zones.append(numpy.array([[-size[0]/2+w+2, size[1]/2],[-size[0]/2, size[1]/2], [-size[0]/2, size[1]/2-h],[-size[0]/2+w, size[1]/2-h]], numpy.float32))
        self._disallowed_zones.append(numpy.array([[ size[0]/2, size[1]/2],[ size[0]/2-w-2, size[1]/2], [ size[0]/2-w, size[1]/2-h],[ size[0]/2, size[1]/2-h]], numpy.float32))

        super(Ultimaker2, self)._updateMachineShape()
