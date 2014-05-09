from ConfigParser import ConfigParser

preferences = None


def getPreference(key, default):
    global preferences
    if preferences is None:
        return default
    if not preferences.has_option('preferences', key):
        return default
    return preferences.get('preferences', key)


def setPreference(key, value):
    global preferences
    if preferences is None:
        preferences = ConfigParser()
    if not preferences.has_section('preferences'):
        preferences.add_section('preferences')
    preferences.set('preferences', key, value)


def savePreferences(filename):
    global preferences
    if preferences is None:
        return
    with open(filename, "w") as f:
        preferences.write(f)


def loadPreferences(filename):
    global preferences
    preferences = ConfigParser()
    preferences.read(filename)
    if not preferences.has_section('preferences'):
        preferences.add_section('preferences')
