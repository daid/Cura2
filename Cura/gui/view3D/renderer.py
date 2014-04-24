from Cura.scene.scene import Scene
from Cura.machine.machine import Machine


class PropertyBase(object):
    def __init__(self):
        self._property__map = {}

    def _propertyChanged(self):
        pass


class Property(object):
    def __init__(self, value=None):
        self.__default_value = value

    def __get__(self, instance, instancetype=None):
        if self in instance._property__map:
            return instance._property__map[self]
        return self.__default_value

    def __set__(self, instance, value):
        instance._property__map[self] = value
        instance._propertyChanged()


class Renderer(PropertyBase):
    """
    Abstract renderer class
    """
    active = Property(True)
    machine = Property(None)
    scene = Property(None)

    def __init__(self):
        super(Renderer, self).__init__()

    def render(self):
        pass

    def _propertyChanged(self):
        pass
        #TODO: Queue refresh
