import wx
from wx.lib.agw.customtreectrl import CustomTreeCtrl
from wx.lib.agw.customtreectrl import EVT_TREE_ITEM_CHECKING
from wx.lib.agw.customtreectrl import EVT_TREE_ITEM_CHECKED


class MachineViewsPanel(wx.Panel):
    def __init__(self, parent, app):
        self._app = app
        super(MachineViewsPanel, self).__init__(parent)

        self._settings_tree = CustomTreeCtrl(self, style=wx.BORDER_SIMPLE, agwStyle=wx.TR_HAS_BUTTONS|wx.TR_HIDE_ROOT)
        self.Bind(EVT_TREE_ITEM_CHECKED, self._onItemChecked, self._settings_tree)
        root_node = self._settings_tree.AddRoot('root')
        for category in self._app.getMachine().getSettingCategories():
            if not category.isVisible():
                continue
            category_node = self._settings_tree.AppendItem(root_node, category.getLabel())
            for child in category.getChildren():
                self._addSettingNode(category_node, child)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        sizer.Add(self._settings_tree, 1, flag=wx.EXPAND)

    def _addSettingNode(self, parent_node, setting):
        setting_node = self._settings_tree.AppendItem(parent_node, setting.getLabel(), ct_type=1)
        setting_node.Set3State(True)
        setting_node.setting = setting
        if setting.getVisibleProperty():
            setting_node.Set3StateValue(wx.CHK_CHECKED)
        if setting.getVisibleProperty() and not setting.isVisible():
            setting_node.Set3StateValue(wx.CHK_UNDETERMINED)
        for child in setting.getChildren():
            self._addSettingNode(setting_node, child)

    def _onItemChecked(self, e):
        item = e.GetItem()
        if item.GetValue() == wx.CHK_CHECKED:
            item.setting.setVisible(True)
            if not item.setting.isVisible():
                item.Set3StateValue(wx.CHK_UNDETERMINED)
        elif item.GetValue() == wx.CHK_UNDETERMINED:
            item.Set3StateValue(wx.CHK_UNCHECKED)
            item.setting.setVisible(False)
        else:
            item.setting.setVisible(False)
        self._checkItemState(item.GetParent())

    def _checkItemState(self, item):
        if item is None:
            return

        if item.GetValue() == wx.CHK_CHECKED:
            if not item.setting.isVisible():
                item.Set3StateValue(wx.CHK_UNDETERMINED)
                self._settings_tree.RefreshLine(item)
        elif item.GetValue() == wx.CHK_UNDETERMINED:
            if item.setting.isVisible():
                item.Set3StateValue(wx.CHK_CHECKED)
                self._settings_tree.RefreshLine(item)
        self._checkItemState(item.GetParent())


class PreferencesDialog(wx.Dialog):
    def __init__(self, app):
        self._app = app
        super(PreferencesDialog, self).__init__(app.getMainWindow(), title='Settings', size=(600, 600))
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

        cats = ['Main', 'Setting views', 'Machines']
        self._preference_category_list = wx.ListBox(self._main_panel, choices=cats)
        self._preference_category_list.SetSelection(0)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._main_panel.SetSizer(sizer)

        self._main_settings_panel = wx.Panel(self._main_panel)
        self._view_settings_panel = MachineViewsPanel(self._main_panel, self._app)
        self._machine_settings_panel = wx.Panel(self._main_panel)

        self._main_settings_panel.SetBackgroundColour(wx.RED)
        self._machine_settings_panel.SetBackgroundColour(wx.BLUE)

        sizer.Add(self._preference_category_list, 0, border=5, flag=wx.ALL | wx.EXPAND)
        sizer.Add(self._main_settings_panel, 1, border=5, flag=wx.ALL | wx.EXPAND)
        sizer.Add(self._view_settings_panel, 1, border=5, flag=wx.ALL | wx.EXPAND)
        sizer.Add(self._machine_settings_panel, 1, border=5, flag=wx.ALL | wx.EXPAND)

        self.Bind(wx.EVT_LISTBOX, self.updateSettingCategory, self._preference_category_list)
        self.updateSettingCategory()

    def updateSettingCategory(self, e=None):
        idx = self._preference_category_list.GetSelection()
        self._main_settings_panel.Show(idx == 0)
        self._view_settings_panel.Show(idx == 1)
        self._machine_settings_panel.Show(idx == 2)
        self._main_panel.Layout()

    def onCloseButton(self, e):
        self.Close()
