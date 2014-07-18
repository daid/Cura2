import wx
import os

from Cura import preferences
from Cura.removableStorage import getStorageDevices
from Cura.gui.floatSizer import FloatingPanel
from Cura.gui.widgets.profileCategoryButton import ProfileCategoryButton
from Cura.gui.widgets.innerTitleBar import InnerTitleBar
from Cura.gui.widgets.gradientButton import GradientButton


class PrintSaveButton(GradientButton):
    # TODO: This does not belong here. Move to seperate file
    def __init__(self, parent, app):
        self._app = app
        super(PrintSaveButton, self).__init__(parent, label='Save on', icon='save_button.png', icon_align=wx.ALIGN_RIGHT)
        app.getTranslator().addProgressCallback(self._onProgressUpdate)
        self.Bind(wx.EVT_BUTTON, self._onSaveClick)
        self._updateButton()

    def _onProgressUpdate(self, progress, ready):
        self.setFillAmount(progress)
        self.Enable(ready)

        self._updateButton()

    def _updateButton(self):
        if len(getStorageDevices()) > 0:
            self.SetLabel('Save on')
            self.setIcon('save_sd_button.png')
        else:
            self.SetLabel('Save')
            self.setIcon('save_button.png')

    def _onSaveClick(self, e):
        storage_devices = getStorageDevices()
        if len(storage_devices) > 0:
            if len(storage_devices) == 1:
                path = storage_devices[0][1]
            else:
                dlg = wx.SingleChoiceDialog(self, _("Select SD drive"), _("Multiple removable drives have been found,\nplease select your SD card drive"), map(lambda n: n[0], storage_devices))
                if dlg.ShowModal() != wx.ID_OK:
                    dlg.Destroy()
                    return
                path = storage_devices[dlg.GetSelection()][1]
                dlg.Destroy()
            filename = os.path.join(path, self._app.getScene().getResult().getDefaultFilename())

            with open(filename, "wb") as f:
                f.write(self._app.getScene().getResult().getGCode())
            self._app.showNotification('Saved', 'Saved as %s' % (filename))
        else:
            dlg = wx.FileDialog(self, _("Save toolpath"), style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            dlg.SetFilename(self._app.getScene().getResult().getDefaultFilename())
            dlg.SetWildcard('Toolpath (*.gcode)|*.gcode')
            if dlg.ShowModal() != wx.ID_OK:
                dlg.Destroy()
                return
            filename = dlg.GetPath()
            dlg.Destroy()

            with open(filename, "wb") as f:
                f.write(self._app.getScene().getResult().getGCode())

    def __del__(self):
        self._app.getTranslator().removeProgressCallback(self._onProgressUpdate)


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

    def onSmallToggle(self, e):
        self.setSmall(not self._titleBar.isSmall())
        self.Fit()
        self.Parent.Layout()
        self.Layout() #because on linux the layout stuff doesn't bubble down. Screw you wxwidgets.

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
