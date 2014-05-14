
import ConfigParser as configParser

preferences = None


def getPreference(key, default='', section='preferences'):
    global preferences
    if preferences is None:
        return default
    if not preferences.has_section(section):
        return default
    if not preferences.has_option(section, key):
        return default
    return preferences.get(section, key)


def setPreference(key, value, section='preferences'):
    global preferences
    if preferences is None:
        preferences = configParser.ConfigParser()
    if not preferences.has_section(section):
        preferences.add_section(section)
    preferences.set(section, key, value)


def savePreferences(filename):
    global preferences
    if preferences is None:
        return
    with open(filename, "w") as f:
        preferences.write(f)


def loadPreferences(filename):
    global preferences
    preferences = configParser.ConfigParser()
    preferences.read(filename)
