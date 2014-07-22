
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

        # Machine settings
        self.addSetting('machine', Setting('machine_nozzle_size', 0.4, 'float').setRange(0.1,10).setLabel(_("Nozzle diameter (mm)"), _("The nozzle size is very important, this is used to calculate the line width of the infill, and used to calculate the amount of outside wall lines and thickness for the wall thickness you entered in the print settings.")))
        self.addSetting('machine', Setting('machine_nozzle_count', '1', {str(n): str(n) for n in range(1, self.getMaxNozzles() + 1)}).setLabel(_("Extruder count"), _("Amount of extruders in this machine.")))
        self.addSetting('machine', Setting('machine_heated_bed', False, 'bool').setLabel(_('Heated bed')))
        self.addSetting('machine', Setting('machine_center_is_zero', False, 'bool').setLabel(_('Center is 0,0')))
        self.addSetting('machine', Setting('machine_build_area_shape', 'rectangle', {'rectangle': 'Rectangle', 'round': 'Round'}).setLabel(_('Build area shape')))

        self.addSetting('machine', Setting('machine_head_shape_min_x', 0, 'float').setLabel(_("Head size towards X min (mm)"), _("The head size when printing multiple objects, measured from the tip of the nozzle towards the outer part of the head. 75mm for an Ultimaker if the fan is on the left side.")))
        self.addSetting('machine', Setting('machine_head_shape_min_y', 0, 'float').setLabel(_("Head size towards Y min (mm)"), _("The head size when printing multiple objects, measured from the tip of the nozzle towards the outer part of the head. 18mm for an Ultimaker if the fan is on the left side.")))
        self.addSetting('machine', Setting('machine_head_shape_max_x', 0, 'float').setLabel(_("Head size towards X max (mm)"), _("The head size when printing multiple objects, measured from the tip of the nozzle towards the outer part of the head. 18mm for an Ultimaker if the fan is on the left side.")))
        self.addSetting('machine', Setting('machine_head_shape_max_y', 0, 'float').setLabel(_("Head size towards Y max (mm)"), _("The head size when printing multiple objects, measured from the tip of the nozzle towards the outer part of the head. 35mm for an Ultimaker if the fan is on the left side.")))
        self.addSetting('machine', Setting('machine_nozzle_gantry_distance', 0, 'float').setLabel(_("Nozzle to gantry distance (mm)"), _("Z distance between the tip of the nozzle and the first gantry of your printer. Only objects smaller then this size can be printed 'one-at-a-time'")))
        for n in xrange(1, self.getMaxNozzles() + 1):
            self.addSetting('machine', Setting('machine_nozzle_offset_x_' + str(n), 0.0, 'float').setLabel(_('Nozzle %d offset X') % (n + 1)))
            self.addSetting('machine', Setting('machine_nozzle_offset_y_' + str(n), 0.0, 'float').setLabel(_('Nozzle %d offset Y') % (n + 1)))
        self.addSetting('machine', Setting('machine_start_gcode', '', 'string').setLabel(_('Start GCode')))
        self.addSetting('machine', Setting('machine_end_gcode', '', 'string').setLabel(_('End GCode')))

        # Profile settings
        self.getSettingByKey('layer_height').setAlwaysVisible()
        self.addSetting('layer_height', Setting('layer_height_0', 0.3, 'float').setRange(0).setLabel(_("Initial layer thickness (mm)"), _("Layer thickness of the bottom layer. A thicker bottom layer makes sticking to the bed easier.")))

        self.addSetting('resolution', Setting('shell_thickness', 0.8, 'float').setRange(0.0).setLabel(_("Shell thickness (mm)"), _("Thickness of the outside shell in the horizontal and vertical direction.\nThis is used in combination with the nozzle size to define the number\nof perimeter lines and the thickness of those perimeter lines.\nThis is also used to define the number of solid top and bottom layers.")))

        self.addSetting('shell_thickness', Setting('wall_thickness', 0.8, 'float').setRange(0.0).setLabel(_("Wall thickness (mm)"), _("Thickness of the outside walls in the horizontal direction.\nThis is used in combination with the nozzle size to define the number\nof perimeter lines and the thickness of those perimeter lines.")))
        self.addSetting('wall_thickness', Setting('wall_line_count', 2, 'int').setRange(0).setLabel(_("Wall line count"), _("Amount of wall lines. This these lines are called perimeter lines in other tools and impact the strength and structural integrity of your print.")))
        self.addSetting('wall_thickness', Setting('wall_line_width', 0.4, 'float').setRange(0.0).setLabel(_("Wall line width"), _("Width of a single wall line. Each wall line will be printed with this width in mind.")))
        self.addSetting('wall_line_width', Setting('wall_line_width_0', 0.4, 'float').setRange(0.0).setLabel(_("First wall line width"), _("Width of the outer wall line. By printing a thinner first wall line you can print higher details with a larger nozzle.")))
        self.addSetting('wall_line_width', Setting('wall_line_width_x', 0.4, 'float').setRange(0.0).setLabel(_("Other walls line width"), _("Width of a single wall line for all the other lines except the outer one.")))
        self.getSettingByKey('wall_line_count').setCopyFromParentFunction(lambda m, v: _calculateLineInfo(m, v)[0])
        self.getSettingByKey('wall_line_width').setCopyFromParentFunction(lambda m, v: _calculateLineInfo(m, v)[1])

        self.addSetting('shell_thickness', Setting('top_bottom_thickness', 0.8, 'float').setRange(0).setLabel(_("Bottom/Top thickness (mm)"), _("This controls the thickness of the bottom and top layers, the amount of solid layers put down is calculated by the layer thickness and this value.\nHaving this value a multiple of the layer thickness makes sense. And keep it near your wall thickness to make an evenly strong part.")))
        self.addSetting('top_bottom_thickness', Setting('top_thickness', 0.8, 'float').setRange(0).setLabel(_("Top thickness (mm)"), _("This controls the thickness of the top layers, the amount of solid layers put down is calculated by the layer thickness and this value.\nHaving this value a multiple of the layer thickness makes sense. And keep it near your wall thickness to make an evenly strong part.")))
        self.addSetting('top_bottom_thickness', Setting('bottom_thickness', 0.8, 'float').setRange(0).setLabel(_("Bottom thickness (mm)"), _("This controls the thickness of the bottom layers, the amount of solid layers put down is calculated by the layer thickness and this value.\nHaving this value a multiple of the layer thickness makes sense. And keep it near your wall thickness to make an evenly strong part.")))
        self.addSetting('top_thickness', Setting('top_layers', 4, 'int').setRange(0).setLabel(_("Top layers"), _("This controls the amount of top layers.")))
        self.addSetting('bottom_thickness', Setting('bottom_layers', 4, 'int').setRange(0).setLabel(_("Bottom layers"), _("This controls the amount of bottom layers.")))
        self.addSetting('resolution', Setting('top_bottom_pattern', 'lines', {'lines': _('Lines'), 'concentric': _('Concentric')}).setLabel(_('Bottom/Top pattern'), _('Pattern of the top/bottom filling. This normally is done with lines to get the best possible filling. But in some cases a concentric fill gives a nicer end result finish.')))
        self.getSettingByKey('top_layers').setCopyFromParentFunction(lambda machine, value: math.ceil(float(value) / machine.getSettingValueByKeyFloat('layer_height')))
        self.getSettingByKey('bottom_layers').setCopyFromParentFunction(lambda machine, value: math.ceil(float(value) / machine.getSettingValueByKeyFloat('layer_height')))

        self.addSettingCategory(SettingCategory('material', order=2).setLabel('Material'))
        self.addSetting('material', Setting('material_print_temperature', 220.0, 'float').setRange(0,340).setLabel(_("Printing temperature (C)"), _("Temperature used for printing. Set at 0 to pre-heat yourself.\nFor PLA a value of 210C is usually used.\nFor ABS a value of 230C or higher is required.")))
        self.addSetting('material', Setting('material_bed_temperature', 70.0, 'float').setRange(0,340).setLabel(_("Bed temperature (C)"), _("Temperature used for the heated printer bed. Set at 0 to pre-heat yourself.")))
        self.addSetting('material', Setting('material_diameter', 2.85, 'float').setRange(1).setLabel(_("Diameter (mm)"), _("Diameter of your filament, as accurately as possible.\nIf you cannot measure this value you will have to calibrate it, a higher number means less extrusion, a smaller number generates more extrusion.")))
        self.addSetting('material', Setting('material_flow', 100.0, 'float').setRange(5,300).setLabel(_("Flow (%)"), _("Flow compensation, the amount of material extruded is multiplied by this value")))

        self.addSetting('material', Setting('retraction_enable', True, 'bool').setLabel(_("Enable retraction"), _("Retract the filament when the nozzle is moving over a none-printed area. Details about the retraction can be configured in the advanced tab.")))
        self.addSetting('retraction_enable', Setting('retraction_speed', 40, 'float').setRange(0.1).setLabel(_("Speed (mm/s)"), _("Speed at which the filament is retracted, a higher retraction speed works better. But a very high retraction speed can lead to filament grinding.")))
        self.addSetting('retraction_enable', Setting('retraction_amount', 4.5, 'float').setRange(0).setLabel(_("Distance (mm)"), _("Amount of retraction, set at 0 for no retraction at all. A value of 4.5mm seems to generate good results for 3mm filament.")))
        self.addSetting('retraction_enable', Setting('retraction_min_travel', 4.5, 'float').setRange(0).setLabel(_("Minimum travel (mm)"), _("Minimum amount of travel needed for a retraction to happen at all. To make sure you do not get a lot of retractions in a small area.")))
        self.addSetting('retraction_enable', Setting('retraction_combing', True, 'bool').setLabel(_("Enable combing"), _("Combing is the act of avoiding holes in the print for the head to travel over. If combing is disabled the printer head moves straight from the start point to the end point and it will always retract.")))
        self.addSetting('retraction_enable', Setting('retraction_minimal_extrusion', 0.02, 'float').setRange(0).setLabel(_("Minimal extrusion before retracting (mm)"), _("The minimal amount of extrusion that needs to be done before retracting again if a retraction needs to happen before this minimal is reached the retraction is ignored.\nThis avoids retracting a lot on the same piece of filament which flattens the filament and causes grinding issues.")))
        self.addSetting('retraction_enable', Setting('retraction_hop', 0.0, 'float').setRange(0).setLabel(_("Z hop when retracting (mm)"), _("When a retraction is done, the head is lifted by this amount to travel over the print. A value of 0.075 works well. This feature has a lot of positive effect on delta towers.")))
        self.getSettingByKey('retraction_speed').setCopyFromParentFunction(None)
        self.getSettingByKey('retraction_amount').setCopyFromParentFunction(None)
        self.getSettingByKey('retraction_min_travel').setCopyFromParentFunction(None)
        self.getSettingByKey('retraction_combing').setCopyFromParentFunction(None)
        self.getSettingByKey('retraction_minimal_extrusion').setCopyFromParentFunction(None)
        self.getSettingByKey('retraction_hop').setCopyFromParentFunction(None)

        self.addSettingCategory(SettingCategory('infill', order=15).setLabel('Infill'))
        self.addSetting('infill', Setting('fill_sparse_density', 20.0, 'float').setRange(0, 100).setLabel(_("Fill Density (%)"), _("This controls how densely filled the insides of your print will be. For a solid part use 100%, for an empty part use 0%. A value around 20% is usually enough.\nThis won't affect the outside of the print and only adjusts how strong the part becomes.")))
        self.addSetting('infill', Setting('fill_overlap', 15.0, 'float').setRange(0,100).setLabel(_("Infill overlap (%)"), _("Amount of overlap between the infill and the walls. There is a slight overlap with the walls and the infill so the walls connect firmly to the infill.")))
        self.addSetting('fill_sparse_density', Setting('fill_pattern', 'grid', {'grid': 'Grid', 'lines': 'Lines', 'concentric': 'Concentric'}).setLabel(_('Infill pattern.'), _('Cura defaults to switch between grid and line infill. But with this setting visible you can control this yourself.\nThe line infill is cross hatched every other layer, while the grid is cross-hatched each layer.')))
        self.addSetting('infill', Setting('fill_sparse_thickness', 0.1, 'float').setRange(0).setLabel(_('Sparse infill thickness (mm)'), _('Thickness of the sparse infill. This is rounded to a multiple of the layer-thickness and used to print the sparse-infill at possible thicker layers to save printing time.')))
        self.addSetting('fill_sparse_thickness', Setting('fill_sparse_combine', 1, 'int').setRange(1).setLabel(_('Sparse infill layers'), _('Amount of layers that are combined together to form sparse infill.')))
        self.getSettingByKey('fill_sparse_density').setAlwaysVisible()
        self.getSettingByKey('fill_pattern').setCopyFromParentFunction(lambda m, v: 'lines' if float(v) > 25 else 'grid')
        self.getSettingByKey('fill_sparse_combine').setCopyFromParentFunction(lambda m, v: math.floor((float(v) + 0.001) / m.getSettingValueByKeyFloat('layer_height')))

        self.addSettingCategory(SettingCategory('platform_adhesion', order=16).setLabel('Skirt/Brim/Raft'))
        self.addSetting('platform_adhesion', Setting('adhesion_type', '', {'': 'None', 'brim': 'Brim', 'raft': 'Raft'}).setLabel(_("Platform adhesion type"), _("Different options that help in preventing corners from lifting due to warping.\nBrim adds a single layer thick flat area around your object which is easy to cut off afterwards, and it is the recommended option.\nRaft adds a thick raster below the object and a thin interface between this and your object.\n(Note that enabling the brim or raft disables the skirt)")))
        self.addSetting('platform_adhesion', Setting('skirt_line_count', 1, 'int').setRange(0).setLabel(_("Line count"), _("The skirt is a line drawn around the object at the first layer. This helps to prime your extruder, and to see if the object fits on your platform.\nSetting this to 0 will disable the skirt. Multiple skirt lines can help priming your extruder better for small objects.")))
        self.addSetting('platform_adhesion', Setting('skirt_gap', 3.0, 'float').setRange(0).setLabel(_("Skirt distance (mm)"), _("The distance between the skirt and the first layer.\nThis is the minimal distance, multiple skirt lines will be put outwards from this distance.")))
        self.addSetting('platform_adhesion', Setting('skirt_minimal_length', 250, 'float').setRange(0).setLabel(_("Skirt minimal length (mm)"), _("The minimal length of the skirt, if this minimal length is not reached it will add more skirt lines to reach this minimal length.\nNote: If the line count is set to 0 this is ignored.")))
        self.addSetting('platform_adhesion', Setting('brim_line_count', 30, 'float').setRange(1,100).setLabel(_("Brim line amount"), _("The amount of lines used for a brim, more lines means a larger brim which sticks better, but this also makes your effective print area smaller.")))
        self.addSetting('platform_adhesion', Setting('raft_margin', 5.0, 'float').setRange(0).setLabel(_("Raft extra margin (mm)"), _("If the raft is enabled, this is the extra raft area around the object which is also rafted. Increasing this margin will create a stronger raft while using more material and leaving less area for your print.")))
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
        self.addSetting('speed', Setting('speed_travel', 150.0, 'float').setRange(0.1).setLabel(_("Travel speed (mm/s)"), _("Speed at which travel moves are done, a well built Ultimaker can reach speeds of 250mm/s. But some machines might miss steps then.")))
        self.addSetting('speed', Setting('speed_layer_0', 15.0, 'float').setRange(0.1).setLabel(_("Bottom layer speed (mm/s)"), _("Print speed for the bottom layer, you want to print the first layer slower so it sticks better to the printer bed.")))
        self.addSetting('speed', Setting('speed_slowdown_layers', 4, 'int').setRange(0).setLabel(_("Amount of slower layers"), _("The first few layers are printed slower then the rest of the object, this to get better adhesion to the printer bed and improve the overall success rate of prints. The speed is gradually increased over these layers. 4 layers of speedup is generally right for most materials and printers.")))
        self.addSetting('speed_layer_0', Setting('skirt_speed', 15.0, 'float').setRange(0.1).setLabel(_('Skirt speed (mm/2)'), _('Speed at which the skirt and brim are printed. Normally this is done at the initial layer speed. But sometimes you want to print the skirt at a different speed.')))
        self.addSetting('speed_print', Setting('speed_infill', 50.0, 'float').setRange(0.1).setLabel(_("Infill speed (mm/s)"), _("Speed at which infill parts are printed. Printing the infill faster can greatly reduce printing time, but this can negatively affect print quality.")))
        self.addSetting('speed_print', Setting('speed_wall', 50.0, 'float').setRange(0.1).setLabel(_("Shell speed (mm/s)"), _("Speed at which shell is printed. Printing the outer shell at a lower speed improves the final skin quality.")))
        self.addSetting('speed_print', Setting('speed_support', 50.0, 'float').setRange(0.1).setLabel(_("Support print speed (mm/s)"), _("Speed at which exterior support is printed. Printing exterior supports at higher speeds can greatly improve printing time. And the quality of exterior support is usually no problem.")))
        self.addSetting('speed_wall', Setting('speed_wall_0', 50.0, 'float').setRange(0.1).setLabel(_("Outer shell speed (mm/s)"), _("Speed at which outer shell is printed. Printing the outer shell at a lower speed improves the final skin quality. However, having a large difference between the inner shell speed and the outer shell speed will effect quality in a negative way.")))
        self.addSetting('speed_wall', Setting('speed_wall_x', 50.0, 'float').setRange(0.1).setLabel(_("Inner shell speed (mm/s)"), _("Speed at which inner shells are printed. Printing the inner shell faster then the outer shell will reduce printing time. It is good to set this somewhere in between the outer shell speed and the infill/printing speed.")))

        self.addSettingCategory(SettingCategory('cool', order=17).setLabel('Fan/Cool'))
        self.addSetting('cool', Setting('cool_fan_enabled', True, 'bool').setLabel(_("Enable cooling fan"), _("Enable the cooling fan during the print. The extra cooling from the cooling fan is essential during faster prints.")))
        self.addSetting('cool_fan_enabled', Setting('cool_fan_speed', 100, 'float').setRange(0,100).setLabel(_("Fan speed (%)"), _("Fan speed used for the print cooling fan on the printer head.")))
        self.getSettingByKey('cool_fan_speed').setCopyFromParentFunction(lambda m, v: 100 if v else 0)
        self.addSetting('cool', Setting('cool_fan_full_at_height', 0.5, 'float').setRange(0).setLabel(_("Fan full on at height (mm)"), _("The height at which the fan is turned on completely. For the layers below this the fan speed is scaled linearly with the fan off at layer 0.")))
        self.addSetting('cool_fan_full_at_height', Setting('cool_fan_full_layer', 4, 'int').setRange(0).setLabel(_("Fan full on at layer"), _("The layer number at which the fan is turned on completely. For the layers below this the fan speed is scaled linearly with the fan off at layer 0.")))
        self.getSettingByKey('cool_fan_full_layer').setCopyFromParentFunction(lambda m, v: int((float(v) - m.getSettingValueByKeyFloat('layer_height_0') + 0.001) / m.getSettingValueByKeyFloat('layer_height')))
        self.addSetting('cool_fan_speed', Setting('cool_fan_speed_min', 100, 'float').setRange(0,100).setLabel(_("Fan speed min (%)"), _("Normally the fan is ran at the minimal fan speed. If the layer is slowed down due to minimal layer time, the fan speed is put somewhere between minimal and maximal fan speed.")))
        self.addSetting('cool_fan_speed', Setting('cool_fan_speed_max', 100, 'float').setRange(0,100).setLabel(_("Fan speed max (%)"), _("Normally the fan is ran at the minimal fan speed. If the layer is slowed down due to minimal layer time, the fan speed is put somewhere between minimal and maximal fan speed.")))
        self.addSetting('cool', Setting('cool_min_layer_time', 5.0, 'float').setRange(0).setLabel(_("Minimal layer time (sec)"), _("Minimum time spent in a layer, gives the layer time to cool down before the next layer is put on top. If the layer will be placed down too fast the printer will slow down to make sure it has spent at least this amount of seconds printing this layer.")))
        self.addSetting('cool', Setting('cool_min_speed', 10.0, 'float').setRange(0).setLabel(_("Minimum speed (mm/s)"), _("The minimal layer time can cause the print to slow down so much it starts to ooze. The minimal feedrate protects against this. Even if a print gets slowed down it will never be slower than this minimal speed.")))
        self.addSetting('cool', Setting('cool_lift_head', False, 'bool').setLabel(_("Cool head lift"), _("Lift the head if the minimal speed is hit because of cool slowdown, and wait the extra time so the minimal layer time is always hit.")))

        self.addSettingCategory(SettingCategory('blackmagic', order=100).setLabel('Black Magic'))
        self.addSetting('blackmagic', Setting('magic_spiralize', False, 'bool').setLabel(_("Spiralize the outer contour"), _("Spiralize is smoothing out the Z move of the outer edge. This will create a steady Z increase over the whole print. This feature turns a solid object into a single walled print with a solid bottom.\nThis feature used to be called Joris in older versions.")))

        size = self.getSize()
        ret = numpy.array([[-size[0]/2,-size[1]/2],[size[0]/2,-size[1]/2],[size[0]/2, size[1]/2], [-size[0]/2, size[1]/2]], numpy.float32)
        self._machine_shape = ret

    def getMaxNozzles(self):
        return 8

    def getHeadShape(self):
        x_min = self.getSettingValueByKeyFloat('machine_head_shape_min_x')
        y_min = self.getSettingValueByKeyFloat('machine_head_shape_min_y')
        x_max = self.getSettingValueByKeyFloat('machine_head_shape_max_x')
        y_max = self.getSettingValueByKeyFloat('machine_head_shape_max_y')
        return numpy.array([[-x_min,-y_min],[x_max,-y_min],[x_max, y_max], [-x_min, y_max]], numpy.float32)

    def getExtraPrintAreaShape(self):
        if self.getSettingValueByKey('adhesion_type') == 'brim':
            x = y = self.getSettingValueByKeyFloat('brim_line_count') * self.getSettingValueByKeyFloat('wall_line_width_0')
        else:
            x = y = self.getSettingValueByKeyFloat('wall_line_width_0') + self.getSettingValueByKeyFloat('skirt_gap')
        return numpy.array([[-x,-y],[x,-y],[x, y], [-x, y]], numpy.float32)

    def getHeadSizeMin(self):
        x_min = self.getSettingValueByKeyFloat('machine_head_shape_min_x')
        y_min = self.getSettingValueByKeyFloat('machine_head_shape_min_y')
        x_max = self.getSettingValueByKeyFloat('machine_head_shape_max_x')
        y_max = self.getSettingValueByKeyFloat('machine_head_shape_max_y')
        return min(x_min, x_max), min(y_min, y_max)

    def getExportExtension(self):
        return 'gcode'
