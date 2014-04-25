"""
The meshLoader module contains a universal interface for loading 3D files.
Depending on the file extension the proper meshLoader is called to load the file.
"""
__copyright__ = "Copyright (C) 2013 David Braam - Released under terms of the AGPLv3 License"

import os

from Cura.meshLoaders import stl
from Cura.meshLoaders import obj
from Cura.meshLoaders import dae
from Cura.meshLoaders import amf


def loadSupportedExtensions():
    """ return a list of supported file extensions for loading. """
    return ['.stl', '.obj', '.dae', '.amf']


def saveSupportedExtensions():
    """ return a list of supported file extensions for saving. """
    return ['.amf', '.stl']


def loadMeshes(filename):
    """
    Loads mesh from file. Only the first found mesh is returned.
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext == '.stl':
        return stl.loadMeshes(filename)
    if ext == '.obj':
        return obj.loadMeshes(filename)
    if ext == '.dae':
        return dae.loadMeshes(filename)
    if ext == '.amf':
        return amf.loadMeshes(filename)
    print 'Error: Unknown model extension: %s' % (ext)
    return []


def saveMeshes(filename, objects):
    """
    Save a list of objects into the file given by the filename. Use the filename extension to find out the file format.
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext == '.stl':
        stl.saveScene(filename, objects)
        return
    if ext == '.amf':
        amf.saveScene(filename, objects)
        return
    print 'Error: Unknown model extension: %s' % (ext)
