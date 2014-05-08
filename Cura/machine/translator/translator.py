import platform
import os
import subprocess
import threading
from cStringIO import StringIO


class Translator(object):
    """
    The translator class forms the interface between Cura and the engine. The translator communicates with
    a socket, which in place sends the data to the engine.
    Some machines might need to send (or receive) different kinds of data. This is the base class, with inherited
    classes for such cases.
    """
    def __init__(self, scene, machine):
        self._engine_executable_name = 'Engine'
        self._engine_thread = None
        self._engine_process = None
        self._connections = []
        self._scene = scene
        self._machine = machine
        self._start_timer = None
        self._start_delay = 0.5

    def trigger(self):
        """
        Call this function when you want to trigger the translator, there is a short delay before the process is run so multiple
        triggers in a short period do not spawn a lot of processes.
        """
        if self._start_timer is not None:
            self._start_timer.cancel()
        self._start_timer = threading.Timer(self._start_delay, self._onTrigger)
        self._start_timer.start()

    def _onTrigger(self):
        self._start_timer = None
        self.start()

    def findExecutable(self):
        """
            Finds and returns the path to the current engine executable. This is OS depended.
        :return: The full path to the engine executable.
        """
        name = self._engine_executable_name
        if platform.system() == 'Windows':
            name += '.exe'
            if os.path.exists('C:/Software/Cura_SteamEngine/_bin/Release/Cura_SteamEngine.exe'):
                return 'C:/Software/Cura_SteamEngine/_bin/Release/Cura_SteamEngine.exe'
        searchPaths = [
            os.path.join(os.path.dirname(__file__), '../..'),
            os.path.join(os.path.dirname(__file__), '../../../../..'),
            os.path.join(os.path.dirname(__file__), '../..', self._engine_executable_name),
            '/usr/bin/',
            '/usr/local/bin/',
        ]
        for path in searchPaths:
            p = os.path.abspath(os.path.join(path, name))
            if os.path.isfile(p):
                return p

        raise RuntimeError('Engine executable not found...')

    def _runEngineProcess(self, commandList):
        """
        Run the given commands, small wrapper around subprocess.Popen so the process is hidden on Windows, and started as low priority.
        """
        kwargs = {}
        if subprocess.mswindows:
            su = subprocess.STARTUPINFO()
            su.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            su.wShowWindow = subprocess.SW_HIDE
            kwargs['startupinfo'] = su
            kwargs['creationflags'] = 0x00004000 #BELOW_NORMAL_PRIORITY_CLASS
        return subprocess.Popen(commandList, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)

    def start(self):
        self._engine_thread = threading.Thread(target=self._start, args=(self._engine_thread,))
        self._engine_thread.daemon = True
        self._engine_thread.start()

    def _start(self, prevThread):
        if prevThread is not None:
            # If an old engine thread was still running, kill it.
            if self._engine_process is not None:
                try:
                    self._engine_process.terminate()
                except:  # Sometimes the process is already dead, at which point terminate will throw an exception, ignore that.
                    pass
            prevThread.join()

        self._engine_process = None
        self._result_output = StringIO()
        self._result_log = StringIO()

        if not self.canTranslate():
            return

        self.setup()
        for connection in self._connections:
            connection.setup()

        commandList = [self.findExecutable()]
        for connection in self._connections:
            commandList += connection.getCommandParameters()
        commandList += self.getCommandParameters()
        self._engine_process = self._runEngineProcess(commandList)

        communicationThread = threading.Thread(target=self._communicate)
        communicationThread.daemon = True
        communicationThread.start()

        logThread = threading.Thread(target=self._watchStderr, args=(self._engine_process.stderr,))
        logThread.daemon = True
        logThread.start()

        data = self._engine_process.stdout.read(4096)
        while len(data) > 0:
            self._result_output.write(data)
            data = self._engine_process.stdout.read(4096)

        for connection in self._connections:
            connection.finish()

        logThread.join()
        communicationThread.join()

        returnCode = self._engine_process.wait()
        self._engine_process = None
        #if returnCode != 0:
        print self._result_log.getvalue()

    def _communicate(self):
        for connection in self._connections:
            connection.connect()
        self.communicate()

    def _watchStderr(self, stderr):
        data = stderr.read(4096)
        while len(data) > 0:
            self._result_log.write(data)
            data = stderr.read(4096)

    def addConnection(self, connection):
        self._connections.append(connection)

    def sendData(self, data):
        for connection in self._connections:
            if connection.sendData(data):
                return

    def canTranslate(self):
        """ Override in subclass """
        return True

    def getCommandParameters(self):
        """ Override in subclass """
        return []

    def setup(self):
        """ Override in subclass """
        pass

    def communicate(self):
        """ Override in subclass """
        pass

    def receivedData(self, data):
        """ Override in subclass """
        pass
