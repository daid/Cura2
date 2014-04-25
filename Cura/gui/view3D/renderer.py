
class Renderer(object):
    """
    Abstract renderer class
    """

    def __init__(self):
        super(Renderer, self).__init__()
        self.active = True
        self.machine = None
        self.scene = None

    def render(self):
        pass
