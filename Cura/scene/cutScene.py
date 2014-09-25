
import os
import threading

from Cura.vectorLoaders import vectorLoader
from Cura.scene.scene import Scene
from Cura.scene.cuttableObject import CuttableObject


class CutResult(object):
    def __init__(self):
        self._gcode = None
        self._log = None
        self._default_filename = None
        self._cut_path_polygons = None

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

    def setCutPathPolygons(self, polygons):
        self._cut_path_polygons = polygons

    def getCutPathPolygons(self):
        return self._cut_path_polygons


class CutScene(Scene):
    def __init__(self):
        super(CutScene,self).__init__()
        self._result_object = CutResult()
        self._move_object_lock = threading.RLock()
        self._want_to_print_one_at_a_time = True
        self._print_one_at_a_time = True
        self._update_thread = None

    def loadFile(self, filename):
        if not os.path.isfile(filename):
            return None
        obj = CuttableObject(filename)
        obj.setScene(self)
        obj.loadVector(filename)
        self.addObject(obj)
        self.deselectAll()
        obj.setSelected(True)

    def getSupportedLoadExtensions(self):
        return vectorLoader.loadSupportedExtensions()

    def getResult(self):
        return self._result_object

    def clearResult(self):
        self._result_object = CutResult()
