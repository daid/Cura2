import os
import gettext

from Cura.resources import getResourcePath

def setup():
    languages = ['en']

    #TODO: Resource path
    locale_path = getResourcePath('locale')
    print locale_path
    locale_path = os.path.normpath(locale_path)
    translation = gettext.translation('Cura', locale_path, languages, fallback=True)
    translation.install(unicode=True)
