import wx

from Cura import preferences
from Cura.gui.floatSizer import FloatingPanel
from Cura.gui.widgets.profileCategoryButton import ProfileCategoryButton
from Cura.gui.widgets.innerTitleBar import InnerTitleBar
from Cura.gui.widgets.gradientButton import GradientButton


class PrintSaveButton(GradientButton):
    # TODO: This does not belong here. Move to seperate file
    def __init__(self, parent, app):
        self._app = app
        super(PrintSaveButton, self).__init__(parent, label='Save GCode')
        app.getTranslator().addProgressCallback(self._onProgressUpdate)
        self.Bind(wx.EVT_BUTTON, self._onSaveClick)

    def _onProgressUpdate(self, progress, ready):
        self.setFillAmount(progress)

    def _onSaveClick(self, e):
        # TODO: USB print, SD save
        dlg = wx.FileDialog(self, _("Save toolpath"), style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        dlg.SetWildcard('Toolpath (*.gcode)|*.gcode')
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return
        filename = dlg.GetPath()
        dlg.Destroy()

        with open(filename, "wb") as f:
            f.write(self._app.getScene().getResult().getGCode())


class ProfilePanel(FloatingPanel):
    """
    Always visible side panel which contains all the categories from the machine settings.
    This panel can be collapsed into icons or used normal sized to have text as well as icons.
    """
    def __init__(self, parent, app):
        super(ProfilePanel, self).__init__(parent)

        self._app = app
        self._categoryButtons = []

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
            sizer.Add(b, flag=wx.EXPAND)
            b.Bind(wx.EVT_BUTTON, self.onCategoryButton)
            self._categoryButtons.append(b)

            n += 1
            if n % 4 == 0:
                sizer.Add(wx.StaticLine(self), flag=wx.EXPAND)

        self._pluginsButton = ProfileCategoryButton(self, 'Plugins', 'icon_plugin.png')
        self._loadProfileButton = ProfileCategoryButton(self, 'Load profile', 'icon_load_profile.png')
        self._saveButton = PrintSaveButton(self, app)
        self._pluginsButton.Bind(wx.EVT_BUTTON, self.onPluginButton)
        self._loadProfileButton.Bind(wx.EVT_BUTTON, self.onLoadProfileButton)
        sizer.Add(self._pluginsButton, flag=wx.EXPAND)
        sizer.Add(self._loadProfileButton, flag=wx.EXPAND)
        sizer.Add(self._saveButton, flag=wx.EXPAND)
        self.SetSizer(sizer)
        self.setSmall(preferences.getPreference('profile_small', 'False') == 'True')

    def onSmallToggle(self, e):
        self.setSmall(not self._titleBar.isSmall())
        self.Fit()
        self.Parent.Layout()

    def setSmall(self, small):
        self._titleBar.setSmall(small)
        for button in self._categoryButtons:
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
        button = e.GetEventObject()
        if not button.GetValue():
            button = None
        for b in self._categoryButtons:
            if b != button:
                b.SetValue(False)
        self._pluginsButton.SetValue(False)
        if button is None:
            self._app.getMainWindow().closeSettings()
        else:
            self._app.getMainWindow().openSettingCategory(button)

    def onPluginButton(self, e):
        for b in self._categoryButtons:
            b.SetValue(False)
        self._app.getMainWindow().closeSettings()
        if self._pluginsButton.GetValue():
            pass

    def onLoadProfileButton(self, e):
        self._loadProfileButton.SetValue(False)
