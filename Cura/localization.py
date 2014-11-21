import os
import gettext

from Cura.resources import getResourcePath

##  Handle translations and locale-based formatting.
#
#   TODO: Implement additional languages and locales. It would probably also help if things were moved to a
#   Locale class.
def setup():
    languages = ['en']

    locale_path = getResourcePath('locale')
    locale_path = os.path.normpath(locale_path)
    translation = gettext.translation('Cura', locale_path, languages, fallback=True)
    translation.install(unicode=True)


def formatMaterial(amount_in_mm):
    if amount_in_mm < 1000:
        return '%0.2fm' % (amount_in_mm / 1000.0)
    return '%0.1fm' % (amount_in_mm / 1000.0)


def formatTime(time_in_seconds):
    return '%d hours %d minutes' % (int(time_in_seconds / 60.0 / 60.0), int(time_in_seconds / 60.0 % 60.0))
