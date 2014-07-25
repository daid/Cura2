
import wx
import os
from threading import Thread
from time import sleep

from Cura.meshLoaders import meshLoader
from Cura.gui.widgets.machineButton import MachineButton
from Cura.gui.widgets.innerTitleBar import InnerTitleBar
from Cura.gui.floatSizer import FloatingPanel
from Cura.resources import getBitmap
from Cura.preferences import getPreference
from Cura.preferences import setPreference


class FileBrowserPanel(FloatingPanel):
    def __init__(self, parent, app):
        super(FileBrowserPanel, self).__init__(parent)
        self._app = app
        self.SetSize((185, 400))
        self._local_file_panel = wx.Panel(self)
        self._machine_button = MachineButton(self, app)

        self._load_button = wx.StaticBitmap(self._local_file_panel, bitmap=getBitmap('icon_open_model.png'))
        self._local_file_list = wx.ListBox(self._local_file_panel, size=(164, 248))
        sizer = wx.GridBagSizer(2, 2)
        sizer.Add(self._load_button, (0, 0), border=10, flag=wx.LEFT|wx.RIGHT|wx.TOP|wx.ALIGN_RIGHT)
        sizer.Add(self._local_file_list, (1, 0), border=10, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM)
        self._local_file_panel.SetSizer(sizer)

        self._load_button.Bind(wx.EVT_LEFT_DOWN, self._onLoadFile)
        self._local_file_list.Bind(wx.EVT_LEFT_DCLICK, self._onLocalFileDoubleClick)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        sizer.Add(InnerTitleBar(self, 'File browsing'), flag=wx.EXPAND)
        sizer.Add(self._local_file_panel)
        sizer.Add(self._machine_button, flag=wx.EXPAND)

        t = Thread(target=self._watchPathsThread)
        t.daemon = True
        t.start()

    def _onLoadFile(self, e):
        dlg = wx.FileDialog(self, _("Open 3D model"), style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST|wx.FD_MULTIPLE)

        wildcardList = ';'.join(map(lambda s: '*' + s, meshLoader.loadSupportedExtensions()))
        wildcardFilter = "All (%s)|%s;%s" % (wildcardList, wildcardList, wildcardList.upper())
        wildcardList = ';'.join(map(lambda s: '*' + s, meshLoader.loadSupportedExtensions()))
        wildcardFilter += "|Mesh files (%s)|%s;%s" % (wildcardList, wildcardList, wildcardList.upper())

        dlg.SetWildcard(wildcardFilter)
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return
        filenames = dlg.GetPaths()
        dlg.Destroy()
        if len(filenames) < 1:
            return

        for filename in filenames:
            self._app.getScene().loadFile(filename)
            setPreference('last_file_path', os.path.dirname(filename))
            self._timeout = 0

    def _onLocalFileDoubleClick(self, e):
        if self._local_file_list.GetSelection() >= 0:
            filename = self._local_file_list.full_filename_list[self._local_file_list.GetSelection()]
            self._app.getScene().loadFile(filename)

    def _updateFileList(self, files):
        selection = self._local_file_list.GetSelection()
        self._local_file_list.full_filename_list = files
        self._local_file_list.Set(map(os.path.basename, files))
        self._local_file_list.SetSelection(selection)

    def _watchPathsThread(self):
        supported_extensions = meshLoader.loadSupportedExtensions()
        while True:
            path = getPreference('last_file_path', '')
            fileList = []
            try:
                for file in os.listdir(path):
                    _, ext = os.path.splitext(file)
                    if ext.lower() not in supported_extensions:
                        continue
                    try:
                        info = os.stat(os.path.join(path, file))
                        fileList.append((info.st_mtime, os.path.join(path, file)))
                    except:
                        pass
            except:
                pass
            fileList.sort(reverse=True)
            wx.CallAfter(self._updateFileList, map(lambda n: n[1], fileList[:20]))
            self._timeout = 50
            while self._timeout > 0:
                sleep(0.1)
                if not self:
                    return
                self._timeout -= 1
