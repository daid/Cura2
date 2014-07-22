import wx
import os
import threading

from Cura.removableStorage import getStorageDevices
from Cura.removableStorage import ejectDrive
from Cura.gui.widgets.gradientButton import GradientButton


class PrintSaveButton(GradientButton):
    def __init__(self, parent, app):
        self._app = app
        super(PrintSaveButton, self).__init__(parent, label='Save on', icon='save_button.png', icon_align=wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_BUTTON, self._onSaveClick)
        self._updateButton()
        app.getTranslator().addProgressCallback(self._onProgressUpdate)
        self._timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._updateButton)
        self._timer.Start(2000)

    def _onProgressUpdate(self, progress, ready):
        self.setFillAmount(progress)
        self.Enable(ready)
        if ready:
            self._updateButton()

    def _updateButton(self, e=None):
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
            self._app.showNotification('Saved', 'Saved as %s' % (filename), lambda : threading.Thread(target=self._eject, args=(path,)).start())
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

    def _eject(self, drive):
        ejectDrive(drive)
        self._app.showNotification('Ejected', 'You can now remove the card')

    def __del__(self):
        self._app.getTranslator().removeProgressCallback(self._onProgressUpdate)
