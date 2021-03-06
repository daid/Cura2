"""
STL file mesh loader.
STL is the most common file format used for 3D printing right now.
STLs come in 2 flavors.
    Binary, which is easy and quick to read.
    Ascii, which is harder to read, as can come with windows, mac and unix style newlines.
    The ascii reader has been designed so it has great compatibility with all kinds of formats or slightly broken exports from tools.

This module also contains a function to save objects as an STL file.

http://en.wikipedia.org/wiki/STL_(file_format)
"""
__copyright__ = "Copyright (C) 2013 David Braam - Released under terms of the AGPLv3 License"

import sys
import os
import struct
import time

from Cura.mesh.mesh import Mesh

# import ctypes
# import numpy
#
# STLLoaderDll = ctypes.CDLL('C:/Software/Cura2/dll/STLLoader/.bin/Release/STLLoader.dll')
# openFile = STLLoaderDll.openFile
# openFile.argtypes = [ctypes.c_char_p]
# openFile.restype = ctypes.c_void_p
# getMeshCount = STLLoaderDll.getMeshCount
# getMeshCount.argtypes = [ctypes.c_void_p]
# getMeshCount.restype = ctypes.c_int
# getVolumeCount = STLLoaderDll.getVolumeCount
# getVolumeCount.argtypes = [ctypes.c_void_p, ctypes.c_int]
# getVolumeCount.restype = ctypes.c_int
# getVertexCount = STLLoaderDll.getVertexCount
# getVertexCount.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
# getVertexCount.restype = ctypes.c_int
# storeVertexData = STLLoaderDll.storeVertexData
# storeVertexData.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_void_p]
# storeVertexData.restype = ctypes.c_int
# closeFile = STLLoaderDll.closeFile
# closeFile.argtypes = [ctypes.c_void_p]
# closeFile.restype = None
#
# import time
# t = time.time()
# res = openFile('C:/Models/Knot-Thing.stl')
# print getMeshCount(res)
# print getVolumeCount(res, 0)
# print getVertexCount(res, 0, 0)
# vertexData = numpy.zeros((getVertexCount(res, 0, 0), 6), numpy.float32)
# storeVertexData(res, 0, 0, vertexData.ctypes)
# print vertexData
# closeFile(res)
# print time.time() - t

def _loadAscii(volume, f):
    cnt = 0
    for lines in f:
        for line in lines.split('\r'):
            if 'vertex' in line:
                cnt += 1
    volume._prepareFaceCount(int(cnt) / 3)
    f.seek(5, os.SEEK_SET)
    cnt = 0
    data = [None,None,None]
    for lines in f:
        for line in lines.split('\r'):
            if 'vertex' in line:
                data[cnt] = line.split()[1:]
                cnt += 1
                if cnt == 3:
                    volume._addFace(float(data[0][0]), float(data[0][1]), float(data[0][2]), float(data[1][0]), float(data[1][1]), float(data[1][2]), float(data[2][0]), float(data[2][1]), float(data[2][2]))
                    cnt = 0


def _loadBinary(volume, f):
    #Skip the header
    f.read(80-5)
    faceCount = struct.unpack('<I', f.read(4))[0]
    volume._prepareFaceCount(faceCount)
    for idx in xrange(0, faceCount):
        data = struct.unpack("<ffffffffffffH", f.read(50))
        volume._addFace(data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11])


def loadMeshes(filename):
    mesh = Mesh()
    mesh.metaData['filename'] = filename
    volume = mesh.newVolume()

    f = open(filename, "rb")
    if f.read(5).lower() == "solid":
        _loadAscii(volume, f)
        if volume.vertexCount < 3:
            f.seek(5, os.SEEK_SET)
            _loadBinary(volume, f)
    else:
        _loadBinary(volume, f)
    f.close()
    volume.calculateNormals()
    return [mesh]


def saveScene(filename, meshes):
    f = open(filename, 'wb')
    saveSceneStream(f, meshes)
    f.close()


def saveSceneStream(stream, meshes):
    #Write the STL binary header. This can contain any info, except for "SOLID" at the start.
    stream.write(("CURA BINARY STL EXPORT. " + time.strftime('%a %d %b %Y %H:%M:%S')).ljust(80, '\000'))

    vertexCount = 0
    for mesh in meshes:
        for volume in mesh.getVolumes():
            vertexCount += volume.vertexCount

    #Next follow 4 binary bytes containing the amount of faces, and then the face information.
    stream.write(struct.pack("<I", int(vertexCount / 3)))
    for mesh in meshes:
        for volume in mesh.getVolumes():
            vertexes = m.getTransformedVertexes(True)
            for idx in xrange(0, volume.vertexCount, 3):
                v1 = vertexes[idx]
                v2 = vertexes[idx+1]
                v3 = vertexes[idx+2]
                stream.write(struct.pack("<fff", 0.0, 0.0, 0.0))
                stream.write(struct.pack("<fff", v1[0], v1[1], v1[2]))
                stream.write(struct.pack("<fff", v2[0], v2[1], v2[2]))
                stream.write(struct.pack("<fff", v3[0], v3[1], v3[2]))
                stream.write(struct.pack("<H", 0))
