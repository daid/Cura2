__author__ = 'Jaime van Kessel'

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
        self._platform_mesh = None

    def _update(self, instructions):
        if self.machine is None:
            return

        instructions.add(UpdateNormalMatrix())
        machine_shape = self.machine.getShape()
        height = self.machine.getSettingValueByKeyFloat('machine_height')

        vertex_data = []
        indices = []
        for p in machine_shape:
            vertex_data += [p[0], p[1], 0.05, p[0]/20.0, p[1]/20.0]
        cnt = len(machine_shape)
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
        for p in machine_shape:
            vertex_data += [p[0], p[1], 0.05, 0, 0]
        for p in machine_shape:
            vertex_data += [p[0], p[1], height, 0, 0]
        cnt = len(machine_shape)
        for n in range(0, cnt - 2):
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
