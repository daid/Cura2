__author__ = 'd.braam'

import os
import gettext



def setup():
    languages = ['en']

    #TODO: Resource path
    locale_path = os.path.dirname(__file__)
    print locale_path
    if locale_path is not None:
        locale_path = os.path.normpath(locale_path)
    translation = gettext.translation('Cura', locale_path, languages, fallback=True)
    translation.install(unicode=True)
