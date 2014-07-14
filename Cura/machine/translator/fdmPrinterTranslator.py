
import platform
import os
import struct
import numpy

from Cura.localization import formatTime
from Cura.localization import formatMaterial
from Cura.geometry import polygon
from Cura.machine.translator.printer3DTranslator import Printer3DTranslator
from Cura.machine.engineCommunication.socketConnection import SocketConnection


class FDMPrinterTranslator(Printer3DTranslator):
    def __init__(self):
        super(FDMPrinterTranslator, self).__init__()
        self._engine_executable_name = 'CuraEngine'
        self._object_index_mapping = None   # Mapping from indexes reported by the engine to objects on the build-plate.

        self.addConnection(SocketConnection(self))

    def findExecutable(self):
        """ Hack to ease development. """
        if platform.system() == 'Windows':
            if os.path.exists('C:/Software/Cura_SteamEngine/_bin/Release/Cura_SteamEngine.exe'):
                return 'C:/Software/Cura_SteamEngine/_bin/Release/Cura_SteamEngine.exe'
        return super(FDMPrinterTranslator, self).findExecutable()

    CMD_SETTING = 0x00100004
    CMD_MATRIX = 0x00300002
    CMD_PROCESS = 0x00300000
    CMD_OBJECT_COUNT = 0x00300003
    CMD_OBJECT_LIST = 0x00200000
    CMD_MESH_LIST = 0x00200001
    CMD_VERTEX_LIST = 0x00200002
    CMD_NORMAL_LIST = 0x00200003
    CMD_INDEX_LIST = 0x00200004

    CMD_PROGRESS_UPDATE = 0x00300001
    CMD_OBJECT_PRINT_TIME = 0x00300004
    CMD_OBJECT_PRINT_MATERIAL = 0x00300005
    CMD_LAYER_INFO = 0x00300007
    CMD_POLYGON = 0x00300006

    def _findPrintOrder(self):
        #Construct a hit map, where object_hit_map[n][m] == True says when printing object N the head will hit object M
        object_list = self._scene.getObjects()
        use_list = [False] * len(object_list)
        object_hit_map = [[]] * len(object_list)
        for n in xrange(0, len(object_list)):
            object_hit_map[n] = [False] * len(object_list)
            use_list[n] = self._scene.checkPlatform(object_list[n])
        for n in xrange(0, len(object_list)):
            if use_list[n]:
                for m in xrange(0, len(object_list)):
                    if n == m or not use_list[m]:
                        object_hit_map[n][m] = False
                    else:
                        object_hit_map[n][m] = polygon.polygonCollision(object_list[n].getHeadHitShape(), object_list[m].getObjectBoundary())

        for n in xrange(0, len(object_list)):
            for m in xrange(0, len(object_list)):
                if n != m and use_list[n] and use_list[m] and object_hit_map[n][m] and object_hit_map[m][n]:
                    return False

        #Generate a list of which indexes we all need to print and sort in a proper print order.
        index_list = []
        for n in xrange(0, len(object_list)):
            if use_list[n]:
                index_list.append(n)

        #Sort from least to most hit objects.
        index_list.sort(lambda a, b: sum(object_hit_map[a]) - sum(object_hit_map[b]))

        todo_list = [([], index_list)]
        while len(todo_list) > 0:
            done_list, index_list = todo_list.pop()
            for add_index in index_list:
                can_add = True
                #Check if this to-add object does not hit an already placed object.
                for idx in done_list:
                    if object_hit_map[add_index][idx]:
                        can_add = False
                        break
                if not can_add:
                    continue
                #Check if this to-add object does not block the placing of a later object.
                for idx in index_list:
                    if add_index != idx and object_hit_map[idx][add_index]:
                        can_add = False
                        break
                if not can_add:
                    continue

                if len(index_list) == 1:
                    #We are done, all items added. Return the order we found
                    return done_list + [add_index]

                #Add this option to the todo_list so it gets evaluated deeper.
                new_index_list = index_list[:]
                new_index_list.remove(add_index)
                todo_list.append((done_list + [add_index], new_index_list))
        return False

    def communicate(self):
        for k, v in self.getEngineSettings().items():
            self.sendData(self.CMD_SETTING, str(k) + '\x00' + str(v))
        one_at_a_time = self._scene.getOneAtATimeActive()
        if one_at_a_time:
            ## Find out printing order
            order = self._findPrintOrder()

        for obj in self._scene.getObjects():
            obj.clearInfo()
        self._object_index_mapping = None

        if one_at_a_time and order:
            self._object_index_mapping = []
            for idx in order:
                self._object_index_mapping.append(self._scene.getObjects()[idx])
                self._scene.getObjects()[idx].setInfo('Order', '%d' % (order.index(idx) + 1))
            ## Print objects in that order
            self.sendData(self.CMD_OBJECT_COUNT, struct.pack("@i", len(order)))
            for idx in order:
                obj = self._scene.getObjects()[idx]
                pos = obj.getPosition().copy()
                if self._machine.getSettingValueByKey('machine_center_is_zero') == 'False':
                    pos[0] += self._machine.getSettingValueByKeyFloat('machine_width') / 2
                    pos[1] += self._machine.getSettingValueByKeyFloat('machine_depth') / 2
                self.sendData(self.CMD_SETTING, 'posx\x00' + str(pos[0] * 1000))
                self.sendData(self.CMD_SETTING, 'posy\x00' + str(pos[1] * 1000))
                self.sendData(self.CMD_MATRIX, obj.getMatrix().getA1().astype(numpy.float32).tostring())
                mesh = obj.getMesh()
                self.sendData(self.CMD_OBJECT_LIST, struct.pack("@i", len(mesh.getVolumes())))
                for volume in mesh.getVolumes():
                    self.sendData(self.CMD_MESH_LIST, struct.pack("@i", 1))
                    self.sendData(self.CMD_VERTEX_LIST, volume.getVertexPositionData().tostring())
                    # self.sendData(self.CMD_NORMAL_LIST, volume.getVertexNormalData().tostring())
                self.sendData(self.CMD_PROCESS)
        else:
            self.sendData(self.CMD_OBJECT_COUNT, struct.pack("@i", 1))
            mesh_count = 0
            for obj in self._scene.getObjects():
                if not self._scene.checkPlatform(obj):
                    continue
                mesh_count += len(obj.getMesh().getVolumes())
            self.sendData(self.CMD_OBJECT_LIST, struct.pack("@i", mesh_count))
            for obj in self._scene.getObjects():
                if not self._scene.checkPlatform(obj):
                    continue
                self.sendData(self.CMD_SETTING, 'posx\x00' + str(obj.getPosition()[0] * 1000))
                self.sendData(self.CMD_SETTING, 'posy\x00' + str(obj.getPosition()[1] * 1000))
                self.sendData(self.CMD_MATRIX, obj.getMatrix().getA1().astype(numpy.float32).tostring())
                for volume in obj.getMesh().getVolumes():
                    self.sendData(self.CMD_MESH_LIST, struct.pack("@i", 1))
                    self.sendData(self.CMD_VERTEX_LIST, volume.getVertexPositionData().tostring())
                    # self.sendData(self.CMD_NORMAL_LIST + volume.getVertexNormalData().tostring())
            if self._machine.getSettingValueByKey('machine_center_is_zero') == 'True':
                self.sendData(self.CMD_SETTING, 'posx\x000')
                self.sendData(self.CMD_SETTING, 'posy\x000')
            else:
                self.sendData(self.CMD_SETTING, 'posx\x00' + str(self._machine.getSettingValueByKeyFloat('machine_width') / 2 * 1000))
                self.sendData(self.CMD_SETTING, 'posy\x00' + str(self._machine.getSettingValueByKeyFloat('machine_depth') / 2 * 1000))
            self.sendData(self.CMD_PROCESS)

    def receivedData(self, command_nr, data):
        if command_nr == self.CMD_PROGRESS_UPDATE:
            self.progressUpdate(struct.unpack('@f', data)[0], False)
        elif command_nr == self.CMD_OBJECT_PRINT_TIME:
            index, print_time = struct.unpack('@if', data)
            if self._object_index_mapping is not None:
                self._object_index_mapping[index].setInfo('Print time', formatTime(print_time))
            else:
                for obj in self._scene.getObjects():
                    obj.setInfo('Total print time', formatTime(print_time))
        elif command_nr == self.CMD_OBJECT_PRINT_MATERIAL:
            index, extruder_nr, material_amount = struct.unpack('@iif', data)
            if self._object_index_mapping is not None:
                self._object_index_mapping[index].setInfo('Material', formatMaterial(material_amount))
            else:
                for obj in self._scene.getObjects():
                    obj.setInfo('Total material', formatMaterial(material_amount))
        elif command_nr == self.CMD_LAYER_INFO:
            object_index, layer_nr, z_height, layer_height = struct.unpack("@iiii", data)
            z_height /= 1000.0
            layer_height /= 1000.0
            if self._object_index_mapping is not None:
                self._object_index_mapping[object_index].addToolpathLayer(layer_nr, z_height, layer_height)
            else:
                self._scene.getObjects()[0].addToolpathLayer(layer_nr, z_height, layer_height)
        elif command_nr == self.CMD_POLYGON:
            n = data.index('\x00')
            name = data[0:n]
            n += 1
            object_index, layer_nr, polygon_count = struct.unpack("@iii", data[n:n + 3 * 4])
            n += 3 * 4
            polygons = []
            for cnt in xrange(0, polygon_count):
                point_count = struct.unpack("@i", data[n:n + 4])[0]
                n += 4
                polygons.append(numpy.fromstring(data[n:n + 16 * point_count], numpy.int64).astype(numpy.float32).reshape((point_count, 2)) / 1000.0)
                n += 16 * point_count
            if self._object_index_mapping is not None:
                self._object_index_mapping[object_index].addToolpathPolygons(name, layer_nr, polygons)
            else:
                self._scene.getObjects()[0].addToolpathPolygons(name, layer_nr, polygons)
        else:
            print 'Unhandled engine message:', hex(command_nr), len(data)

    def canTranslate(self):
        if len(self._scene.getObjects()) < 1:
            return False
        for obj in self._scene.getObjects():
            if obj.getMesh() is None:
                return False
        return True

    def setup(self):
        self.progressUpdate(0.0, False)
        for obj in self._scene.getObjects():
            obj.updatePrintExtension()
        self._scene.clearResult()

    def finish(self, success):
        self._scene.getResult().setLog(self._result_log.getvalue())
        self._scene.getResult().setGCode(self._result_output.getvalue())
        if success:
            self.progressUpdate(1.0, True)
        else:
            self.progressUpdate(0.0, False)

    def getCommandParameters(self):
        return ['-v', '--command-socket']

    def getEngineSettings(self):
        vbk = self._machine.getSettingValueByKey
        fbk = self._machine.getSettingValueByKeyFloat
        settings = {
            'layerThickness': int(fbk('layer_height') * 1000),
            'initialLayerThickness': int(fbk('layer_height_0') * 1000),
            'filamentDiameter': int(fbk('material_diameter') * 1000),
            'filamentFlow': int(fbk('material_flow')),
            'layer0extrusionWidth': int(fbk('wall_line_width_0') * 1000),
            'extrusionWidth': int(fbk('wall_line_width_x') * 1000),
            'insetCount': int(fbk('wall_line_count')),
            'downSkinCount': int(fbk('bottom_layers')),
            'upSkinCount': int(fbk('top_layers')),
            'skirtDistance': int(fbk('skirt_gap') * 1000),
            'skirtLineCount': int(fbk('skirt_line_count')),
            'skirtMinLength': int(fbk('skirt_minimal_length') * 1000),

            'retractionAmount': int(fbk('retraction_amount') * 1000),
            # 'retractionAmountPrime': int(fbk('') * 1000),
            # 'retractionAmountExtruderSwitch': int(fbk('') * 1000),
            'retractionSpeed': int(fbk('retraction_speed')),
            'retractionMinimalDistance': int(fbk('retraction_min_travel') * 1000),
            'minimalExtrusionBeforeRetraction': int(fbk('retraction_minimal_extrusion') * 1000),
            'retractionZHop': int(fbk('retraction_hop') * 1000),

            'enableCombing': 1 if vbk('retraction_combing') == 'True' else 0,
            # 'enableOozeShield': int(fbk('') * 1000),
            # 'wipeTowerSize': int(fbk('') * 1000),
            # 'multiVolumeOverlap': int(fbk('') * 1000),

            'initialSpeedupLayers': int(fbk('speed_slowdown_layers')),
            'initialLayerSpeed': int(fbk('speed_layer_0')),
            'skirtSpeed': int(fbk('skirt_speed')),
            'inset0Speed': int(fbk('speed_wall_0')),
            'insetXSpeed': int(fbk('speed_wall_x')),
            'supportSpeed': int(fbk('speed_support')),
            'moveSpeed': int(fbk('speed_travel')),
            'fanFullOnLayerNr': int(fbk('cool_fan_full_layer')),

            'infillOverlap': int(fbk('fill_overlap')),
            'infillSpeed': int(fbk('speed_infill')),

            'minimalLayerTime': int(fbk('cool_min_layer_time')),
            'minimalFeedrate': int(fbk('cool_min_speed')),
            'coolHeadLift': 1 if vbk('cool_lift_head') == 'True' else 0,
            'fanSpeedMin': int(fbk('cool_fan_speed_min')),
            'fanSpeedMax': int(fbk('cool_fan_speed_max')),

            'spiralizeMode': 1 if vbk('magic_spiralize') == 'True' else 0,
        }

        if vbk('top_bottom_pattern') == 'lines':
            settings['skinPattern'] = 0
        elif vbk('top_bottom_pattern') == 'concentric':
            settings['skinPattern'] = 1

        if vbk('fill_pattern') == 'grid':
            settings['infillPattern'] = 0
        elif vbk('fill_pattern') == 'lines':
            settings['infillPattern'] = 1
        elif vbk('fill_pattern') == 'concentric':
            settings['infillPattern'] = 2

        if vbk('adhesion_type') == 'raft':
            settings['raftMargin'] = int(fbk('raft_margin') * 1000)
            settings['raftLineSpacing'] = int(fbk('raft_line_spacing') * 1000)
            settings['raftBaseThickness'] = int(fbk('raft_base_thickness') * 1000)
            settings['raftBaseLinewidth'] = int(fbk('raft_base_linewidth') * 1000)
            settings['raftBaseSpeed'] = int(fbk('raft_base_speed') * 1000)
            settings['raftInterfaceThickness'] = int(fbk('raft_interface_thickness') * 1000)
            settings['raftInterfaceLinewidth'] = int(fbk('raft_interface_linewidth') * 1000)
            settings['raftInterfaceLineSpacing'] = int(fbk('raft_line_spacing') * 1000)
            settings['raftFanSpeed'] = 0
            settings['raftSurfaceThickness'] = int(fbk('layer_height_0') * 1000)
            settings['raftSurfaceLinewidth'] = int(fbk('wall_line_width_x') * 1000)
            settings['raftSurfaceLineSpacing'] = int(fbk('wall_line_width_x') * 1000)
            settings['raftSurfaceLayers'] = int(fbk('raft_surface_layers'))
            settings['raftSurfaceSpeed'] = int(fbk('speed_layer_0') * 1000)
            settings['raftAirGap'] = int(fbk('raft_airgap') * 1000)
            settings['skirtLineCount'] = 0
        if vbk('adhesion_type') == 'brim':
            settings['skirtDistance'] = 0
            settings['skirtLineCount'] = int(fbk('brim_line_count'))
        if vbk('support_type') == '':
            settings['supportType'] = 0
            settings['supportAngle'] = -1
        else:
            settings['supportType'] = 0
            settings['supportAngle'] = int(fbk('support_angle'))
            settings['supportEverywhere'] = 1 if vbk('support_type') == 'everywhere' else 0
            settings['supportLineDistance'] = int(100 * fbk('wall_line_width_x') * 1000 / fbk('support_fill_rate')),
            settings['supportXYDistance'] = int(fbk('support_xy_distance') * 1000)
            settings['supportZDistance'] = int(fbk('support_z_distance') * 1000)
            settings['supportExtruder'] = -1
            if vbk('support_pattern') == 'grid':
                settings['supportType'] = 0
            elif vbk('support_pattern') == 'lines':
                settings['supportType'] = 1

        settings['sparseInfillLineDistance'] = -1
        if fbk('fill_sparse_density') >= 100:
            settings['sparseInfillLineDistance'] = fbk('wall_line_width_x')
            settings['downSkinCount'] = 10000
            settings['upSkinCount'] = 10000
        elif fbk('fill_sparse_density') > 0:
            settings['sparseInfillLineDistance'] = int(100 * fbk('wall_line_width_x') * 1000 / fbk('fill_sparse_density'))

        return settings
