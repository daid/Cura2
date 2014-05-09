
import platform
import os
import struct
import numpy

from Cura.machine.translator.printer3DTranslator import Printer3DTranslator
from Cura.machine.engineCommunication.socketConnection import SocketConnection


class FDMPrinterTranslator(Printer3DTranslator):
    def __init__(self, scene, machine):
        super(FDMPrinterTranslator, self).__init__(scene, machine)
        self._engine_executable_name = 'CuraEngine'

        self.addConnection(SocketConnection(self))

    def findExecutable(self):
        """ Hack to ease development. """
        if platform.system() == 'Windows':
            if os.path.exists('C:/Software/Cura_SteamEngine/_bin/Release/Cura_SteamEngine.exe'):
                return 'C:/Software/Cura_SteamEngine/_bin/Release/Cura_SteamEngine.exe'
        return super(FDMPrinterTranslator, self).findExecutable()

    CMD_SETTING = struct.pack('@i', 0x0001)
    CMD_MATRIX = struct.pack('@i', 0x0002)
    CMD_PROCESS = struct.pack('@i', 0x0003)
    CMD_START_MESH = struct.pack('@i', 0x1000)
    CMD_START_VOLUME = struct.pack('@i', 0x1001)
    CMD_VOLUME_VERTEX_POSITION = struct.pack('@i', 0x1002)
    CMD_VOLUME_VERTEX_NORMAL = struct.pack('@i', 0x1003)
    CMD_FINISHED = struct.pack('@i', 0x9000)

    CMD_PROGRESS_UPDATE = struct.pack('@i', 0x10000)

    def communicate(self):
        for k, v in self.getEngineSettings().items():
            self.sendData(self.CMD_SETTING + str(k) + '=' + str(v))
        self.sendData(self.CMD_START_MESH)
        for obj in self._scene.getObjects():
            self.sendData(self.CMD_SETTING + 'posx=' + str(obj.getPosition()[0]))
            self.sendData(self.CMD_SETTING + 'posy=' + str(obj.getPosition()[1]))
            self.sendData(self.CMD_MATRIX + obj.getMatrix().getA1().astype(numpy.float32).tostring())
            mesh = obj.getMesh()
            self.sendData(self.CMD_START_MESH)
            for volume in mesh.getVolumes():
                self.sendData(self.CMD_START_VOLUME)
                self.sendData(self.CMD_VOLUME_VERTEX_POSITION + volume.getVertexPositionData())
                # self.sendData(self.CMD_VOLUME_VERTEX_NORMAL + volume.getVertexNormalData())
            self.sendData(self.CMD_PROCESS)
        self.sendData(self.CMD_FINISHED)

    def receivedData(self, data):
        if data[0:4] == self.CMD_PROGRESS_UPDATE:
            self.progressUpdate(struct.unpack('@f', data[4:8])[0], False)
        else:
            print 'Unhandled engine message:', len(data)

    def canTranslate(self):
        if len(self._scene.getObjects()) < 1:
            return False
        for obj in self._scene.getObjects():
            if obj.getMesh() is None:
                return False
        return True

    def setup(self):
        self.progressUpdate(0.0, False)

    def finish(self, success):
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
            'infillPattern': int(0),

            'minimalLayerTime': int(fbk('cool_min_layer_time') * 1000),
            'minimalFeedrate': int(fbk('cool_min_speed')),
            'coolHeadLift': 1 if vbk('cool_lift_head') == 'True' else 0,
            'fanSpeedMin': int(fbk('cool_fan_speed_min')),
            'fanSpeedMax': int(fbk('cool_fan_speed_max')),

            'spiralizeMode': 1 if vbk('magic_spiralize') == 'True' else 0,
        }

        if vbk('adhesion_type') == 'raft':
            settings['raftMargin'] = int(fbk('raft_margin') * 1000)
            settings['raftLineSpacing'] = int(fbk('raft_line_spacing') * 1000)
            settings['raftBaseThickness'] = int(fbk('raft_base_thickness') * 1000)
            settings['raftBaseLinewidth'] = int(fbk('raft_base_linewidth') * 1000)
            settings['raftBaseSpeed'] = int(fbk('raft_base_speed') * 1000)
            settings['raftInterfaceThickness'] = int(fbk('raft_interface_thickness') * 1000)
            settings['raftInterfaceLinewidth'] = int(fbk('raft_interface_linewidth') * 1000)
            settings['raftInterfaceLineSpacing'] = int(fbk('') * 1000)
            settings['raftFanSpeed'] = int(fbk('') * 1000)
            settings['raftSurfaceThickness'] = int(fbk('') * 1000)
            settings['raftSurfaceLinewidth'] = int(fbk('') * 1000)
            settings['raftSurfaceLineSpacing'] = int(fbk('') * 1000)
            settings['raftSurfaceLayers'] = int(fbk('raft_surface_layers'))
            settings['raftSurfaceSpeed'] = int(fbk('') * 1000)
            settings['raftAirGap'] = int(fbk('raft_airgap') * 1000)
            settings['skirtLineCount'] = 0
        if vbk('adhesion_type') == 'brim':
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

        settings['sparseInfillLineDistance'] = -1
        if fbk('fill_sparse_density') >= 100:
            settings['sparseInfillLineDistance'] = fbk('wall_line_width_x')
            settings['downSkinCount'] = 10000
            settings['upSkinCount'] = 10000
        elif fbk('fill_sparse_density') > 0:
            settings['sparseInfillLineDistance'] = int(100 * fbk('wall_line_width_x') * 1000 / fbk('fill_sparse_density'))

        return settings
