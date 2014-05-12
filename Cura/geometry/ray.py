import numpy
import math


class Ray(object):
    def __init__(self, origin, direction):
        self.origin = origin
        direction /= numpy.linalg.norm(direction)
        self.direction = direction

    def intersectWithRay(self, other):
        q12 = self.origin - other.origin
        v1_dot_v1 = numpy.dot(self.direction, self.direction)
        v2_dot_v2 = numpy.dot(other.direction, other.direction)
        v1_dot_v2 = numpy.dot(self.direction, other.direction)
        q12_dot_v1 = numpy.dot(q12, self.direction)
        q12_dot_v2 = numpy.dot(q12, other.direction)

        # Calculate scale factors.
        denom = v1_dot_v1 * v2_dot_v2 - v1_dot_v2 * v1_dot_v2
        s =  (v1_dot_v2 / denom) * q12_dot_v2 - (v2_dot_v2 / denom) * q12_dot_v1
        t = -(v1_dot_v2 / denom) * q12_dot_v1 + (v1_dot_v1 / denom) * q12_dot_v2
        return ((self.origin + s * self.direction) + (other.origin + t * other.direction)) / 2.0

    def rotatePoint(self, point, angle):
        return numpy.array(
            [(self.origin[0] * (self.direction[1] * self.direction[1] + self.direction[2] * self.direction[2]) - self.direction[0] * (self.origin[1] * self.direction[1] + self.origin[2] * self.direction[2] - self.direction[0] * point[0] - self.direction[1] * point[1] - self.direction[2] * point[2])) * (1. - cos(angle)) + point[0] * cos(angle) + (-self.origin[2] * self.direction[1] + self.origin[1] * self.direction[2] - self.direction[2] * point[1] + self.direction[1] * point[2]) * math.sin(angle)],
            [(self.origin[1] * (self.direction[0] * self.direction[0] + self.direction[2] * self.direction[2]) - self.direction[1] * (self.origin[0] * self.direction[0] + self.origin[2] * self.direction[2] - self.direction[0] * point[0] - self.direction[1] * point[1] - self.direction[2] * point[2])) * (1. - cos(angle)) + point[1] * cos(angle) + ( self.origin[2] * self.direction[0] - self.origin[0] * self.direction[2] + self.direction[2] * point[0] - self.direction[0] * point[2]) * math.sin(angle)],
            [(self.origin[2] * (self.direction[0] * self.direction[0] + self.direction[1] * self.direction[1]) - self.direction[2] * (self.origin[0] * self.direction[0] + self.origin[1] * self.direction[1] - self.direction[0] * point[0] - self.direction[1] * point[1] - self.direction[2] * point[2])) * (1. - cos(angle)) + point[2] * cos(angle) + (-self.origin[1] * self.direction[0] + self.origin[0] * self.direction[1] - self.direction[1] * point[0] + self.direction[0] * point[1]) * math.sin(angle)],
        numpy.float32)
