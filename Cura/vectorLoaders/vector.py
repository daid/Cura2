import numpy


class Path(object):
    def __init__(self):
        self._points = []
        self.metaData = {}

    def addPoint(self, x, y):
        self._points.append([x, y])

    def getPoints(self):
        return self._points

    def isClosed(self):
        return self._points[0][0] == self._points[-1][0] and self._points[0][1] == self._points[-1][1]


class Vector(object):
    def __init__(self):
        self._paths = []
        self.metaData = {}

    def getPaths(self):
        return self._paths

    def addLine(self, x0, y0, x1, y1):
        if len(self._paths) > 0 and self._paths[-1]._points[-1][0] == x0 and self._paths[-1]._points[-1][1] == y0:
            self._paths[-1].addPoint(x1, y1)
        else:
            new_path = Path()
            new_path.addPoint(x0, y0)
            new_path.addPoint(x1, y1)
            self._paths.append(new_path)

    def _postProcessPaths(self):
        for p in self._paths:
            if abs(p._points[0][0] - p._points[-1][0]) < 0.01 and abs(p._points[0][1] - p._points[-1][1]) < 0.01:
                p._points[0][0] = p._points[-1][0]
                p._points[0][1] = p._points[-1][1]
        open_paths = []
        closed_paths = []
        for p in self._paths:
            if not p.isClosed():
                open_paths.append(p)
            else:
                closed_paths.append(p)

        while True:
            link = self._linkOpenPath(open_paths)
            if link is None:
                break
            if abs(link._points[0][0] - link._points[-1][0]) < 0.01 and abs(link._points[0][1] - link._points[-1][1]) < 0.01:
                link._points[0][0] = link._points[-1][0]
                link._points[0][1] = link._points[-1][1]
            if link.isClosed():
                open_paths.remove(link)
                closed_paths.append(link)

        self._paths = open_paths + closed_paths
        for p in self._paths:
            p._points = numpy.array(p._points, numpy.float32)

    def _linkOpenPath(self, open_paths):
        for n in xrange(0, len(open_paths)):
            for m in xrange(n + 1, len(open_paths)):
                p0 = open_paths[n]
                p1 = open_paths[m]
                if abs(p1._points[0][0] - p0._points[-1][0]) < 0.01 and abs(p1._points[0][1] - p0._points[-1][1]) < 0.01:
                    p0._points += p1._points
                    open_paths.remove(p1)
                    return p0
                if abs(p0._points[0][0] - p1._points[-1][0]) < 0.01 and abs(p0._points[0][1] - p1._points[-1][1]) < 0.01:
                    p1._points += p0._points
                    open_paths.remove(p0)
                    return p1
                if abs(p0._points[0][0] - p1._points[0][0]) < 0.01 and abs(p0._points[0][1] - p1._points[0][1]) < 0.01:
                    p0._points = p1._points[::-1] + p0._points
                    open_paths.remove(p1)
                    return p0
                if abs(p0._points[-1][0] - p1._points[-1][0]) < 0.01 and abs(p0._points[-1][1] - p1._points[-1][1]) < 0.01:
                    p0._points += p1._points[::-1]
                    open_paths.remove(p1)
                    return p0
        return None
