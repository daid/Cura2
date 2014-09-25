__copyright__ = "Copyright (C) 2013 David Braam - Released under terms of the AGPLv3 License"

import math

from Cura.geometry.nurbs import Nurbs
from Cura.vectorLoaders.vector import Vector


class DXF(Vector):
    def __init__(self, filename):
        super(DXF, self).__init__()
        self._resolution = 1.0

        self._last_polyline_point = None
        self._blocks = {}
        self._active_block = None

        entityType = 'NONE'
        sectionName = 'NONE'
        activeObject = None
        f = open(filename, "r")
        while True:
            groupCode = f.readline().strip()
            if groupCode == '':
                break
            groupCode = int(groupCode)
            value = f.readline().strip()
            if groupCode == 0:
                if entityType == 'SECTION':
                    sectionName = activeObject[2][0]
                elif entityType == 'ENDSEC':
                    sectionName = 'NONE'
                elif sectionName == 'ENTITIES':
                    self._checkForNewPath(entityType, activeObject)
                elif sectionName == 'BLOCKS':
                    if entityType == 'BLOCK':
                        self._active_block = []
                        self._blocks[activeObject[2][0]] = self._active_block
                    elif entityType == 'ENDBLK':
                        self._active_block = None
                    else:
                        self._active_block.append((entityType, activeObject))
                elif activeObject is not None:
                    pass
                    # print sectionName, entityType, activeObject
                entityType = value
                activeObject = {}
            else:
                if groupCode in activeObject:
                    activeObject[groupCode].append(value)
                else:
                    activeObject[groupCode] = [value]
        f.close()

        self._last_polyline_point = None
        self._blocks = None
        self._active_block = None

        self._postProcessPaths()

    def _checkForNewPath(self, type, obj):
        if type == 'LINE':
            self.addLine(float(obj[10][0]), float(obj[20][0]), float(obj[11][0]), float(obj[21][0]))
        elif type == 'POLYLINE':
            self._last_polyline_point = None
        elif type == 'VERTEX':
            if self._last_polyline_point is not None:
                self.addLine(self._last_polyline_point[0], self._last_polyline_point[1], float(obj[10][0]), float(obj[20][0]))
            self._last_polyline_point = [float(obj[10][0]), float(obj[20][0])]
        elif type == 'SEQEND':
            pass    #end of POLYLINE
        elif type == 'LWPOLYLINE':
            for n in xrange(1, len(obj[10])):
                self.addLine(float(obj[10][n-1]), float(obj[20][n-1]), float(obj[10][n]), float(obj[20][n]))
        elif type == 'SPLINE':
            nurb = Nurbs(int(obj[71][0]))
            for idx in xrange(0, len(obj[10])):
                nurb.addControlPoint(float(obj[10][idx]), float(obj[20][idx]))
            for k in obj[40]:
                nurb.addKnot(float(k))
            points = nurb.getPoints(10)
            total_length = 0.0
            for n in xrange(1, len(points)):
                dx = points[n-1][0] - points[n][0]
                dy = points[n-1][1] - points[n][1]
                total_length += math.sqrt(dx*dx+dy*dy)
            points = nurb.getPoints(int(total_length / self._resolution))
            for n in xrange(1, len(points)):
                self.addLine(points[n-1][0], points[n-1][1], points[n][0], points[n][1])
        elif type == 'CIRCLE':
            cx = float(obj[10][0])
            cy = float(obj[20][0])
            r = float(obj[40][0])
            path_length = math.pi * 2 * r
            point_count = math.ceil(path_length / self._resolution)
            for n in xrange(0, int(point_count)):
                x0 = cx + math.cos(float(n) / point_count * math.pi * 2) * r
                y0 = cy + math.sin(float(n) / point_count * math.pi * 2) * r
                x1 = cx + math.cos(float(n+1) / point_count * math.pi * 2) * r
                y1 = cy + math.sin(float(n+1) / point_count * math.pi * 2) * r
                self.addLine(x0, y0, x1, y1)
        elif type == 'ELLIPSE':
            cx = float(obj[10][0])
            cy = float(obj[20][0])
            rx = float(obj[11][0])
            ry = float(obj[21][0])

            #TODO: Properly calculate the size of an ellipse
            path_length = math.pi * 2 * math.sqrt(rx*rx + ry*ry)
            point_count = math.ceil(path_length / self._resolution)
            for n in xrange(0, int(point_count)):
                x0 = cx + math.cos(float(n) / point_count * math.pi * 2) * rx
                y0 = cy + math.sin(float(n) / point_count * math.pi * 2) * ry
                x1 = cx + math.cos(float(n+1) / point_count * math.pi * 2) * rx
                y1 = cy + math.sin(float(n+1) / point_count * math.pi * 2) * ry
                self.addLine(x0, y0, x1, y1)
        elif type == 'ARC':
            cx = float(obj[10][0])
            cy = float(obj[20][0])
            r = float(obj[40][0])
            a0 = float(obj[50][0]) / 180.0 * math.pi
            a1 = float(obj[51][0]) / 180.0 * math.pi
            if a0 > a1:
                a1 += math.pi * 2
            a_diff = a1 - a0
            path_length = r * a_diff
            point_count = math.ceil(path_length / self._resolution)
            for n in xrange(0, int(point_count)):
                x0 = cx + math.cos(a0 + float(n) / point_count * a_diff) * r
                y0 = cy + math.sin(a0 + float(n) / point_count * a_diff) * r
                x1 = cx + math.cos(a0 + float(n+1) / point_count * a_diff) * r
                y1 = cy + math.sin(a0 + float(n+1) / point_count * a_diff) * r
                self.addLine(x0, y0, x1, y1)
        elif type == 'INSERT':
            for typeName, objInfo in block:
                self._checkForNewPath(typeName, objInfo)
        else:
            print 'Unknown Path Entity: ', type, obj
