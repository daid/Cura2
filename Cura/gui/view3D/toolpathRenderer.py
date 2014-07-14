import numpy
import re
import math
import threading
import time
from OpenGL.GL import *

from Cura.gui import openGLUtils
from Cura.gui.view3D.renderer import Renderer


class GCodeLayerRenderer(object):
    def __init__(self, prev_layer = None):
        self._x = 0
        self._y = 0
        self._z = 0
        self._e = 0
        self._last_extrusion_z = 0
        self._prev_last_extrusion_z = 0
        self._feedrate = 0
        self._retracted = False
        self._move_points = []
        self._inset0_extrude_points = []
        self._insetX_extrude_points = []
        self._infill_extrude_points = []
        self._support_extrude_points = []
        self._inset0_extrude_amounts = []
        self._insetX_extrude_amounts = []
        self._infill_extrude_amounts = []
        self._support_extrude_amounts = []

        self._retract_marks = []
        self._prime_marks = []
        self._layer_height = 0.1
        self._active_extrude_points = self._support_extrude_points
        self._active_extrude_amounts = self._support_extrude_amounts

        if prev_layer is not None:
            self._x = prev_layer._x
            self._y = prev_layer._y
            self._z = prev_layer._z
            self._e = prev_layer._e
            self._feedrate = prev_layer._feedrate
            self._retracted = prev_layer._retracted

    def setPosition(self, x, y, z, e):
        if x is not None:
            self._x = x
        if y is not None:
            self._y = y
        if z is not None:
            self._z = z
        if e is not None:
            self._e = e

    def addMove(self, x, y, z, e, f):
        new_x = self._x
        new_y = self._y
        new_z = self._z
        new_e = self._e
        if f is not None:
            self._feedrate = f
        if x is not None:
            new_x = x
        if y is not None:
            new_y = y
        if z is not None:
            new_z = z
        if e is not None:
            new_e = e
        if new_e > self._e:
            if self._retracted:
                self._retracted = False
                self._addPrimeMark(new_x, new_y, new_z)
                if new_x != self._x or new_y != self._y or new_z != self._z:
                    self._move_points.append([self._x, self._y, self._z])
                    self._move_points.append([new_x, new_y, new_z])
            else:
                # Extrusion
                if new_x != self._x or new_y != self._y or new_z != self._z:
                    self._last_extrusion_z = new_z
                    self._active_extrude_points.append([self._x, self._y, self._z, new_x, new_y, new_z])
                    self._active_extrude_amounts.append(new_e - self._e)
        elif new_e < self._e:
            self._retracted = True
            self._addRetractionMark(self._x, self._y, self._z)
            if new_x != self._x or new_y != self._y or new_z != self._z:
                self._move_points.append([self._x, self._y, self._z])
                self._move_points.append([new_x, new_y, new_z])
        else:
            self._move_points.append([self._x, self._y, self._z])
            self._move_points.append([new_x, new_y, new_z])
        self._x = new_x
        self._y = new_y
        self._z = new_z
        self._e = new_e

    def setFanSpeed(self, speed):
        pass

    def setTemperature(self, temperature):
        pass

    def setBedTemperature(self, temperature):
        pass

    def setExtrusionType(self, e_type):
        if e_type == 'WALL-OUTER':
            self._active_extrude_points = self._inset0_extrude_points
            self._active_extrude_amounts = self._inset0_extrude_amounts
        elif e_type == 'WALL-INNER':
            self._active_extrude_points = self._insetX_extrude_points
            self._active_extrude_amounts = self._insetX_extrude_amounts
        elif e_type == 'FILL':
            self._active_extrude_points = self._infill_extrude_points
            self._active_extrude_amounts = self._infill_extrude_amounts
        else:
            self._active_extrude_points = self._support_extrude_points
            self._active_extrude_amounts = self._support_extrude_amounts

    def _addRetractionMark(self, x, y, z):
        size = 1.0
        z += self._layer_height / 2.0
        self._retract_marks.append([x - size, y, z])
        self._retract_marks.append([x, y - size, z])
        self._retract_marks.append([x + size, y, z])
        self._retract_marks.append([x, y + size, z])

    def _addPrimeMark(self, x, y, z):
        size = 0.8
        z += self._layer_height / 2.0
        self._prime_marks.append([x - size, y, z])
        self._prime_marks.append([x, y - size, z])
        self._prime_marks.append([x + size, y, z])
        self._prime_marks.append([x, y + size, z])

    def _extrusion_to_renderer(self, points, amounts):
        if len(points) < 1:
            return None
        points = numpy.array(points, numpy.float32)
        xdiff = (points[::,0] - points[::,3])
        ydiff = (points[::,1] - points[::,4])
        lengths = numpy.sqrt((xdiff * xdiff) + (ydiff * ydiff))
        amounts /= lengths
        #Amounts is amount of E per mm now. Calculate the extrusion width by "width = E / layer_height"
        amounts *= self._e_correction_factor
        normals = (points[::, 3:6] - points[::, 0:3])
        normals[::,0] /= lengths
        normals[::,1] /= lengths
        normals[::,2] /= lengths
        tmp = -normals[::,1]
        normals[::,1] = normals[::,0]
        normals[::,0] = tmp
        normals[::,0] *= amounts
        normals[::,1] *= amounts
        normals[::,2] *= amounts
        verts = numpy.concatenate((points, points[::, 3:6], points[::, 0:3], points[::, 0:3] + normals, points[::, 3:6] + normals, points[::, 3:6] - normals, points[::, 0:3] - normals), 1)
        verts[::, 8] -= self._layer_height
        verts[::, 11] -= self._layer_height
        return openGLUtils.VertexRenderer(GL_QUADS, numpy.array(verts, numpy.float32).reshape((len(verts) * 8, 3)), False)

    def finalize(self):
        filamentRadius = 2.95 / 2.0
        filamentArea = math.pi * filamentRadius * filamentRadius
        self._layer_height = self._last_extrusion_z - self._prev_last_extrusion_z
        if self._layer_height <= 0.0:
            self._layer_height = self._last_extrusion_z
        if self._layer_height <= 0.0:
            self._layer_height = 0.1
        self._e_correction_factor = (filamentArea / self._layer_height / 2.0)

        self._move_points = openGLUtils.VertexRenderer(GL_LINES, numpy.array(self._move_points, numpy.float32), False)
        self._inset0_extrude_points = self._extrusion_to_renderer(self._inset0_extrude_points, self._inset0_extrude_amounts)
        self._insetX_extrude_points = self._extrusion_to_renderer(self._insetX_extrude_points, self._insetX_extrude_amounts)
        self._infill_extrude_points = self._extrusion_to_renderer(self._infill_extrude_points, self._infill_extrude_amounts)
        self._support_extrude_points = self._extrusion_to_renderer(self._support_extrude_points, self._support_extrude_amounts)
        self._retract_marks = openGLUtils.VertexRenderer(GL_QUADS, numpy.array(self._retract_marks, numpy.float32), False)
        self._prime_marks = openGLUtils.VertexRenderer(GL_QUADS, numpy.array(self._prime_marks, numpy.float32), False)

    def render(self, main_renderer, c):
        if main_renderer._show_moves:
            glColor3f(0, 0, c)
            self._move_points.render()

        if main_renderer._show_outer_wall and self._inset0_extrude_points is not None:
            glColor3f(c, 0, 0)
            self._inset0_extrude_points.render()
        if main_renderer._show_inner_wall and self._insetX_extrude_points is not None:
            glColor3f(0, c, 0)
            self._insetX_extrude_points.render()
        if main_renderer._show_infill and self._infill_extrude_points is not None:
            glColor3f(c, c, 0)
            self._infill_extrude_points.render()
        if main_renderer._show_support and self._support_extrude_points is not None:
            glColor3f(0, c, c)
            self._support_extrude_points.render()

        if main_renderer._show_retraction:
            glColor3f(0, 0, 0.5 * c)
            self._retract_marks.render()

            glColor3f(0.5 * c, 0, 0.5 * c)
            self._prime_marks.render()


class GCodeRenderer(object):
    def __init__(self, gcode):
        self._layers = []

        thread = threading.Thread(target=self._process, args=(gcode,))
        thread.daemon = True
        thread.start()

    def _process(self, gcode):
        G = re.compile('G([0-9]+)')
        M = re.compile('M([0-9]+)')
        X = re.compile('X([0-9\\.]+)')
        Y = re.compile('Y([0-9\\.]+)')
        Z = re.compile('Z([0-9\\.]+)')
        E = re.compile('E([0-9\\.]+)')
        F = re.compile('F([0-9\\.]+)')
        S = re.compile('S([0-9]+)')

        current_layer = GCodeLayerRenderer()
        for line in gcode.split('\n'):
            if line.startswith(';'):
                if line.startswith(';LAYER:'):
                    current_layer.finalize()
                    time.sleep(0.001)
                    self._layers.append(current_layer)
                    current_layer = GCodeLayerRenderer(current_layer)
                    current_layer._prev_last_extrusion_z = self._layers[-1]._last_extrusion_z
                if line.startswith(';TYPE:'):
                    current_layer.setExtrusionType(line[6:].strip())
            else:
                g = G.search(line)
                if g:
                    g = int(g.group(1))
                    if g == 0 or g == 1:
                        x = X.search(line)
                        y = Y.search(line)
                        z = Z.search(line)
                        e = E.search(line)
                        f = F.search(line)
                        if x:
                            x = float(x.group(1))
                        if y:
                            y = float(y.group(1))
                        if z:
                            z = float(z.group(1))
                        if e:
                            e = float(e.group(1))
                        if f:
                            f = float(f.group(1))
                        current_layer.addMove(x, y, z, e, f)
                    elif g == 21:
                        pass # Metric
                    elif g == 28:
                        pass # Home
                    elif g == 90:
                        pass # Absolute positioning
                    elif g == 91:
                        pass # Relative positioning
                    elif g == 92:
                        x = X.search(line)
                        y = Y.search(line)
                        z = Z.search(line)
                        e = E.search(line)
                        if x:
                            x = float(x.group(1))
                        if y:
                            y = float(y.group(1))
                        if z:
                            z = float(z.group(1))
                        if e:
                            e = float(e.group(1))
                        current_layer.setPosition(x, y, z, e)
                    else:
                        print 'G', g
                else:
                    m = M.search(line)
                    if m:
                        m = int(m.group(1))
                        if m == 104:
                            s = S.search(line)
                            if s:
                                s = int(s.group(1))
                                current_layer.setTemperature(s)
                        elif m == 140:
                            s = S.search(line)
                            if s:
                                s = int(s.group(1))
                                current_layer.setBedTemperature(s)
                        elif m == 109:
                            s = S.search(line)
                            if s:
                                s = int(s.group(1))
                                current_layer.setTemperature(s)
                        elif m == 190:
                            s = S.search(line)
                            if s:
                                s = int(s.group(1))
                                current_layer.setBedTemperature(s)
                        elif m == 106:
                            s = S.search(line)
                            if s:
                                s = int(s.group(1))
                                current_layer.setFanSpeed(s)
                            else:
                                current_layer.setFanSpeed(255)
                        elif m == 107:
                            current_layer.setFanSpeed(0)
                        elif m == 84:
                            pass # Steppers off
                        else:
                            print 'M', m
        current_layer.finalize()
        self._layers.append(current_layer)

    def render(self, main_renderer):
        f = 1.0
        bottom_layer_nr = 0
        top_layer_nr = main_renderer._top_layer_nr
        if main_renderer._is_single_layer:
            bottom_layer_nr = top_layer_nr - 1
        for layer in self._layers[top_layer_nr:bottom_layer_nr:-1]:
            layer.render(main_renderer, f)
            f -= 0.05
            if f < 0.5:
                f = 1.0


class ToolpathLayerRenderer(object):
    COLORS = {
        'skirt': (0, 0.5, 0.5),
        'inset0': (0.5, 0, 0.5),
        'insetx': (0.5, 0.5, 0),
        'skin': (0.5, 0.5, 0),
        'support': (0.5, 0.5, 0),
    }

    def __init__(self, layer):
        self._renderer = {}
        self._layer = layer

    def render(self):
        for type in self._layer.getPathTypes():
            if not type in self._renderer:
                polygons = self._layer.getPolygons(type)
                point_count = 0
                indices_count = 0
                for poly in polygons:
                    point_count += len(poly)
                    indices_count += len(poly) * 4
                points = numpy.zeros((point_count, 2), numpy.float32)
                indices = numpy.zeros(indices_count, dtype=numpy.int32)
                point_index = 0
                indices_index = 0
                for poly in polygons:
                    n = len(poly)
                    points[point_index:point_index + n] = poly
                    i1 = numpy.arange(n, dtype=numpy.int32).reshape((n, 1)) + point_index
                    i2 = i1 + point_count
                    indices[indices_index:indices_index + (n * 4)] = numpy.concatenate((i1, i1 + 1, i2 + 1, i2), 1).reshape((n * 4))
                    indices[indices_index + (n * 4) - 3] = i1[0]
                    indices[indices_index + (n * 4) - 2] = i2[0]

                    point_index += n
                    indices_index += n * 4
                z_pos1 = numpy.zeros((point_count, 1), numpy.float32)
                z_pos2 = numpy.zeros((point_count, 1), numpy.float32)
                z_pos1.fill(self._layer._z_height)
                z_pos2.fill(self._layer._z_height - self._layer._layer_height)
                points1 = numpy.concatenate((points, z_pos1), 1)
                points2 = numpy.concatenate((points, z_pos2), 1)
                self._renderer[type] = openGLUtils.VertexRenderer(GL_QUADS, numpy.concatenate((points1, points2)), False, indices)
            glColor3fv(self.COLORS[type])
            self._renderer[type].render()


class ToolpathRenderer(Renderer):
    def __init__(self):
        super(ToolpathRenderer,self).__init__()

        self._show_outer_wall = True
        self._show_inner_wall = True
        self._show_infill = True
        self._show_support = True
        self._show_moves = False
        self._show_retraction = True
        self._is_single_layer = False

        self._top_layer_nr = 1

    def render(self):
        glPushMatrix()
        if self.machine.getSettingValueByKey('machine_center_is_zero') == 'False':
            glTranslatef(-self.machine.getSettingValueByKeyFloat('machine_width') / 2.0, -self.machine.getSettingValueByKeyFloat('machine_depth') / 2.0, 0.0)
        glDisable(GL_CULL_FACE)
        glDisable(GL_LIGHTING)
        for obj in self.scene.getObjects():
            for layer_nr in xrange(0, obj.getToolpathLayerCount()):
                layer = obj.getToolpathLayer(layer_nr)
                if layer is None:
                    continue
                if not hasattr(layer, 'renderer'):
                    layer.renderer = ToolpathLayerRenderer(layer)
                # layer.renderer.render(self)

        gcode = self.scene.getResult().getGCode()
        if gcode is not None:
            if not hasattr(self.scene.getResult(), 'renderer'):
                self.scene.getResult().renderer = GCodeRenderer(gcode)
            self.scene.getResult().renderer.render(self)
        glPopMatrix()

    def focusRender(self):
        pass

    def showOuterWall(self, show):
        self._show_outer_wall = show

    def showInnerWall(self, show):
        self._show_inner_wall = show

    def showInfill(self, show):
        self._show_infill = show

    def showSupport(self, show):
        self._show_support = show

    def showMoves(self, show):
        self._show_moves = show

    def showRetraction(self, show):
        self._show_retraction = show

    def setTopShowLayerNr(self, nr):
        self._top_layer_nr = nr

    def setSingleLayer(self, is_single_layer):
        self._is_single_layer = is_single_layer