
import numpy
from ConfigParser import ConfigParser

from Cura.machine.setting import Setting
from Cura.machine.setting import SettingCategory


class Machine(object):
    """
    Machine is an low level object that holds settings. These settings are shared by all types of machines.
    """
    def __init__(self):
        self._setting_category_list = []  # List of SettingCategories, each category holds settings.
        self._translator = None
        self._translatorDelay = 0.5
        self._timer = None

        self.addSettingCategory(SettingCategory('machine').setLabel('Machine configuration').setVisible(False))

        self.addSetting('machine', Setting('machine_width', 200, 'float').setRange(0.0001).setLabel(_('Machine width'), _('Build area size of the machine along the X axis')))
        self.addSetting('machine', Setting('machine_height', 200, 'float').setRange(0.0001).setLabel(_('Machine height'), _('Build area size of the machine along the Y axis')))
        self.addSetting('machine', Setting('machine_depth', 200, 'float').setRange(0.0001).setLabel(_('Machine height'), _('Build area size of the machine along the Z axis')))
        self.addSetting('machine', Setting('machine_name', 'Machine', 'string').setLabel('Machine name'))
        self.addSetting('machine', Setting('machine_icon', '', 'string').setLabel('Machine icon', 'Used for the machine button.'))
        self.addSetting('machine', Setting('display_model', '', 'filename').setLabel('Display model', 'Used in the 3D screen to possible show a 3D model of the machine.'))

        self._machine_shape = numpy.zeros((0, 2), numpy.float32)  # Polygon that forms the 'box' around the machine
        self._disallowed_zones = []  # List of polys

    def addSettingCategory(self, category):
        assert(self.getSettingCategory(category.getKey()) is None)
        self._setting_category_list.append(category)
        self._setting_category_list.sort()

    def getSettingCategory(self, key):
        for c in self._setting_category_list:
            if c.getKey() == key:
                return c
        return None

    def getSettingCategories(self):
        return self._setting_category_list

    def addSetting(self, parent_key, setting):
        assert(self.getSettingCategory(setting.getKey()) is None)
        assert(self.getSettingByKey(setting.getKey()) is None)
        if setting.getLabel() == setting.getKey():
            print 'No proper description for: %s' % (setting.getKey())
        setting.setMachine(self)
        category = self.getSettingCategory(parent_key)
        if category is not None:
            category.addSetting(setting)
            return
        setting_parent = self.getSettingByKey(parent_key)
        if setting_parent is not None:
            setting_parent.addSetting(setting)
            return
        print 'Parent category/setting [%s] not found for [%s]' % (parent_key, setting.getKey())

    def getShape(self):
        return self._machine_shape

    def getDisallowedZones(self):
        return self._disallowed_zones

    def getSize(self):
        return numpy.array([self.getSettingValueByKeyFloat('machine_width'),self.getSettingValueByKeyFloat('machine_depth'),self.getSettingValueByKeyFloat('machine_height')])

    def getSettingByKey(self, key):
        for c in self._setting_category_list:
            s = c.getSettingByKey(key)
            if s is not None:
                return s
        return None

    def setSettingValueByKey(self, key, value):
        s = self.getSettingByKey(key)
        if s is not None:
            s.setValue(value)

    def getSettingValueByKey(self, key):
        s = self.getSettingByKey(key)
        if s is not None:
            return s.getValue()
        import traceback, sys
        traceback.print_stack()
        sys.stderr.write('Setting key not found: %s' % key)
        return ''

    def getSettingValueByKeyFloat(self, key):
        try:
            value = self.getSettingValueByKey(key)
            value = value.replace(',', '.')
            return float(eval(value, {}, {}))
        except:
            return 0.0

    def saveSettings(self, filename):
        settings_storage = ConfigParser()
        self.saveSettingsToConfigParser(settings_storage, 'settings')
        with open(filename, "w") as f:
            settings_storage.write(f)

    def loadSettings(self, filename):
        settings_storage = ConfigParser()
        settings_storage.read(filename)
        self.loadSettingsFromConfigParser(settings_storage, 'settings')

    def saveSettingsToConfigParser(self, config_parser, section_name):
        config_parser.add_section(section_name)
        config_parser.set(section_name, 'machine_class', '%s.%s' % (type(self).__module__, type(self).__name__))
        for cat in self._setting_category_list:
            for setting in cat.getSettings():
                if setting.getValue() != setting.getDefault():
                    config_parser.set(section_name, setting.getKey(), setting.getValue())

    def loadSettingsFromConfigParser(self, config_parser, section_name):
        if config_parser.has_section(section_name):
            for cat in self._setting_category_list:
                for setting in cat.getSettings():
                    if config_parser.has_option(section_name, setting.getKey()):
                        setting.setValue(config_parser.get(section_name, setting.getKey()))

    def onSettingUpdated(self):
        """
        Event that is called whenever a setting is updated. Trigger a new engine action on this, but with a slight delay.
        """
        if self._translator is not None:
            self._translator.trigger()

    def setTranslator(self, translator):
        self._translator = translator
