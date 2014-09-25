
import platform
import os
import struct
import numpy

from Cura.localization import formatTime
from Cura.localization import formatMaterial
from Cura.geometry import polygon
from Cura.machine.translator.translator import Translator
from Cura.machine.engineCommunication.socketConnection import SocketConnection


class CutTranslator(Translator):
    def __init__(self):
        super(CutTranslator, self).__init__()
        self._engine_executable_name = 'CuraCutEngine'

        self.addConnection(SocketConnection(self))

    def findExecutable(self):
        """ Hack to ease development. """
        if platform.system() == 'Windows':
            if os.path.exists('C:/Software/Cura_CutEngine/_bin/Debug/Cura_CutEngine.exe'):
                return 'C:/Software/Cura_CutEngine/_bin/Debug/Cura_CutEngine.exe'
            if os.path.exists('C:/Software/Cura_CutEngine/_bin/Release/Cura_CutEngine.exe'):
                return 'C:/Software/Cura_CutEngine/_bin/Release/Cura_CutEngine.exe'
        return super(CutTranslator, self).findExecutable()

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

    def communicate(self):
        main_settings = self.getEngineSettings()
        for k, v in main_settings.items():
            self.sendData(self.CMD_SETTING, str(k) + '\x00' + str(v))

        self._objects = self._scene.getObjects()
        for obj in self._objects:
            obj.clearInfo()
            self._cut_path_polygons.append([])

        self.sendData(self.CMD_OBJECT_COUNT, struct.pack("@i", len(self._scene.getObjects())))
        for obj in self._objects:
            vector = obj.getVector()
            self.sendData(self.CMD_OBJECT_LIST, struct.pack("@i", len(vector.getPaths())))
            pos = obj.getPosition().copy()
            pos[0] += self._machine.getSettingValueByKeyFloat('machine_width') / 2
            pos[1] += self._machine.getSettingValueByKeyFloat('machine_depth') / 2
            self.sendData(self.CMD_SETTING, 'position.X\x00' + str(pos[0] * 1000))
            self.sendData(self.CMD_SETTING, 'position.Y\x00' + str(pos[1] * 1000))
            self.sendData(self.CMD_SETTING, 'position.Z\x000')
            self.sendData(self.CMD_MATRIX, obj.getMatrix().getA1().astype(numpy.float32).tostring())
            object_settings = self.getEngineSettings(obj)
            for k, v in object_settings.items():
                if main_settings[k] != v:
                    self.sendData(self.CMD_SETTING, str(k) + '\x00' + str(v))
            for path in vector.getPaths():
                if path.isClosed():
                    self.sendData(self.CMD_MESH_LIST, struct.pack("@i", 1))
                    self.sendData(self.CMD_VERTEX_LIST, path.getPoints().tostring())
        self.sendData(self.CMD_PROCESS)

    def receivedData(self, command_nr, data):
        if command_nr == self.CMD_PROGRESS_UPDATE:
            self.progressUpdate(struct.unpack('@f', data)[0], False)
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
            self._cut_path_polygons[object_index] += polygons
        else:
            print 'Unhandled engine message:', hex(command_nr), len(data)

    def canTranslate(self):
        count = 0
        for obj in self._scene.getObjects():
            count += 1
            if obj.getMesh() is None and obj.getVector() is None:
                return False
        return count > 0

    def preSetup(self):
        self.progressUpdate(0.0, False)
        self._cut_path_polygons = []
        self._scene.clearResult()

    def setup(self):
        names = {}
        for obj in self._scene.getObjects():
            name = None
            if obj.getMesh() and 'filename' in obj.getMesh().metaData:
                name = obj.getMesh().metaData['filename']
            if obj.getVector() and 'filename' in obj.getVector().metaData:
                name = obj.getMesh().metaData['filename']
            if name is not None:
                name = os.path.splitext(os.path.basename(name))[0]
                if not name in names:
                    names[name] = 1
                else:
                    names[name] += 1
        default_filename = ""
        for name, count in names.items():
            if count == 1:
                default_filename += '%s ' % (name)
            else:
                default_filename += '%dx %s ' % (count, name)
        self._scene.getResult().setDefaultFilename('%s.%s' % (default_filename.strip(), self._machine.getExportExtension()))

    def finish(self, success):
        result = self._result_output.getvalue()
        self._scene.getResult().setLog(self._result_log.getvalue())
        self._scene.getResult().setGCode(result)
        self._scene.getResult().setCutPathPolygons(self._cut_path_polygons)
        if success:
            self.progressUpdate(1.0, True)
        else:
            self.progressUpdate(0.0, False)

    def getCommandParameters(self):
        return ['-v', '--command-socket']

    def _getSettingValue(self, key):
        return self._machine.getSettingValueByKey(key)

    def _convertToFloat(self, value):
        try:
            value = value.replace(',', '.')
            return float(eval(value, {}, {}))
        except:
            return 0.0

    def getEngineSettings(self, obj=None, volume=None):
        vbk = self._getSettingValue
        fbk = lambda k: self._convertToFloat(vbk(k))

        settings = {}

        settings['startCode'] = vbk('machine_start_gcode')
        settings['endCode'] = vbk('machine_end_gcode')

        return settings
