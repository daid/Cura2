import os
import wx

_image_cache = {}
_mesh_cache = {}

from Cura.meshLoaders import meshLoader


def getResourcePath(subdir):
    return os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'resources', subdir))


def getBitmap(name):
    global _image_cache

    if name not in _image_cache:
        _image_cache[name] = wx.Bitmap(os.path.join(getResourcePath('images'), name))
    return _image_cache[name]


def getMesh(name):
    global _mesh_cache

    if name not in _mesh_cache:
        _mesh_cache[name] = meshLoader.loadMeshes(os.path.join(getResourcePath('meshes'), name))[-1]
    return _mesh_cache[name]
