__author__ = 'Jaime van Kessel'

import threading
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

        self.addSetting('machine', Setting('machine_width', 200, 'float').setRange(0.0001))
        self.addSetting('machine', Setting('machine_height', 200, 'float').setRange(0.0001))
        self.addSetting('machine', Setting('machine_depth', 200, 'float').setRange(0.0001))
        self.addSetting('machine', Setting('machine_name', 'Machine', 'string'))
        self.addSetting('machine', Setting('machine_icon', '', 'string'))
        self.addSetting('machine', Setting('display_model', '', 'string'))

        self._machine_shape = numpy.zeros((0, 2), numpy.float32)  # Polygon that forms the 'box' around the machine

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

    def getSize(self):
        return numpy.array([self.getSettingValueByKeyFloat('machine_width'),self.getSettingValueByKeyFloat('machine_height'),self.getSettingValueByKeyFloat('machine_depth')])

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
        return ''

    def getSettingValueByKeyFloat(self, key):
        value = self.getSettingValueByKey(key)
        try:
            value = value.replace(',', '.')
            return float(eval(value, {}, {}))
        except:
            return 0.0

    def saveSettings(self, filename):
        settingsStorage = ConfigParser()
        settingsStorage.add_section('settings')
        for cat in self._setting_category_list:
            for setting in cat.getSettings():
                settingsStorage.set('settings', setting.getKey(), setting.getValue())
        with open(filename, "w") as f:
            settingsStorage.write(f)

    def loadSettings(self, filename):
        settingsStorage = ConfigParser()
        settingsStorage.read(filename)
        if settingsStorage.has_section('settings'):
            for cat in self._setting_category_list:
                for setting in cat.getSettings():
                    if settingsStorage.has_option('settings', setting.getKey()):
                        setting.setValue(settingsStorage.get('settings', setting.getKey()))

    def onSettingUpdated(self):
        """
        Event that is called whenever a setting is updated. Trigger a new engine action on this, but with a slight delay.
        """
        if self._timer is not None:
            self._timer.cancel()
        self._timer = threading.Timer(self._translatorDelay, self._onSettingUpdate)
        self._timer.start()

    def _onSettingUpdate(self):
        self._timer = None
        if self._translator is not None:
            self._translator.start()

    def setTranslator(self, translator):
        self._translator = translator
