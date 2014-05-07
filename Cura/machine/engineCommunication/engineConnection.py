
class EngineConnection(object):
    """
    Interface for connection with engine. This is the lowest level of communication.
    The connection classes only handle the sending of data.
    The translator class handle the conversion from models to send-able data.
    """
    def __init__(self):
        pass

    def setup(self, scene, machine):
        """
        Setup is called before the engine is started, but after the previous engine is finished running (or killed)
        """
        pass

    def getCommandParameters(self):
        """
        getCommandParameters is called before the engine is started, these are extra parameters given to the engine
        so it knows that it will get this connection.
        """
        return []
