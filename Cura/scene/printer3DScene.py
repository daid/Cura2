
import wx
import os
import numpy

from Cura.geometry import polygon
from Cura.scene.scene import Scene
from Cura.scene.printableObject import PrintableObject


class Printer3DResult(object):
    def __init__(self):
        self._gcode = None
        self._log = None
        self._default_filename = None

    def getGCode(self):
        return self._gcode

    def setGCode(self, gcode):
        self._gcode = gcode

    def getLog(self):
        return self._log

    def setLog(self, log):
        self._log = log

    def setDefaultFilename(self, filename):
        self._default_filename = filename

    def getDefaultFilename(self):
        return self._default_filename


class Printer3DScene(Scene):
    def __init__(self):
        super(Printer3DScene,self).__init__()
        self._result_object = Printer3DResult()
        self._is_in_update = False
        self._want_to_print_one_at_a_time = True
        self._print_one_at_a_time = True
        self._update_thread = None

    def loadFile(self, filename):
        if not os.path.isfile(filename):
            return None
        obj = PrintableObject(filename)
        obj.setScene(self)
        obj.loadMesh(filename)
        self.addObject(obj)
        self.deselectAll()
        obj.setSelected(True)

    def sceneUpdated(self, updatedObject=None):
        super(Printer3DScene, self).sceneUpdated(updatedObject)

        self._print_one_at_a_time = self._want_to_print_one_at_a_time
        if self._print_one_at_a_time:
            cnt = 0
            for obj in self._object_list:
                if not self.checkPlatform(obj):
                    continue
                cnt += 1
                if obj.getSize()[2] >= self._machine.getSettingValueByKeyFloat('machine_nozzle_gantry_distance'):
                    self._print_one_at_a_time = False
                    break
            if cnt < 2:
                self._print_one_at_a_time = False

        if updatedObject is not None and self.checkPlatform(updatedObject):
            self._is_in_update = True
            for obj in self._object_list:
                if obj == updatedObject or not self.checkPlatform(obj):
                    continue
                if self._print_one_at_a_time:
                    v = polygon.polygonCollisionPushVector(obj.getHeadHitShapeMin(), updatedObject.getObjectBoundary())
                    if type(v) is bool:
                        v = polygon.polygonCollisionPushVector(updatedObject.getHeadHitShapeMin(), obj.getObjectBoundary())
                        if type(v) is bool:
                            continue
                        v = -v
                else:
                    v = polygon.polygonCollisionPushVector(obj.getObjectBoundary(), updatedObject.getObjectBoundary())
                    if type(v) is bool:
                        continue
                posDiff = obj.getPosition() - updatedObject.getPosition()
                if numpy.dot(posDiff, v) < 0:
                    v = -v
                wx.CallAfter(obj.setPosition, obj.getPosition() + v * 1.01)
            self._is_in_update = False

    def getOneAtATimeActive(self):
        return self._print_one_at_a_time

    def getResult(self):
        return self._result_object

    def clearResult(self):
        self._result_object = Printer3DResult()

    def checkPlatform(self, obj):
        area = obj.getObjectBoundary()
        if self._machine is None:
            return False
        if obj.getSize()[2] > self._machine.getSettingValueByKeyFloat('machine_height'):
            return False
        if not polygon.fullInside(area, self._machine.getShape()):
            return False
        #Check the "no go zones"
        for poly in self._machine.getDisallowedZones():
            if polygon.polygonCollision(poly, area):
                return False
        return True
