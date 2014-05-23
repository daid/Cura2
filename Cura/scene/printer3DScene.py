
import os
import numpy

from Cura.geometry import polygon
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

        for obj in self._object_list:
            if obj == updatedObject:
                continue
            v0 = polygon.polygonCollisionPushVector(obj._convex2dBoundary + obj.getPosition(), updatedObject._convex2dBoundary + updatedObject.getPosition())
            v1 = polygon.polygonCollisionPushVector(updatedObject._convex2dBoundary + updatedObject.getPosition(), obj._convex2dBoundary + obj.getPosition())
            if type(v0) is bool or type(v1) is bool:
                continue
            if numpy.linalg.norm(v0) < numpy.linalg.norm(v1):
                obj.setPosition(obj.getPosition() + v0 * 1.01)
            else:
                obj.setPosition(obj.getPosition() + v1 * -1.01)

    def getResult(self):
        return self._result_object
