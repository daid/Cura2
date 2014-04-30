"""
OBJ file reader.
OBJ are wavefront object files. These are quite common and can be exported from a lot of 3D tools.
Only vertex information is read from the OBJ file, information about textures and normals is ignored.

http://en.wikipedia.org/wiki/Wavefront_.obj_file
"""
__copyright__ = "Copyright (C) 2013 David Braam - Released under terms of the AGPLv3 License"

from Cura.mesh.mesh import Mesh


def loadMeshes(filename):
    mesh = Mesh()
    mesh.metaData['filename'] = filename
    volume = mesh.newVolume()

    vertexList = []
    normalList = []
    faceList = []

    f = open(filename, "r")
    for line in f:
        parts = line.split()
        if len(parts) < 1:
            continue
        if parts[0] == 'v':
            vertexList.append([float(parts[1]), -float(parts[3]), float(parts[2])])
        if parts[0] == 'vn':
            normalList.append([float(parts[1]), -float(parts[3]), float(parts[2])])
        if parts[0] == 'f':
            parts = map(lambda p: p.split('/'), parts)
            for idx in xrange(1, len(parts)-2):
                data = [int(parts[1][0]), int(parts[idx+1][0]), int(parts[idx+2][0])]
                if len(parts[1]) > 2:
                    data += [int(parts[1][2]), int(parts[idx+1][2]), int(parts[idx+2][2])]
                faceList.append(data)
    f.close()

    volume._prepareFaceCount(len(faceList))
    for f in faceList:
        i = f[0] - 1
        j = f[1] - 1
        k = f[2] - 1
        if i < 0 or i >= len(vertexList):
            i = 0
        if j < 0 or j >= len(vertexList):
            j = 0
        if k < 0 or k >= len(vertexList):
            k = 0
        volume._addFace(vertexList[i][0], vertexList[i][1], vertexList[i][2], vertexList[j][0], vertexList[j][1], vertexList[j][2], vertexList[k][0], vertexList[k][1], vertexList[k][2])
    volume.calculateNormals()

    if len(normalList) > 0:
        n = 0
        for f in faceList:
            if len(f) > 3:
                i = f[3] - 1
                j = f[4] - 1
                k = f[5] - 1
                if i < 0 or i >= len(normalList):
                    i = 0
                if j < 0 or j >= len(normalList):
                    j = 0
                if k < 0 or k >= len(normalList):
                    k = 0
                volume.vertexData[n][3] = normalList[i][0]
                volume.vertexData[n][4] = normalList[i][1]
                volume.vertexData[n][5] = normalList[i][2]
                volume.vertexData[n+1][3] = normalList[j][0]
                volume.vertexData[n+1][4] = normalList[j][1]
                volume.vertexData[n+1][5] = normalList[j][2]
                volume.vertexData[n+2][3] = normalList[k][0]
                volume.vertexData[n+2][4] = normalList[k][1]
                volume.vertexData[n+2][5] = normalList[k][2]
            n += 3
    return [mesh]
