__author__ = 'Jaime van Kessel'

from Cura.machine import settingValidators
import types


class SettingCategory(object):
    def __init__(self, key, icon=None):
        self._key = key
        self._label = key
        self._tooltip = ''
        self._icon = icon
        self._visible = True
        self._settings = []

    def setLabel(self, label, tooltip=''):
        self._label = label
        self._tooltip = tooltip
        return self

    def setVisible(self, visible):
        self._visible = visible
        return self

    def getVisible(self):
        return self._visible

    def addSetting(self, setting):
        self._settings.append(setting)

    def getSettingByKey(self, key):
        for s in self._settings:
            ret = s.getSettingByKey(key)
            if ret is not None:
                return ret
        return None

    def getName(self):
        return self._name

    def getKey(self):
        return self._key

    def getIcon(self):
        return self._icon


class Setting(object):
    """
        A setting object contains a (single) configuration setting.
        Settings have validators that check if the value is valid, but do not prevent invalid values!
        Settings have conditions that enable/disable this setting depending on other settings. (Ex: Dual-extrusion)
    """
    def __init__(self, key, default, type):
        self._key = key
        self._label = key
        self._tooltip = ''
        self._default = unicode(default)
        self._value = None
        self._type = type
        self._visible = True
        self._validators = []
        self._conditions = []
        self._parent_setting = None
        self._copy_from_parent_function = lambda value: value
        self._child_settings = []

        if type == 'float':
            settingValidators.validFloat(self)
        elif type == 'int':
            settingValidators.validInt(self)

    def addSetting(self, setting):
        setting._parent_setting = self
        self._child_settings.append(setting)

    def getSettingByKey(self, key):
        if self._key == key:
            return self
        for s in self._child_settings:
            ret = s.getSettingByKey(key)
            if ret is not None:
                return ret
        return None

    def setVisible(self, visible):
        self._visible = visible
        return self

    def getVisible(self):
        return self._visible

    def setLabel(self, label, tooltip=''):
        self._label = label
        self._tooltip = tooltip
        return self

    def setRange(self, minValue=None, maxValue=None):
        if len(self._validators) < 1:
            return
        self._validators[0].minValue = minValue
        self._validators[0].maxValue = maxValue
        return self

    def getLabel(self):
        return self._label

    def getTooltip(self):
        return self._tooltip

    def getKey(self):
        return self._key

    def getType(self):
        return self._type

    def getValue(self):
        if self._value is None:
            return self._default
        return self._value

    def getDefault(self):
        return self._default

    def setValue(self, value):
        self._value = value

    def validate(self):
        result = settingValidators.SUCCESS
        msgs = []
        for validator in self._validators:
            res, err = validator.validate()
            if res == settingValidators.ERROR:
                result = res
            elif res == settingValidators.WARNING and result != settingValidators.ERROR:
                result = res
            if res != settingValidators.SUCCESS:
                msgs.append(err)
        return result, '\n'.join(msgs)

    def addCondition(self, conditionFunction):
        self._conditions.append(conditionFunction)

    def checkConditions(self):
        for condition in self._conditions:
            if not condition():
                return False
        return True
