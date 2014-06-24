
import wx
from Cura.gui.widgets.gcodeTextArea import GcodeTextArea


class FDMMachineConfigDialog(wx.Dialog):
    def __init__(self, app):
        self._app = app
        super(FDMMachineConfigDialog, self).__init__(app.getMainWindow(), title='Machine Settings')
        self._tabs = wx.Notebook(self)
        self._main_panel = wx.Panel(self._tabs)
        self._head_panel = wx.Panel(self._tabs)
        self._bottom_panel = wx.Panel(self)
        self.SetSizer(wx.BoxSizer(wx.VERTICAL))
        self.GetSizer().Add(self._tabs, 1, wx.EXPAND)
        self.GetSizer().Add(wx.StaticLine(self), 0, wx.EXPAND)
        self.GetSizer().Add(self._bottom_panel, 0, wx.EXPAND)

        self._tabs.AddPage(self._main_panel, 'Main')
        self._tabs.AddPage(self._head_panel, 'Head')

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._bottom_panel.SetSizer(sizer)
        self._close_button = wx.Button(self._bottom_panel, -1, 'Ok')
        sizer.Add(wx.Panel(self._bottom_panel), 1)
        sizer.Add(self._close_button, 0, border=5, flag=wx.ALL)
        self.Bind(wx.EVT_BUTTON, self.onCloseButton, self._close_button)

        sizer = wx.GridBagSizer(2, 2)
        self._main_panel.SetSizer(sizer)
        self.addSetting(self._main_panel, self._app.getMachine().getSettingByKey('machine_nozzle_size'), 0)
        self.addSetting(self._main_panel, self._app.getMachine().getSettingByKey('machine_width'), 1)
        self.addSetting(self._main_panel, self._app.getMachine().getSettingByKey('machine_depth'), 2)
        self.addSetting(self._main_panel, self._app.getMachine().getSettingByKey('machine_height'), 3)
        self.addSetting(self._main_panel, self._app.getMachine().getSettingByKey('machine_nozzle_count'), 4)
        self.addSetting(self._main_panel, self._app.getMachine().getSettingByKey('machine_heated_bed'), 5)

        self.addSetting(self._main_panel, self._app.getMachine().getSettingByKey('machine_center_is_zero'), 7)
        self.addSetting(self._main_panel, self._app.getMachine().getSettingByKey('machine_build_area_shape'), 8)

        sizer = wx.GridBagSizer(2, 2)
        self._head_panel.SetSizer(sizer)
        self.addSetting(self._head_panel, self._app.getMachine().getSettingByKey('machine_head_shape_min_x'), 0)
        self.addSetting(self._head_panel, self._app.getMachine().getSettingByKey('machine_head_shape_min_y'), 1)
        self.addSetting(self._head_panel, self._app.getMachine().getSettingByKey('machine_head_shape_max_x'), 2)
        self.addSetting(self._head_panel, self._app.getMachine().getSettingByKey('machine_head_shape_max_y'), 3)
        self.addSetting(self._head_panel, self._app.getMachine().getSettingByKey('machine_nozzle_gantry_distance'), 4)
        for n in xrange(1, self._app.getMachine().getMaxNozzles()):
            self.addSetting(self._head_panel, self._app.getMachine().getSettingByKey('machine_nozzle_offset_x_%d' % (n)), n * 2 - 2, 1)
            self.addSetting(self._head_panel, self._app.getMachine().getSettingByKey('machine_nozzle_offset_y_%d' % (n)), n * 2 - 1, 1)

        self.addGCodeTab(self._app.getMachine().getSettingByKey('machine_start_gcode'))
        self.addGCodeTab(self._app.getMachine().getSettingByKey('machine_end_gcode'))

        self.Fit()
        self.Centre()

    def addSetting(self, panel, s, x, y=0):
        flag = wx.EXPAND
        if s.getType() == 'float' or s.getType() == 'int':
            ctrl = wx.TextCtrl(panel, value=s.getValue())
            ctrl.Bind(wx.EVT_TEXT, self.OnSettingChange)
        elif s.getType() == 'bool':
            ctrl = wx.CheckBox(panel, style=wx.ALIGN_RIGHT)
            ctrl.SetValue(s.getValue() == 'True')
            ctrl.Bind(wx.EVT_CHECKBOX, self.OnSettingChange)
            flag = 0
        elif isinstance(s.getType(), dict):
            try:
                value = s.getType()[s.getValue()]
            except KeyError:
                value = s.getType().values()[0]
            ctrl = wx.ComboBox(panel, value=value, choices=s.getType().values(), style=wx.CB_DROPDOWN|wx.CB_READONLY)
            ctrl.Bind(wx.EVT_COMBOBOX, self.OnSettingChange)
            ctrl.Bind(wx.EVT_LEFT_DOWN, self.OnMouseExit)
        else:
            print 'Unknown settings type:', s.getType()
            ctrl = wx.TextCtrl(panel, value=s.getValue())

        ctrl.setting = s
        sizer = panel.GetSizer()
        if y == 0:
            sizer.Add(wx.Panel(panel, size=(10, 10)), pos=(x, 0), span=(1, 1))
        sizer.Add(wx.StaticText(panel, label=s.getLabel()), pos=(x, y * 3 + 1), span=(1, 1), flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(ctrl, pos=(x, y * 3 + 2), span=(1, 1), flag=flag)
        sizer.Add(wx.Panel(panel, size=(10, 10)), pos=(x, y * 3 + 3), span=(1, 1))

        ctrl.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEnter)
        ctrl.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseExit)
        return ctrl

    def addGCodeTab(self, setting):
        textArea = GcodeTextArea(self._tabs)
        textArea.SetValue(setting.getValue())
        textArea.setting = setting
        textArea.Bind(wx.EVT_KILL_FOCUS, self.OnSettingChange, textArea)
        textArea.Bind(wx.stc.EVT_STC_CHANGE, self.OnSettingChange, textArea)
        self._tabs.AddPage(textArea, setting.getLabel())

    def OnSettingChange(self, e):
        ctrl = e.GetEventObject()
        ctrl.setting.setValue(ctrl.GetValue())

    def onCloseButton(self, e):
        self.Close()

    def OnMouseEnter(self, e):
        pass

    def OnMouseExit(self, e):
        e.Skip()
