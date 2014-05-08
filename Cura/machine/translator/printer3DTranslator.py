
from Cura.machine.translator.translator import Translator


class Printer3DTranslator(Translator):
    def __init__(self, scene, machine):
        super(Printer3DTranslator, self).__init__(scene, machine)
