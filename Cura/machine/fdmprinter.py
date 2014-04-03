__author__ = 'Jaime van Kessel'

from Cura.machine import printer3D
import numpy

class FDMPrinter(printer3D.Printer3D):
    """
    Class that holds settings for any kind of FDMPrinter
    """
    def __init__(self):
        super(FDMPrinter,self).__init__()

        size = self.getSize()
        ret = numpy.array([[-size[0]/2,-size[1]/2],[size[0]/2,-size[1]/2],[size[0]/2, size[1]/2], [-size[0]/2, size[1]/2]], numpy.float32)
        self._machine_shape = ret
