__author__ = 'd.braam'

import os
import gettext

from kivy.resources import resource_find


def setup():
    languages = ['en']

    locale_path = resource_find('locale')
    if locale_path is not None:
        locale_path = os.path.normpath(locale_path)
    translation = gettext.translation('Cura', locale_path, languages, fallback=True)
    translation.install(unicode=True)
