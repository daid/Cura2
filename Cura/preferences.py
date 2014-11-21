
import ConfigParser as configParser

preferences = None

##  Handle loading and saving preferences to a preferences file.
#
#   TODO: Move to its own class and get rid of globals.

##  Return a single preference value
#   \param key The preference to get
#   \param default The value to return if not found
#   \param section The section the preference should be located in
#
#   \return The value of the preference or \param default if not found.
#
#   TODO: Use "Section/Pref" notation to allow nesting and easier handling of sections
def getPreference(key, default='', section='preferences'):
    global preferences
    if preferences is None:
        return default
    if not preferences.has_section(section):
        return default
    if not preferences.has_option(section, key):
        return default
    return preferences.get(section, key)

##  Set a preference.
#   \param key The preference to set.
#   \param value The value to set the preference to.
#   \param section The section the preference belongs to.
#
#   \sa getPreference
def setPreference(key, value, section='preferences'):
    global preferences
    if preferences is None:
        preferences = configParser.ConfigParser()
    if not preferences.has_section(section):
        preferences.add_section(section)
    preferences.set(section, key, str(value))

##  Write preferences to a file.
#   \param filename The name of the file to write to.
def savePreferences(filename):
    global preferences
    if preferences is None:
        return
    with open(filename, "w") as f:
        preferences.write(f)

##  Read preferences from a file.
#   \param filename The filename to read from.
#   \return A ConfigParser object representing the preferences
def loadPreferences(filename):
    global preferences
    preferences = configParser.ConfigParser()
    preferences.read(filename)
