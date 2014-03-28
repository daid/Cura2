__author__ = 'Jaime van Kessel'

from Cura.machine import settingValidators
import types

class Setting(object):
    """
        A setting object contains a (single) configuration setting.
        Settings have validators that check if the value is valid, but do not prevent invalid values!
        Settings have conditions that enable/disable this setting depending on other settings. (Ex: Dual-extrusion)
    """
    def __init__(self, name, default, type, category= '', subcategory = ''):
        self._name = name
        self._label = name
        self._tooltip = ''
        self._default = unicode(default)
        self._value = None
        self._type = type
        self._category = category
        self._subcategory = subcategory
        self._validators = []
        self._conditions = []

        if type is types.FloatType:
            settingValidators.validFloat(self)
        elif type is types.IntType:
            settingValidators.validInt(self)

    def setLabel(self, label, tooltip = ''):
        self._label = label
        self._tooltip = tooltip
        return self

    def setRange(self, minValue = None, maxValue = None):
        if len(self._validators) < 1:
            return
        self._validators[0].minValue = minValue
        self._validators[0].maxValue = maxValue
        return self

    def getLabel(self):
        return self._label

    def getTooltip(self):
        return self._tooltip

    def getCategory(self):
        return self._category

    def getSubCategory(self):
        return self._subcategory

    def getName(self):
        return self._name

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
