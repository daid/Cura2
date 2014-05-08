
class EngineConnection(object):
    """
    Interface for connection with engine. This is the lowest level of communication.
    The connection classes only handle the sending of data.
    The translator class handle the conversion from models to send-able data.
    """
    def __init__(self, translator):
        self._translator = translator

    def received(self, data):
        self._translator.receivedData(data)

    def setup(self):
        """
        Setup is called before the engine is started, but after the previous engine is finished running (or killed)
        Used to setup the connector for a new run of the engine.
        """
        pass

    def connect(self):
        """
        Called after creating the process, so a connection to the process can be made.
        """
        pass

    def finish(self):
        """
        Finish is called after the engine is finished running. Can be used for cleanup.
        """
        pass

    def getCommandParameters(self):
        """
        getCommandParameters is called before the engine is started, these are extra parameters given to the engine
        so it knows that it will get this connection.
        """
        return []

    def sendData(self, data):
        """ Override in subclass """
        return False
