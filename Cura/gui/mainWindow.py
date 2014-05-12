import wx

from Cura.meshLoaders import meshLoader
from Cura.gui.floatSizer import FloatSizer
from Cura.gui.floatSizer import FloatingPanel
from Cura.gui.openGLPanel import OpenGLPanel
from Cura.gui.profilePanel import ProfilePanel
from Cura.gui.settingPanel import SettingPanel
from Cura.gui.topBar import TopBarLeft
from Cura.gui.topBar import TopBarRight
from Cura.gui.widgets.innerTitleBar import InnerTitleBar


class MainOpenGLView(OpenGLPanel):
    def __init__(self, parent, app):
        self._app = app
        super(MainOpenGLView, self).__init__(parent)
        self.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
        self.Bind(wx.EVT_LEFT_DOWN, self.onMouseDown)
        self.Bind(wx.EVT_RIGHT_DOWN, self.onMouseDown)
        self.Bind(wx.EVT_MOTION, self.onMouseMotion)
        self.Bind(wx.EVT_LEFT_UP, self.onMouseUp)
        self.Bind(wx.EVT_RIGHT_UP, self.onMouseUp)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        self._activeTool = None
        self._mousePos = (0, 0)

    def onRender(self):
        self._app.getView().render(self)

    def onKeyDown(self, e):
        for tool in self._app.getTools():
            if tool.isActive() and tool.onKeyDown(e.GetKeyCode()):
                return

    def onMouseDown(self, e):
        if self._activeTool is None:
            for tool in self._app.getTools():
                if tool.isActive() and tool.onMouseDown(e.GetX(), e.GetY(), e.GetButton()):
                    self._activeTool = tool
                    break
        self._mousePos = (e.GetX(), e.GetY())

    def onMouseMotion(self, e):
        self._app.getView().updateMousePos(e.GetX(), e.GetY())
        if self._activeTool is not None:
            dx, dy = (e.GetX() - self._mousePos[0], e.GetY() - self._mousePos[1])
            self._activeTool.onMouseMove(e.GetX(), e.GetY(), dx, dy)
        self._mousePos = (e.GetX(), e.GetY())

    def onMouseUp(self, e):
        if self._activeTool is not None:
            self._activeTool.onMouseUp(e.GetX(), e.GetY(), e.GetButton())
        if not e.LeftIsDown() and not e.RightIsDown() and not e.MiddleIsDown():
            self._activeTool = None

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

        self._hideTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._onHideTimer, self._hideTimer)
        wx.CallAfter(self.Hide)

    def _onHideTimer(self, e):
        self.Hide()

    def notify(self, title, message):
        self._title.SetLabel(title)
        self._info.SetLabel(message)
        self.Show()
        self._hideTimer.Start(10000, False)


class FileBrowserPanel(FloatingPanel):
    def __init__(self, parent, app):
        super(FileBrowserPanel, self).__init__(parent)
        self._app = app
        self.SetSize((185, 400))
        self._loadButton = wx.Button(self, label='Load')
        self._loadButton.Bind(wx.EVT_BUTTON, self._onLoadFile)

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


class ToolsPanel(FloatingPanel):
    def __init__(self, parent, app):
        self._app = app
        super(ToolsPanel, self).__init__(parent)
        self._main_panel = wx.Panel(self)
        self.SetSizer(wx.BoxSizer())
        self.GetSizer().Add(self._main_panel, 1, flag=wx.EXPAND)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self._main_panel.SetSizer(sizer)
        # TODO: Get tool panel title from app.
        sizer.Add(InnerTitleBar(self._main_panel, 'Transform model'), flag=wx.EXPAND)
        self._tools_panel = wx.Panel(self._main_panel)
        sizer.Add(self._tools_panel, flag=wx.EXPAND)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._tools_panel.SetSizer(sizer)
        for tool in self._app.getTools():
            if tool.hasActiveButton():
                button = wx.Button(self._tools_panel, label=str(tool), size=(53,38))
                button.tool = tool
                button.Bind(wx.EVT_BUTTON, self.onToolButton)
                sizer.Add(button)

    def onToolButton(self, e):
        tool = e.GetEventObject().tool
        tool.setActive(not tool.isActive())
        self._app.getView().refresh()

class MainWindow(wx.Frame):
    def __init__(self, app):
        super(MainWindow, self).__init__(None, title='Cura - Pink Unicorn edition')
        self._app = app

        self._mainView = MainOpenGLView(self, app)
        self._settingsPanel = None
        self._topBarLeft = TopBarLeft(self._mainView, app)
        self._topBarRight = TopBarRight(self._mainView, app)
        self._app.getView().setOpenGLWindow(self._mainView)

        self._fileBrowser = FileBrowserPanel(self._mainView, app)

        self._toolsPanel = ToolsPanel(self._mainView, app)

        self._printProfilePanel = ProfilePanel(self._mainView, app)
        self._printProfilePanel.Fit()
        self._printProfilePanel.SetPosition((600, 32))

        self._notification = NotificationPanel(self._mainView)

        self._mainSizer = wx.BoxSizer(wx.VERTICAL)
        self._mainSizer.Add(self._mainView, 1, wx.EXPAND)
        self.SetSizer(self._mainSizer)

        self._floatSizer = FloatSizer(self)
        self._floatSizer.Add(self._toolsPanel, userData={'top': 0})
        self._floatSizer.Add(self._topBarLeft, userData={'top': 0, 'left': 0, 'width': self._toolsPanel})
        self._floatSizer.Add(self._topBarRight, userData={'top': 0, 'right': 0, 'width': self._toolsPanel})
        self._floatSizer.Add(self._fileBrowser, userData={'left': 0, 'top': 72})
        self._floatSizer.Add(self._printProfilePanel, userData={'right': 0, 'top': 72})
        self._floatSizer.Add(self._notification, userData={'bottom': 32})
        self._mainView.SetSizer(self._floatSizer)
        self.SetMinSize((500, 500))

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
