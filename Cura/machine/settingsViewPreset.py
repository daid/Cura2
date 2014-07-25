import ConfigParser as configParser


def loadSettingViewPresets(filename):
    """
    Returns a list of SettingsViewPresets
    """
    cp = configParser.ConfigParser()
    cp.read(filename)
    n = 1
    ret = []
    while cp.has_section('ViewPreset_%d' % (n)):
        svp = SettingsViewPreset()
        svp.setName(cp.get('ViewPreset_%d' % (n), 'view_preset_name'))
        for key in cp.options('ViewPreset_%d' % (n)):
            svp.setSettingVisible(key, cp.get('ViewPreset_%d' % (n), key) == 'True')
        ret.append(svp)
        n += 1
    return ret


def saveSettingViewPresets(filename, svp_list):
    """
    Save a list of SettingsViewPresets to an ini file.
    Returns True on success
    """
    cp = configParser.ConfigParser()
    n = 1
    for svp in svp_list:
        if not svp.isBuildIn():
            svp.addToConfigParser(cp, 'ViewPreset_%d' % (n))
            cp.set('ViewPreset_%d' % (n), 'view_preset_name', svp.getName())
            n += 1
    try:
        with open(filename, "w") as f:
            cp.write(f)
    except IOError:
        return False
    return True


class SettingsViewPreset(object):
    def __init__(self):
        self._name = 'No name'
        self._setting_key_map = {}
        self._build_in = False

    def copy(self):
        svp = SettingsViewPreset()
        svp.setName(self._name + " copy")
        svp._setting_key_map = self._setting_key_map.copy()
        return svp

    def getName(self):
        return self._name

    def setName(self, name):
        self._name = name

    def setBuildIn(self):
        self._build_in = True

    def isBuildIn(self):
        return self._build_in

    def setSettingVisible(self, key, visible):
        self._setting_key_map[key] = visible

    def isSettingVisible(self, key):
        if key not in self._setting_key_map:
            self._setting_key_map[key] = False
        return self._setting_key_map[key]

    def applyPreset(self, machine):
        for category in machine.getSettingCategories():
            if category.isVisible():
                for setting in category.getSettings():
                    setting.setVisible(self.isSettingVisible(setting.getKey()))

    def exportToFile(self, filename):
        config = configParser.ConfigParser()
        self.addToConfigParser(config, 'view_preset')
        with open(filename, "w") as f:
            config.write(f)

    def addToConfigParser(self, config_parser, section_name):
        config_parser.add_section(section_name)
        for k, v in self._setting_key_map.items():
            config_parser.set(section_name, k, str(v))

    def importFromFile(self, filename):
        config = configParser.ConfigParser()
        config.read(filename)
        if not config.has_section('view_preset'):
            return False
        self._setting_key_map = {}
        for k in config.options('view_preset'):
            self._setting_key_map[k] = config.get('view_preset', k) == 'True'
