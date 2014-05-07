__author__ = 'Jaime van Kessel'

import platform
import os
from Cura.machine.translator.printer3DTranslator import Printer3DTranslator


class FDMPrinterTranslator(Printer3DTranslator):
    def __init__(self, scene, machine):
        super(FDMPrinterTranslator, self).__init__(scene, machine)
        self._engine_executable_name = 'CuraEngine'

    def findExecutable(self):
        """
            Finds and returns the path to the current engine executable. This is OS depended.
        :return: The full path to the engine executable.
        """
        if platform.system() == 'Windows':
            if os.path.exists('C:/Software/Cura_SteamEngine/_bin/Release/Cura_SteamEngine.exe'):
                return 'C:/Software/Cura_SteamEngine/_bin/Release/Cura_SteamEngine.exe'
        return super(FDMPrinterTranslator, self).findExecutable()

    def canTranslate(self):
        return True

    def getCommandParameters(self):
        return []
