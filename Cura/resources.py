import os
import wx
import platform

_image_cache = {}
_mesh_cache = {}

from Cura.meshLoaders import meshLoader

## Functionality to handle standard paths and loading files

#
def getResourcePath(subdir):
    return os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'resources', subdir))

##  Load an image by name.
#
#   This will attempt to load the named image from the resources directory.
#
#   \param name The name of the image to load.
#
#   TODO: Get rid of globals and move to a proper class.
def getBitmap(name):
    global _image_cache

    if name not in _image_cache:
        full_filename = os.path.join(getResourcePath('images'), name)
        if os.path.isfile(full_filename):
            _image_cache[name] = wx.Bitmap(os.path.join(getResourcePath('images'), name))
        else:
            if name != '':
                print '%s not found' % (full_filename)
            _image_cache[name] = wx.EmptyBitmap(1, 1)
    return _image_cache[name]

##  Load a mesh by name.
#
#   This will attempt to load the named mesh from the resources directory.
#
#   \param name The name of the mesh to load.
#
#   TODO: Get rid of globals and move to a proper class.
def getMesh(name):
    global _mesh_cache

    if name not in _mesh_cache:
        full_filename = os.path.join(getResourcePath('meshes'), name)
        if os.path.isfile(full_filename):
            _mesh_cache[name] = meshLoader.loadMeshes(os.path.join(getResourcePath('meshes'), name))[-1]
        else:
            _mesh_cache[name] = None
    return _mesh_cache[name]

##  Return a default location to store preferences.
#   \param filename The name of the
#
#   TODO: Verify that this actually does the right thing.
def getDefaultPreferenceStoragePath(filename):
    base_path = os.path.dirname(__file__)
    base_path = os.path.abspath(os.path.join(base_path, '..'))
    if platform.system().startswith('Windows'):
        base_path = os.path.expanduser('~/.cura')
    try:
        os.makedirs(base_path)
    except:
        pass
    return os.path.join(base_path, filename)
