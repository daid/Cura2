import wx

from Cura.gui.floatSizer import FloatingPanel
from Cura.gui.widgets.innerTitleBar import InnerTitleBar
from Cura.gui.tooltip import showTooltip
from Cura.gui.tooltip import hideTooltip

class SettingPanel(FloatingPanel):
    """
    Panel which contains configuration settings that can be changed.
    This panel is used in the main window and expanded from the side profilePanel.
    """
    def __init__(self, parent, app, category):
        super(SettingPanel, self).__init__(parent)
        self._app = app

        sizer = wx.GridBagSizer(2, 2)
        sizer.Add(InnerTitleBar(self, category.getLabel()), pos=(0, 0), span=(1, 4), flag=wx.EXPAND)
        n = 1
        for s in category.getSettings():
            if not s.isVisible():
                continue
            flag = wx.EXPAND
            if s.getType() == 'float' or s.getType() == 'int':
                ctrl = wx.TextCtrl(self, value=s.getValue())
                ctrl.Bind(wx.EVT_TEXT, self.OnSettingChange)
            elif s.getType() == 'bool':
                ctrl = wx.CheckBox(self, style=wx.ALIGN_RIGHT)
                ctrl.SetValue(s.getValue() == 'True')
                ctrl.Bind(wx.EVT_CHECKBOX, self.OnSettingChange)
                flag = 0
            elif isinstance(s.getType(), dict):
                try:
                    value = s.getType()[s.getValue()]
                except KeyError:
                    value = s.getType().values()[0]
                ctrl = wx.ComboBox(self, value=value, choices=s.getType().values(), style=wx.CB_DROPDOWN|wx.CB_READONLY)
                ctrl.Bind(wx.EVT_COMBOBOX, self.OnComboSettingChange)
                ctrl.Bind(wx.EVT_LEFT_DOWN, self.OnMouseExit)
            else:
                print 'Unknown settings type:', s.getType()
                ctrl = wx.TextCtrl(self, value=s.getValue())

            label = wx.StaticText(self, label=s.getLabel())
            ctrl.setting = s
            label.setting = s
            sizer.Add(wx.Panel(self, size=(10, 10)), pos=(n, 0), span=(1, 1))
            sizer.Add(label, pos=(n, 1), span=(1, 1), flag=wx.ALIGN_CENTER_VERTICAL)
            sizer.Add(ctrl, pos=(n, 2), span=(1, 1), flag=flag)
            sizer.Add(wx.Panel(self, size=(10, 10)), pos=(n, 3), span=(1, 1))

            ctrl.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEnter)
            ctrl.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseExit)
            label.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEnter)
            label.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseExit)

            n += 1

        sizer.Add(wx.Panel(self, size=(3, 3)), pos=(n, 0), span=(1, 4))
        self.SetSizer(sizer)

    def OnSettingChange(self, e):
        ctrl = e.GetEventObject()
        ctrl.setting.setValue(ctrl.GetValue())

    def OnComboSettingChange(self, e):
        ctrl = e.GetEventObject()
        for k, v in ctrl.setting.getType().items():
            if v == ctrl.GetValue():
                ctrl.setting.setValue(k)

    def OnMouseEnter(self, e):
        ctrl = e.GetEventObject()
        showTooltip(ctrl.setting.getTooltip(), ctrl)

    def OnMouseExit(self, e):
        ctrl = e.GetEventObject()
        hideTooltip(ctrl)
        e.Skip()
