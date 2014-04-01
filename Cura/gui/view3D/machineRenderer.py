__author__ = 'Jaime van Kessel'

from kivy.graphics import BindTexture
from kivy.graphics import Mesh
from kivy.graphics import UpdateNormalMatrix
from kivy.core.image import Image
from kivy.resources import resource_find

from Cura.gui.view3D.renderer import Renderer
from Cura.meshLoaders import meshLoader


class MachineRenderer(Renderer):
    """
    Renderer responsible for rendering the 3D model of the machine
    """
    def __init__(self):
        super(MachineRenderer,self).__init__()
        self._machine_width = 0
        self._machine_height = 0
        self._machine_depth = 0
        self._mesh_path = resource_find('meshes/ultimaker_platform.stl') #Todo; hardcoded now.
        self._platform_mesh = None
        self._platform_image = Image('checkerboard.png', mipmap=True)
        self._platform_image.texture.wrap = 'repeat'
        self._platform_image.texture.mag_filter = 'nearest'
        self._platform_image.texture.min_filter = 'nearest_mipmap_linear'

    def _update(self, instructions):
        instructions.add(UpdateNormalMatrix())

        #polys = self.machine.getShape()
        polys = [
            [[-100.0, -100.0], [100.0, -100.0], [100.0, 100.0], [-100.0, 100.0]]
        ]

        vertex_data = []
        indices = []
        for p in polys[0]:
            vertex_data += [p[0], p[1], 0.05, p[0]/20.0, p[1]/20.0]
        cnt = len(polys[0])
        for n in range(0, cnt - 2):
            indices += [0, n+1, n+2]
        instructions.add(Mesh(
            vertices=vertex_data,
            indices=indices,
            fmt=[('v_pos', 3, 'float'), ('v_tc0', 2, 'float')],
            mode='triangles',
            texture=self._platform_image.texture
        ))

        vertex_data = []
        indices = []
        for p in polys[0]:
            vertex_data += [p[0], p[1], 0.05, 0, 0]
        for p in polys[0]:
            vertex_data += [p[0], p[1], 200.0, 0, 0]
        cnt = len(polys[0])
        for n in range(0, cnt - 2):
            indices += [0, n+1, n+2]
            indices += [cnt, cnt+n+2, cnt+n+1]
        for n in range(0, cnt):
            indices += [(n+1)%cnt, n, cnt+n]
            indices += [(n+1)%cnt, cnt+n, (cnt+(n+1)%cnt)]
        instructions.add(Mesh(
            vertices=vertex_data,
            indices=indices,
            fmt=[('v_pos', 3, 'float'), ('v_tc0', 2, 'float')],
            mode='triangles',
            texture=self._platform_image.texture
        ))

    def render(self):
        super(MachineRenderer, self).render()
        if self._machine is not None:
            #Draw machine
            glEnable(GL_CULL_FACE)
            glEnable(GL_BLEND)
            #size = [self._machine_width,self._machine_depth,self._machine_height]
            if self._platform_mesh is None:
                self._platform_mesh = meshLoader.loadMesh(self._mesh_path)
            #if(self._test_mesh is None):
            #    self._test_mesh = meshLoader.loadPrintableObject(self._test_mesh_path)
            glColor4f(1,0.7,0.8,0.5)
            self._object_shader.bind()
            self._renderMesh(self._platform_mesh)
            #glColor4f(1,0.7,0.8,1)
            #self._renderObject(self._test_mesh[0])
            #self._renderObject(self._platform_mesh[0])
            self._object_shader.unbind()
            #Draw sides
            glDepthMask(False)
            polys = self._machine.getShape()
            height = self._machine.getSettingValueByNameFloat('machine_height')
            glBegin(GL_QUADS)
            # Draw the sides of the build volume.
            for n in xrange(0, len(polys[0])):
                #if not circular:
                if n % 2 == 0:
                    glColor4ub(5, 171, 231, 96)
                else:
                    glColor4ub(5, 171, 231, 64)

                glVertex3f(polys[0][n][0], polys[0][n][1], height)
                glVertex3f(polys[0][n][0], polys[0][n][1], 0)
                glVertex3f(polys[0][n-1][0], polys[0][n-1][1], 0)
                glVertex3f(polys[0][n-1][0], polys[0][n-1][1], height)
            glEnd()

            #Draw top of build volume.
            glColor4ub(5, 171, 231, 128)
            glBegin(GL_TRIANGLE_FAN)
            for p in polys[0][::-1]:
                glVertex3f(p[0], p[1], height)
            glEnd()
            #Draw checkerboard

            if self._platform_texture is None:
                self._platform_texture = openglHelpers.loadGLTexture('checkerboard.png')
                glBindTexture(GL_TEXTURE_2D, self._platform_texture)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glColor4f(1,1,1,0.5)
            glBindTexture(GL_TEXTURE_2D, self._platform_texture)
            glEnable(GL_TEXTURE_2D)
            glBegin(GL_TRIANGLE_FAN)
            for p in polys[0]:
                glTexCoord2f(p[0]/20, p[1]/20)
                glVertex3f(p[0], p[1], 0.05) #drawn a bit above the model to prevent z-fight
            glEnd()

            #Draw no-go zones (if any)
            glDisable(GL_TEXTURE_2D)
            glColor4ub(127, 127, 127, 200)
            polys = self._machine.getDisallowedZones()
            for poly in polys:
                glBegin(GL_TRIANGLE_FAN)
                for p in poly:
                    glTexCoord2f(p[0]/20, p[1]/20)
                    glVertex3f(p[0], p[1], 0)
                glEnd()
            glDepthMask(True)
            glDisable(GL_BLEND)
            glDisable(GL_CULL_FACE)
