
class Nurbs(object):
    def __init__(self, degree):
        self._degree = degree
        self._control_points = []
        self._knots = []
        self._weights = []

    def addControlPoint(self, x, y):
        self._control_points.append(complex(x, y))

    def addKnot(self, knot):
        self._knots.append(knot)

    def addWeight(self, weight):
        self._weights.append(weight)

    def _f(self, i, n, u):
        denom = self._knots[i+n] - self._knots[i]
        if denom == 0.0:
            return 0.0
        return (u - self._knots[i]) / denom

    def _g(self, i, n, u):
        denom = self._knots[i+n+1] - self._knots[i]
        if denom == 0.0:
            return 0.0
        return (self._knots[i+n+1] - u) / denom

    def _N(self, i, n, u):
        if n == 0:
            if self._knots[i] <= u <= self._knots[i+1]:
                return 1.0
            return 0.0
        else:
            Nin1u = self._N(i, n-1, u)
            Ni1n1u = self._N(i+1, n-1, u)
            if Nin1u == 0.0:
                a = 0.0
            else:
                a = self._f(i, n, u) * Nin1u
            if Ni1n1u == 0.0:
                b = 0.0
            else:
                b = self._g(i, n, u) * Ni1n1u
            return a + b

    def getPoints(self, point_count):
        point_count = max(point_count, 2)
        ret = []
        if len(self._weights) < 1:
            self._weights = [1.0] * len(self._control_points)
        for point_nr in xrange(0, point_count+1):
            u = self._knots[0] + (self._knots[-1] - self._knots[0]) / float(point_count) * point_nr
            C_u = complex(0, 0)
            Nku = []
            for n in xrange(0, len(self._control_points)):
                Nku.append(self._weights[n] * self._N(n, self._degree, u))
            denom = sum(Nku)
            for n in xrange(0, len(self._control_points)):
                if Nku[n] != 0.0 and denom != 0.0:
                    R_iku = Nku[n] / denom
                    if R_iku != 0.0:
                        C_u += self._control_points[n] * R_iku
            ret.append([C_u.real, C_u.imag])
        return ret
