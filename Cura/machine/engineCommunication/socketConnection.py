__author__ = 'Jaime van Kessel'

import socket
import threading
import errno
import struct
import time
from Cura.machine.engineCommunication.engineConnection import EngineConnection


class SocketConnection(EngineConnection):
    """
    The SocketConnection handles a connection to the engine trough a TCP/IP socket.
    This can send&receive large amounts of binary data. One connection exists at a time.
    """
    def __init__(self, translator, serverPort=0xC20A):
        super(SocketConnection, self).__init__(translator)

        self._serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._serverPortNr = serverPort
        while True:
            try:
                self._serverSocket.bind(('127.0.0.1', self._serverPortNr))
            except:
                print "Failed to listen on port: %d" % (self._serverPortNr)
                self._serverPortNr += 1
                if self._serverPortNr > 0xFFFF:
                    print "Failed to listen on any port..."
                    break
            else:
                break
        self._thread = None
        self._dataSocket = None
        self._listenThread = threading.Thread(target=self._socketListenFunction)
        self._listenThread.daemon = True
        self._listenThread.start()

    def _socketListenFunction(self):
        self._serverSocket.listen(1)
        print 'Listening for engine communications on %d' % (self._serverPortNr)
        while True:
            try:
                self._dataSocket, _ = self._serverSocket.accept()
                self._thread = threading.Thread(target=self._socketConnectionFunction)
                self._thread.daemon = True
                self._thread.start()
            except socket.error, e:
                if e.errno != errno.EINTR:
                    raise

    def _socketConnectionFunction(self):
        try:
            while self._dataSocket is not None:
                size = self.readInt32()
                data = self.read(size)
                self.received(data)
        except IOError:
            pass
        self._close()

    def _close(self):
        """
        Close the current socket connection, if opened.
        """
        if self._dataSocket is not None:
            try:
                self._dataSocket.close()
            except:
                pass
            self._dataSocket = None

    def readInt32(self):
        return struct.unpack('@i', self.read(4))[0]

    def read(self, size):
        data = ''
        while len(data) < size:
            if self._dataSocket is None:
                #Raise an IO error to signal the socket is closed.
                raise IOError()
            recv = self._dataSocket.recv(size - len(data))
            data += recv
            if len(recv) <= 0:
                #Raise an IO error to signal the socket is closed.
                raise IOError()
        return data

    def sendData(self, data):
        if self._dataSocket is None:
            return False
        self._dataSocket.sendall(struct.pack('@i', len(data)))
        self._dataSocket.sendall(data)
        return True

    def setup(self):
        """
        Setup is called before the engine is started, but after the previous engine is finished running (or killed)
        """
        # When we setup a new translation, kill the current socket connection if not yet closed properly yet.
        self._close()
        self._wait_for_connection = True

    def connect(self):
        while self._dataSocket is None and self._wait_for_connection:
            time.sleep(0.1)

    def finish(self):
        self._wait_for_connection = False

    def getCommandParameters(self):
        """
        getCommandParameters is called before the engine is started, these are extra parameters given to the engine
        so it knows that it will get this connection.
        """
        return ['--socket', str(self._serverPortNr)]
