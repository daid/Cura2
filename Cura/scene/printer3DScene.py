
import os

from Cura.scene.scene import Scene
from Cura.scene.printableObject import PrintableObject


class Printer3DResult(object):
    def __init__(self):
        self._gcode = None
        self._log = None

    def getGCode(self):
        return self._gcode

    def setGCode(self, gcode):
        self._gcode = gcode

    def getLog(self):
        return self._log

    def setLog(self, log):
        self._log = log


class Printer3DScene(Scene):
    def __init__(self):
        super(Printer3DScene,self).__init__()
        self._result_object = Printer3DResult()

    def loadFile(self, filename):
        if not os.path.isfile(filename):
            return None
        obj = PrintableObject(filename)
        obj.loadMesh(filename)
        self.addObject(obj)
        self.deselectAll()
        obj.setSelected(True)

    def sceneUpdated(self, updatedObject=None):
        super(Printer3DScene, self).sceneUpdated(updatedObject)

    def getResult(self):
        return self._result_object
