import numpy
from Cura.geometry.ray import Ray


class Plane(object):
    def __init__(self, normal=None, distance=None, a=None, b=None, c=None):
        # a,b,c = [x,y,z],[x,y,z],[x,y,z]
        # normal,distance = [x,y,z],d
        # normal,a = [x,y,z],[x,y,z]
        if a is not None and b is not None and c is not None:
            normal = numpy.cross(b - a, c - a)
            normal /= numpy.linalg.norm(normal)
            distance = numpy.dot(normal, a)
        if distance is None:
            if a is None:
                distance = 0
            else:
                distance = numpy.dot(normal, a)
        assert isinstance(normal, numpy.ndarray)
        self.normal = normal
        self.distance = distance

    def flip(self):
        self.normal *= -1
        self.distance *= -1

    def pointOnPlane(self, point):
        return self.intersectRay(Ray(point, self.normal))

    def intersectRay(self, ray):
        assert isinstance(ray, Ray)
        normalDotOrigin = numpy.dot(self.normal, ray.origin)
        normalDotDirection = numpy.dot(self.normal, ray.direction)
        return ray.origin + (((self.distance - normalDotOrigin)/normalDotDirection) * ray.direction)

    def intersectPlane(self, plane):
        lineDir = numpy.cross(self.normal, plane.getNormal())
        v = lineDir.cross(self.normal)
        v /= numpy.linalg.norm(v)
        lineOrigin = plane.intersectWithLine(Ray(self.normal * self.distance, v))
        lineDir /= numpy.linalg.norm(lineDir)
        return Ray(lineOrigin, lineDir)
