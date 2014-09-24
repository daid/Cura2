
class Renderer(object):
    """
    Abstract renderer class
    """

    def __init__(self):
        super(Renderer, self).__init__()
        self.active = True
        self.machine = None
        self.scene = None
        self.view = None

    def focusRender(self):
        pass

    def render(self):
        pass

    def setCurrentFocusRenderObject(self, obj, sub_section=None):
        self.view.setCurrentFocusRenderObject(obj, sub_section)