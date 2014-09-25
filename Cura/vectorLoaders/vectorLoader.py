"""
The meshLoader module contains a universal interface for loading 2D vector files.
Depending on the file extension the proper vectorLoader is called to load the file.
"""
__copyright__ = "Copyright (C) 2013 David Braam - Released under terms of the AGPLv3 License"

import os

from Cura.vectorLoaders import dxf


def loadSupportedExtensions():
    """ return a list of supported file extensions for loading. """
    return ['.dxf']


def saveSupportedExtensions():
    """ return a list of supported file extensions for saving. """
    return []


def loadVector(filename):
    """
    Loads vectors from file.
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext == '.dxf':
        return dxf.DXF(filename)
    print 'Error: Unknown vector extension: %s' % (ext)
    return []


def saveVector(filename, objects):
    """
    Save a list of objects into the file given by the filename. Use the filename extension to find out the file format.
    """
    ext = os.path.splitext(filename)[1].lower()
    print 'Error: Unknown vector extension: %s' % (ext)
