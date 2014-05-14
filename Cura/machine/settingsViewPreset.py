
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
