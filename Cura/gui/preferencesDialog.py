import wx
from wx.lib.agw.customtreectrl import CustomTreeCtrl
from wx.lib.agw.customtreectrl import EVT_TREE_ITEM_CHECKED


class MachineViewCustomizeDialog(wx.Dialog):
    def __init__(self, parent, app, setting_view_preset):
        self._app = app
        self._setting_view_preset = setting_view_preset
        super(MachineViewCustomizeDialog, self).__init__(parent, title='Settings', size=(500, 600))

        self._settings_tree = CustomTreeCtrl(self, style=wx.BORDER_SIMPLE, agwStyle=wx.TR_HAS_BUTTONS|wx.TR_HIDE_ROOT)
        self.Bind(EVT_TREE_ITEM_CHECKED, self._onItemChecked, self._settings_tree)
        root_node = self._settings_tree.AddRoot('root')
        for category in self._app.getMachine().getSettingCategories():
            if not category.isVisible():
                continue
            category_node = self._settings_tree.AppendItem(root_node, category.getLabel())
            category_node.Expand()
            for child in category.getChildren():
                self._addSettingNode(category_node, child)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        sizer.Add(self._settings_tree, 1, flag=wx.EXPAND)

    def _addSettingNode(self, parent_node, setting):
        setting_node = self._settings_tree.AppendItem(parent_node, setting.getLabel(), ct_type=1)
        #setting_node.Set3State(True)
        setting_node.setting = setting
        if self._setting_view_preset.isSettingVisible(setting.getKey()):
            setting_node.Check(True)
        for child in setting.getChildren():
            self._addSettingNode(setting_node, child)
        setting_node.Expand()

    def _onItemChecked(self, e):
        item = e.GetItem()
        if item.GetValue():
            self._setting_view_preset.setSettingVisible(item.setting.getKey(), True)
        else:
            self._setting_view_preset.setSettingVisible(item.setting.getKey(), False)


class PreferencesDialog(wx.Dialog):
    def __init__(self, app):
        self._app = app
        super(PreferencesDialog, self).__init__(app.getMainWindow(), title='Settings')
        self._main_panel = wx.Panel(self)
        self._bottom_panel = wx.Panel(self)
        self.SetSizer(wx.BoxSizer(wx.VERTICAL))
        self.GetSizer().Add(self._main_panel, 1, wx.EXPAND)
        self.GetSizer().Add(wx.StaticLine(self), 0, wx.EXPAND)
        self.GetSizer().Add(self._bottom_panel, 0, wx.EXPAND)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._bottom_panel.SetSizer(sizer)
        self._close_button = wx.Button(self._bottom_panel, -1, 'Ok')
        sizer.Add(wx.Panel(self._bottom_panel), 1)
        sizer.Add(self._close_button, 0, border=5, flag=wx.ALL)
        self.Bind(wx.EVT_BUTTON, self.onCloseButton, self._close_button)

        sizer = wx.GridBagSizer(2, 2)
        self._main_panel.SetSizer(sizer)
        setting_view_options = map(lambda svp: svp.getName(), self._app.getSettingsViewPresets())
        setting_view_options.append('+Add custom')
        self._setting_view_selection = wx.ComboBox(self._main_panel, choices=setting_view_options, style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self._setting_view_selection.SetSelection(self._app.getSettingsViewPresets().index(self._app.getActiveSettingsViewPreset()))
        self._setting_view_customize = wx.Button(self._main_panel, label='Customize')
        sizer.Add(wx.StaticText(self._main_panel, -1, 'Settings view preset'), pos=(0, 0), border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self._setting_view_selection, pos=(0, 1), border=5, flag=wx.ALL | wx.EXPAND)
        sizer.Add(self._setting_view_customize, pos=(0, 2), border=5, flag=wx.ALL)
        sizer.AddGrowableCol(1)

        self._main_panel.Layout()

        self.Bind(wx.EVT_BUTTON, self.onCustomizeButton, self._setting_view_customize)

    def onCloseButton(self, e):
        self._app.setActiveSettingsView(self._app.getSettingsViewPresets()[self._setting_view_selection.GetSelection()])
        self.Close()

    def onCustomizeButton(self, e):
        MachineViewCustomizeDialog(self, self._app, self._app.getSettingsViewPresets()[self._setting_view_selection.GetSelection()]).ShowModal()
