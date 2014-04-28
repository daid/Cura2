import wx

from Cura.gui.openGLPanel import OpenGLPanel
from Cura.gui.profilePanel import ProfilePanel
from Cura.gui.settingPanel import SettingPanel
from Cura.gui.topBar import TopBar


class FloatSizer(wx.PySizer):
    def __init__(self):
        wx.PySizer.__init__(self)

    def CalcMin(self):
        return wx.Size(1, 1)

    def RecalcSizes(self):
        size = self.GetSize()
        for item in self.GetChildren():
            itemSize = item.CalcMin()
            x = (size[0] - itemSize[0]) / 2
            y = (size[1] - itemSize[1]) / 2
            data = item.GetUserData()
            if 'left' in data:
                x = data['left']
            if 'top' in data:
                y = data['top']
            if 'right' in data:
                if isinstance(data['right'], wx.Window):
                    x = data['right'].GetPosition()[0] - itemSize[0]
                else:
                    x = size[0] - itemSize[0] - data['right']
            if 'bottom' in data:
                if isinstance(data['bottom'], wx.Window):
                    y = data['bottom'].GetPosition()[1] - itemSize[1]
                else:
                    y = size[1] - itemSize[1] - data['bottom']

            item.SetDimension((x, y), itemSize)


class MainOpenGLView(OpenGLPanel):
    def __init__(self, parent, app):
        self._app = app
        super(MainOpenGLView, self).__init__(parent)
        self.Bind(wx.EVT_MOTION, self.onMouseMotion)

    def onRender(self):
        self._app.getView().render(self)

    def onMouseMotion(self, e):
        if e.Dragging():
            self._app.getView().setYaw(self._app.getView().getYaw() + e.GetX() - self._mouseX)
            self._app.getView().setPitch(self._app.getView().getPitch() - e.GetY() + self._mouseY)
            self.queueRefresh()
        self._mouseX = e.GetX()
        self._mouseY = e.GetY()


class NotificationPanel(wx.Panel):
    def __init__(self, parent):
        super(NotificationPanel, self).__init__(parent, style=wx.SIMPLE_BORDER)
        self.SetBackgroundColour((160, 160, 160))
        self._title = wx.StaticText(self, label='Big and bold')
        self._info = wx.StaticText(self, label='Small and informative information,\nwhich can span multiple lines.')

        f = self._title.GetFont()
        self._title.SetFont(wx.Font(f.PointSize * 2, f.Family, f.Style, wx.FONTWEIGHT_BOLD, False, f.FaceName))
        self._title.SetForegroundColour((255, 255, 255))
        self._info.SetForegroundColour((255, 255, 255))
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._title, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=16)
        sizer.Add(wx.StaticLine(self), flag=wx.TOP|wx.LEFT|wx.RIGHT, border=4)
        sizer.Add(self._info, flag=wx.BOTTOM|wx.LEFT|wx.RIGHT, border=16)
        self.SetSizer(sizer)


class MainWindow(wx.Frame):
    def __init__(self, app):
        super(MainWindow, self).__init__(None, title='Cura - Pink Unicorn edition')
        self._app = app

        self._topbar = TopBar(self, app)
        self._mainView = MainOpenGLView(self, app)
        self._settingsPanel = None
        self._app.getView().setOpenGLWindow(self._mainView)

        self._fileBrowser = wx.Panel(self._mainView)
        self._fileBrowser.SetSize((185, 400))
        self._fileBrowser.SetBackgroundColour(wx.GREEN)

        self._transformTools = wx.Panel(self._mainView)
        self._transformTools.SetSize((165, 54))
        self._transformTools.SetBackgroundColour(wx.BLUE)

        self._printProfilePanel = ProfilePanel(self._mainView, app)
        self._printProfilePanel.Fit()
        self._printProfilePanel.SetPosition((600, 32))

        self._notification = NotificationPanel(self._mainView)

        self._mainSizer = wx.BoxSizer(wx.VERTICAL)
        self._mainSizer.Add(self._topbar, 0, wx.EXPAND)
        self._mainSizer.Add(self._mainView, 1, wx.EXPAND)
        self.SetSizer(self._mainSizer)

        self._floatSizer = FloatSizer()
        self._floatSizer.Add(self._fileBrowser, userData={'left': 0, 'top': 32})
        self._floatSizer.Add(self._printProfilePanel, userData={'right': 0, 'top': 32})
        self._floatSizer.Add(self._transformTools, userData={'top': 0})
        self._floatSizer.Add(self._notification, userData={'bottom': 32})
        self._mainView.SetSizer(self._floatSizer)

    def closeSettings(self):
        if self._settingsPanel is not None:
            self._floatSizer.Detach(self._settingsPanel)
            self._settingsPanel.Destroy()
            self._settingsPanel = None
            self._mainView.Refresh()

    def openSettingCategory(self, category):
        self.closeSettings()

        self._settingsPanel = SettingPanel(self._mainView, self._app, category)
        self._floatSizer.Add(self._settingsPanel, userData={'right': self._printProfilePanel, 'top': 32})
        self._mainView.Layout()
