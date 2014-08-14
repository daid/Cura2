import wx

from Cura import preferences
from Cura.gui.settingPanel import SettingPanel
from Cura.gui.floatSizer import FloatingPanel
from Cura.gui.widgets.profileCategoryButton import ProfileCategoryButton
from Cura.gui.widgets.innerTitleBar import InnerTitleBar
from Cura.gui.widgets.printSaveButton import PrintSaveButton


class ProfilePanel(FloatingPanel):
    """
    Always visible side panel which contains all the categories from the machine settings.
    This panel can be collapsed into icons or used normal sized to have text as well as icons.
    """
    def __init__(self, parent, app):
        super(ProfilePanel, self).__init__(parent)

        self._app = app
        self._buttons = []
        self._panels = []

        sizer = wx.BoxSizer(wx.VERTICAL)
        self._titleBar = InnerTitleBar(self, 'Profile')
        self._titleBar.Bind(wx.EVT_LEFT_DOWN, self.onSmallToggle)
        sizer.Add(self._titleBar, flag=wx.EXPAND)

        n = 0
        for c in self._app.getMachine().getSettingCategories():
            if not c.isVisible():
                continue
            # Filter out categories that do not have visible settings.
            if len(filter(lambda s: s.isVisible(), c.getSettings())) < 1:
                continue
            b = ProfileCategoryButton(self, c.getLabel(), c.getIcon())
            b.category = c
            b.Bind(wx.EVT_BUTTON, self.onCategoryButton)
            self._buttons.append(b)
            p = SettingPanel(self, self._app, c)
            self._panels.append(p)

            # n += 1
            # if n % 4 == 0:
            #     sizer.Add(wx.StaticLine(self), flag=wx.EXPAND)

        self._pluginsButton = ProfileCategoryButton(self, 'Plugins', 'icon_plugin.png')
        self._pluginsButton.Hide()
        self._loadProfileButton = ProfileCategoryButton(self, 'Load profile', 'icon_load_profile.png')
        self._loadProfileButton.Hide()
        self._saveButton = PrintSaveButton(self, app)
        self._pluginsButton.Bind(wx.EVT_BUTTON, self.onPluginButton)
        self._loadProfileButton.Bind(wx.EVT_BUTTON, self.onLoadProfileButton)

        sizer.Add(self._pluginsButton, flag=wx.EXPAND)
        sizer.Add(self._loadProfileButton, flag=wx.EXPAND)
        sizer.Add(self._saveButton, flag=wx.EXPAND)
        self.SetSizer(sizer)
        self.setSmall(preferences.getPreference('profile_small', 'False') == 'True')
        self._updateSizer()

    def _updateSizer(self):
        sizer = self.GetSizer()
        for item in sizer.GetChildren():
            sizer.Detach(item.GetWindow())
        sizer.Add(self._titleBar, flag=wx.EXPAND)
        for n in xrange(0, len(self._buttons)):
            if not self._buttons[n].IsShown():
                continue
            sizer.Add(self._buttons[n], flag=wx.EXPAND)
            if self._buttons[n].GetValue():
                sizer.Add(self._panels[n], flag=wx.EXPAND)
                self._panels[n].Layout()
                self._panels[n].Show()
            else:
                self._panels[n].Hide()
        sizer.Add(self._saveButton, flag=wx.EXPAND)
        self.Parent.Layout()
        self.Layout() #because on linux the layout stuff doesn't bubble down. Screw you wxwidgets.

    def onSmallToggle(self, e):
        self.setSmall(not self._titleBar.isSmall())
        self.Fit()
        self.Parent.Layout()
        self.Layout() #because on linux the layout stuff doesn't bubble down. Screw you wxwidgets.

    def setSmall(self, small):
        self._titleBar.setSmall(small)
        for button in self._buttons:
            button.setSmall(small)
        self._pluginsButton.setSmall(small)
        self._loadProfileButton.setSmall(small)
        self._saveButton.setSmall(small)
        if small:
            self._titleBar.setIcon('inner_title_bar_open_arrow.png')
        else:
            self._titleBar.setIcon('inner_title_bar_close_arrow.png')
        preferences.setPreference('profile_small', str(small))

    def onCategoryButton(self, e):
        self._updateSizer()

    def onPluginButton(self, e):
        if self._pluginsButton.GetValue():
            pass

    def onLoadProfileButton(self, e):
        self._loadProfileButton.SetValue(False)
