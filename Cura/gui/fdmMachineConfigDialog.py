
import wx
from Cura.meshLoaders import meshLoader
from Cura.gui.widgets.gcodeTextArea import GcodeTextArea


class FDMMachineConfigDialog(wx.Dialog):
    def __init__(self, app):
        self._app = app
        super(FDMMachineConfigDialog, self).__init__(app.getMainWindow(), title='Machine Settings')
        self._tabs = wx.Notebook(self)
        self._tabs.SetMinSize((500, -1))
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
        nozzle_count_ctrl = self.addSetting(self._main_panel, self._app.getMachine().getSettingByKey('machine_nozzle_count'), 4)
        self.addSetting(self._main_panel, self._app.getMachine().getSettingByKey('machine_heated_bed'), 5)

        self.addSetting(self._main_panel, self._app.getMachine().getSettingByKey('machine_center_is_zero'), 7)
        self.addSetting(self._main_panel, self._app.getMachine().getSettingByKey('machine_build_area_shape'), 8)
        self.addSetting(self._main_panel, self._app.getMachine().getSettingByKey('display_model'), 10)

        sizer = wx.GridBagSizer(2, 2)
        self._head_panel.SetSizer(sizer)
        self.addSetting(self._head_panel, self._app.getMachine().getSettingByKey('machine_head_shape_min_x'), 0)
        self.addSetting(self._head_panel, self._app.getMachine().getSettingByKey('machine_head_shape_min_y'), 1)
        self.addSetting(self._head_panel, self._app.getMachine().getSettingByKey('machine_head_shape_max_x'), 2)
        self.addSetting(self._head_panel, self._app.getMachine().getSettingByKey('machine_head_shape_max_y'), 3)
        self.addSetting(self._head_panel, self._app.getMachine().getSettingByKey('machine_nozzle_gantry_distance'), 4)
        self._nozzle_controls = []
        for n in xrange(1, self._app.getMachine().getMaxNozzles()):
            controls = []
            controls.append(self.addSetting(self._head_panel, self._app.getMachine().getSettingByKey('machine_nozzle_offset_x_%d' % (n)), n * 2 - 2, 1))
            controls.append(self.addSetting(self._head_panel, self._app.getMachine().getSettingByKey('machine_nozzle_offset_y_%d' % (n)), n * 2 - 1, 1))
            self._nozzle_controls.append(controls)

        self.addGCodeTab(self._app.getMachine().getSettingByKey('machine_start_gcode'))
        self.addGCodeTab(self._app.getMachine().getSettingByKey('machine_end_gcode'))

        self.Fit()
        self.Centre()

        self._onNozzleCountChange()

        nozzle_count_ctrl.Bind(wx.EVT_COMBOBOX, self._onNozzleCountChange)

    def _onNozzleCountChange(self, e=None):
        if e is not None:
            self.onComboSettingChange(e)
        nozzle_count = int(self._app.getMachine().getSettingValueByKey('machine_nozzle_count'))
        for n in xrange(0, len(self._nozzle_controls)):
            for ctrl in self._nozzle_controls[n]:
                ctrl.label.Show((n + 1) < nozzle_count)
                ctrl.Show((n + 1) < nozzle_count)

    def addSetting(self, panel, s, x, y=0):
        if not s.isVisible():
            return
        flag = wx.EXPAND
        if s.getType() == 'float' or s.getType() == 'int':
            ctrl = wx.TextCtrl(panel, value=s.getValue())
            ctrl.Bind(wx.EVT_TEXT, self.onSettingChange)
        elif s.getType() == 'bool':
            ctrl = wx.CheckBox(panel, style=wx.ALIGN_RIGHT)
            ctrl.SetValue(s.getValue() == 'True')
            ctrl.Bind(wx.EVT_CHECKBOX, self.onSettingChange)
            flag = 0
        elif s.getType() == 'filename':
            ctrl = wx.Button(panel, -1, _('Browse'))
            ctrl.Bind(wx.EVT_BUTTON, self.onBrowse)
        elif isinstance(s.getType(), dict):
            try:
                value = s.getType()[s.getValue()]
            except KeyError:
                value = s.getType().values()[0]
            choices = s.getType().values()
            choices.sort()
            ctrl = wx.ComboBox(panel, value=value, choices=choices, style=wx.CB_DROPDOWN|wx.CB_READONLY)
            ctrl.Bind(wx.EVT_COMBOBOX, self.onComboSettingChange)
            ctrl.Bind(wx.EVT_LEFT_DOWN, self.OnMouseExit)
        else:
            print 'Unknown settings type:', s.getType()
            ctrl = wx.TextCtrl(panel, value=s.getValue())

        label = wx.StaticText(panel, label=s.getLabel())
        ctrl.label = label
        ctrl.setting = s
        sizer = panel.GetSizer()
        if y == 0:
            sizer.Add(wx.Panel(panel, size=(10, 10)), pos=(x, 0), span=(1, 1))
        sizer.Add(label, pos=(x, y * 3 + 1), span=(1, 1), flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(ctrl, pos=(x, y * 3 + 2), span=(1, 1), flag=flag)
        sizer.Add(wx.Panel(panel, size=(10, 10)), pos=(x, y * 3 + 3), span=(1, 1))

        ctrl.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEnter)
        ctrl.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseExit)
        return ctrl

    def addGCodeTab(self, setting):
        textArea = GcodeTextArea(self._tabs)
        textArea.SetValue(setting.getValue())
        textArea.setting = setting
        textArea.Bind(wx.EVT_KILL_FOCUS, self.onSettingChange, textArea)
        textArea.Bind(wx.stc.EVT_STC_CHANGE, self.onSettingChange, textArea)
        self._tabs.AddPage(textArea, setting.getLabel())

    def onSettingChange(self, e):
        ctrl = e.GetEventObject()
        ctrl.setting.setValue(ctrl.GetValue())

    def onComboSettingChange(self, e):
        ctrl = e.GetEventObject()
        for k, v in ctrl.setting.getType().items():
            if v == ctrl.GetValue():
                ctrl.setting.setValue(k)
                return

    def onBrowse(self, e):
        ctrl = e.GetEventObject()

        dlg = wx.FileDialog(self, _("Open 3D model"), style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        wildcardList = ';'.join(map(lambda s: '*' + s, meshLoader.loadSupportedExtensions()))
        wildcardFilter = "All (%s)|%s;%s" % (wildcardList, wildcardList, wildcardList.upper())
        wildcardList = ';'.join(map(lambda s: '*' + s, meshLoader.loadSupportedExtensions()))
        wildcardFilter += "|Mesh files (%s)|%s;%s" % (wildcardList, wildcardList, wildcardList.upper())

        dlg.SetWildcard(wildcardFilter)
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return
        ctrl.setting.setValue(dlg.GetPath())
        dlg.Destroy()

    def onCloseButton(self, e):
        self.Close()

    def OnMouseEnter(self, e):
        pass

    def OnMouseExit(self, e):
        e.Skip()
