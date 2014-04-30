import wx

from Cura.gui.floatSizer import FloatSizer
from Cura.gui.floatSizer import FloatingPanel
from Cura.gui.openGLPanel import OpenGLPanel
from Cura.gui.profilePanel import ProfilePanel
from Cura.gui.settingPanel import SettingPanel
from Cura.gui.topBar import TopBarLeft
from Cura.gui.topBar import TopBarRight


class MainOpenGLView(OpenGLPanel):
    def __init__(self, parent, app):
        self._app = app
        super(MainOpenGLView, self).__init__(parent)
        self.Bind(wx.EVT_MOTION, self.onMouseMotion)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)

    def onRender(self):
        self._app.getView().render(self)

    def onMouseMotion(self, e):
        if e.Dragging():
            self._app.getView().setYaw(self._app.getView().getYaw() + e.GetX() - self._mouseX)
            self._app.getView().setPitch(self._app.getView().getPitch() - e.GetY() + self._mouseY)
        self._mouseX = e.GetX()
        self._mouseY = e.GetY()

    def OnMouseWheel(self, e):
        delta = float(e.GetWheelRotation()) / float(e.GetWheelDelta())
        delta = max(min(delta, 4), -4)
        self._app.getView().deltaZoom(delta)


class NotificationPanel(FloatingPanel):
    def __init__(self, parent):
        super(NotificationPanel, self).__init__(parent)
        self.SetBackgroundColour((160, 160, 160))
        self._title = wx.StaticText(self, label='Big and bold')
        self._info = wx.StaticText(self, label='That\'s what she said,\n!!!')

        f = self._title.GetFont()
        self._title.SetFont(wx.Font(f.PointSize * 2, f.Family, f.Style, wx.FONTWEIGHT_BOLD, False, f.FaceName))
        self._title.SetForegroundColour((255, 255, 255))
        self._info.SetForegroundColour((255, 255, 255))
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._title, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=16)
        sizer.Add(wx.StaticLine(self), flag=wx.TOP|wx.LEFT|wx.RIGHT, border=4)
        sizer.Add(self._info, flag=wx.BOTTOM|wx.LEFT|wx.RIGHT, border=16)
        self.SetSizer(sizer)

        self.Hide()


class MainWindow(wx.Frame):
    def __init__(self, app):
        super(MainWindow, self).__init__(None, title='Cura - Pink Unicorn edition')
        self._app = app

        self._mainView = MainOpenGLView(self, app)
        self._settingsPanel = None
        self._topBarLeft = TopBarLeft(self._mainView, app)
        self._topBarRight = TopBarRight(self._mainView, app)
        self._app.getView().setOpenGLWindow(self._mainView)

        self._fileBrowser = FloatingPanel(self._mainView)
        self._fileBrowser.SetSize((185, 400))
        self._fileBrowser.SetBackgroundColour(wx.GREEN)
        self._fileBrowser.Show()

        self._toolsPanel = FloatingPanel(self._mainView)
        self._toolsPanel.SetSize((165, 54))
        self._toolsPanel.SetBackgroundColour(wx.BLUE)

        self._printProfilePanel = ProfilePanel(self._mainView, app)
        self._printProfilePanel.Fit()
        self._printProfilePanel.SetPosition((600, 32))

        self._notification = NotificationPanel(self._mainView)

        self._mainSizer = wx.BoxSizer(wx.VERTICAL)
        self._mainSizer.Add(self._mainView, 1, wx.EXPAND)
        self.SetSizer(self._mainSizer)

        self._floatSizer = FloatSizer(self)
        self._floatSizer.Add(self._toolsPanel, userData={'top': 0})
        self._floatSizer.Add(self._topBarLeft, userData={'top': 0, 'left': 0, 'width': 0.5})
        self._floatSizer.Add(self._topBarRight, userData={'top': 0, 'right': 0, 'width': 0.5})
        self._floatSizer.Add(self._fileBrowser, userData={'left': 0, 'top': 72})
        self._floatSizer.Add(self._printProfilePanel, userData={'right': 0, 'top': 72})
        self._floatSizer.Add(self._notification, userData={'bottom': 32})
        self._mainView.SetSizer(self._floatSizer)
        self.SetMinSize((300, 300))

        self.Bind(wx.EVT_MOVE, self._onMove)

    def closeSettings(self):
        if self._settingsPanel is not None:
            self._floatSizer.Detach(self._settingsPanel)
            self._settingsPanel.Destroy()
            self._settingsPanel = None
            self._mainView.Refresh()

    def openSettingCategory(self, categoryButton):
        category = categoryButton.category
        self.closeSettings()

        self._settingsPanel = SettingPanel(self._mainView, self._app, category)
        self._floatSizer.Add(self._settingsPanel, userData={'right': self._printProfilePanel, 'top': 72 + categoryButton.GetPosition()[1]})
        self._mainView.Layout()

    def _onMove(self, e):
        self._mainView.Layout()
