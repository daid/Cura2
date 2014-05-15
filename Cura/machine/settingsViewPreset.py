import ConfigParser as configParser

class SettingsViewPreset(object):
    def __init__(self):
        self._name = 'No name'
        self._setting_key_map = {}

    def copy(self):
        svp = SettingsViewPreset()
        svp.setName(self._name + " copy")
        svp._setting_key_map = self._setting_key_map.copy()
        return svp

    def getName(self):
        return self._name

    def setName(self, name):
        self._name = name

    def setSettingVisible(self, key, visible):
        self._setting_key_map[key] = visible

    def isSettingVisible(self, key):
        if key in self._setting_key_map:
            return self._setting_key_map[key]
        return False

    def applyPreset(self, machine):
        for category in machine.getSettingCategories():
            for setting in category.getSettings():
                setting.setVisible(self.isSettingVisible(setting.getKey()))

    def exportToFile(self, filename):
        config = configParser.ConfigParser()
        config.add_section('view_preset')
        for k, v in self._setting_key_map.items():
            config.set('view_preset', k, str(v))
        with open(filename, "w") as f:
            config.write(f)

    def importFromFile(self, filename):
        config = configParser.ConfigParser()
        config.read(filename)
        if not config.has_section('view_preset'):
            return False
        self._setting_key_map = {}
        for k in config.options('view_preset'):
            self._setting_key_map[k] = config.get('view_preset', k) == 'True'
