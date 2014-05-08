
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
            progress = struct.unpack('@f', data[4:8])[0]
            print 'Progress:', progress
        else:
            print 'Unhandled engine message:', len(data)

    def canTranslate(self):
        return len(self._scene.getObjects()) > 0

    def getCommandParameters(self):
        return ['-v', '--command-socket']

    def getEngineSettings(self):
        vbk = self._machine.getSettingValueByKey
        fbk = self._machine.getSettingValueByKeyFloat
        settings = {
            'layerThickness': int(fbk('layer_height') * 1000),
            'initialLayerThickness': int(fbk('layer_height_0') * 1000),
            'filamentDiameter': int(fbk('filament_diameter') * 1000),
            'filamentFlow': int(fbk('filament_flow')),
        }
        return settings
