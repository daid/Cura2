__author__ = 'Jaime van Kessel'

import os

from Cura.scene.scene import Scene
from Cura.scene.printableObject import PrintableObject

class Printer3DScene(Scene):
    def __init__(self):
        super(Printer3DScene,self).__init__()

    def loadFile(self, filename):
        if not os.path.isfile(filename):
            return None
        obj = PrintableObject(filename)
        obj.loadMesh(filename)
        self.addObject(obj)
