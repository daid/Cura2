import wx

from Cura.gui.tooltip import showTooltip
from Cura.gui.tooltip import hideTooltip
from Cura.resources import getBitmap
from Cura.gui.floatSizer import FloatSizer
from Cura.gui.floatSizer import FloatingPanel
from Cura.gui.openGLPanel import OpenGLPanel
from Cura.gui.profilePanel import ProfilePanel
from Cura.gui.settingPanel import SettingPanel
from Cura.gui.topBar import TopBarLeft
from Cura.gui.topBar import TopBarRight
from Cura.gui.widgets.innerTitleBar import InnerTitleBar
from Cura.gui.widgets.toolButton import ToolButton
from Cura.gui.fileBrowser import FileBrowserPanel
from Cura.gui.tooltip import TooltipWindow


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

        focusObj = self._app.getView().getFocusObject()
        if focusObj is not None and hasattr(focusObj, 'getName') and self._activeTool is None:
            if hasattr(focusObj, 'getInfoString'):
                showTooltip(focusObj.getName() + '\n' + focusObj.getInfoString())
            else:
                showTooltip(focusObj.getName())
        else:
            hideTooltip()
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


class NotificationPanel(FloatingPanel):  #TODO move to seperate file
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

    def showNotification(self, title, message):
        self._title.SetLabel(title)
        self._info.SetLabel(message)
        self.Show()
        self._hideTimer.Start(10000, False)


class ToolsPanel(FloatingPanel): #TODO move to seperate file
    def __init__(self, parent, app):
        self._app = app
        self._active_tool = None
        self._buttons = []
        super(ToolsPanel, self).__init__(parent)
        self._main_panel = wx.Panel(self)
        self.SetSizer(wx.BoxSizer())
        self.GetSizer().Add(self._main_panel, 1, flag=wx.EXPAND)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self._main_panel.SetSizer(sizer)
        # TODO: Get tool panel title from app.
        sizer.Add(InnerTitleBar(self._main_panel, 'Transform model'), flag=wx.EXPAND)
        self._tools_panel = wx.Panel(self._main_panel, style=wx.SIMPLE_BORDER)
        self._tools_panel.SetBackgroundColour((214, 214, 214))
        sizer.Add(self._tools_panel, flag=wx.EXPAND)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._tools_panel.SetSizer(sizer)
        firstButton = True
        for tool in self._app.getTools():
            if tool.hasActiveButton():
                if firstButton:
                    firstButton = False
                else:
                    sizer.Add(wx.StaticBitmap(self._tools_panel, bitmap=getBitmap('top_bar_line.png')), 0, flag=wx.EXPAND)
                button = ToolButton(self._tools_panel, tool.getButtonIconName(), size=(53,38))
                button.tool = tool
                button.Bind(wx.EVT_BUTTON, self.onToolButton)
                sizer.Add(button)
                self._buttons.append(button)

    def onToolButton(self, e):
        button = e.GetEventObject()
        tool = button.tool
        tool.setActive(not tool.isActive())
        if self._active_tool is not None and self._active_tool != tool:
            self._active_tool.setActive(False)
        self._active_tool = tool
        for b in self._buttons:
            if b != button:
                b.SetValue(False)
        self._app.getView().refresh()


class ToolpathToolsPanel(FloatingPanel): #TODO move to seperate file
    def __init__(self, parent, app):
        self._app = app
        super(ToolpathToolsPanel, self).__init__(parent, False)

        self._outer_wall_check = wx.CheckBox(self, -1, '')
        self._inner_wall_check = wx.CheckBox(self, -1, '')
        self._infill_check = wx.CheckBox(self, -1, '')
        self._support_check = wx.CheckBox(self, -1, '')
        self._moves_check = wx.CheckBox(self, -1, '')
        self._retraction_check = wx.CheckBox(self, -1, '')

        self._layer_text = wx.StaticText(self, -1, 'Layer: ?/?')

        self._all_layers = wx.RadioButton(self, -1, 'All layers')
        self._single_layer = wx.RadioButton(self, -1, 'Single layer')

        self._outer_wall_check.SetValue(True)
        self._inner_wall_check.SetValue(True)
        self._infill_check.SetValue(True)
        self._support_check.SetValue(True)
        self._moves_check.SetValue(False)
        self._retraction_check.SetValue(True)

        self._all_layers.SetValue(True)

        self._layer_scroll = wx.ScrollBar(self, -1, style=wx.SB_VERTICAL)
        self._layer_scroll.SetScrollbar(0, 0, 1, 10)

        sizer = wx.GridBagSizer(2, 2)
        sizer.Add(wx.StaticText(self, -1, 'Show:'), pos=(0, 0), border=5, flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(wx.StaticText(self, -1, 'Outer walls:'), pos=(1, 0), border=5, flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(wx.StaticText(self, -1, 'Inner walls:'), pos=(2, 0), border=5, flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(wx.StaticText(self, -1, 'Infill/Skin:'), pos=(3, 0), border=5, flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(wx.StaticText(self, -1, 'Support:'), pos=(4, 0), border=5, flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(wx.StaticText(self, -1, 'Moves:'), pos=(5, 0), border=5, flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(wx.StaticText(self, -1, 'Retraction:'), pos=(6, 0), border=5, flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self._outer_wall_check, pos=(1, 1), flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self._inner_wall_check, pos=(2, 1), flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self._infill_check, pos=(3, 1), flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self._support_check, pos=(4, 1), flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self._moves_check, pos=(5, 1), flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self._retraction_check, pos=(6, 1), flag=wx.ALIGN_CENTER_VERTICAL)

        sizer.Add(self._layer_text, pos=(7, 0), span=(1, 2), border=5, flag=wx.TOP | wx.LEFT | wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self._all_layers, pos=(8, 0), span=(1, 2), border=5, flag=wx.TOP | wx.LEFT | wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self._single_layer, pos=(9, 0), span=(1, 2), border=5, flag=wx.BOTTOM | wx.LEFT | wx.ALIGN_CENTER_VERTICAL)

        sizer.Add(self._layer_scroll, pos=(0, 2), span=(10, 1), border=5, flag=wx.ALL | wx.EXPAND)

        self.SetSizer(sizer)
        self.Layout()

        self._app.getTranslator().addProgressCallback(self._translateProgressUpdate)

        self.Bind(wx.EVT_CHECKBOX, self._updateView, self._outer_wall_check)
        self.Bind(wx.EVT_CHECKBOX, self._updateView, self._inner_wall_check)
        self.Bind(wx.EVT_CHECKBOX, self._updateView, self._infill_check)
        self.Bind(wx.EVT_CHECKBOX, self._updateView, self._support_check)
        self.Bind(wx.EVT_CHECKBOX, self._updateView, self._moves_check)
        self.Bind(wx.EVT_CHECKBOX, self._updateView, self._retraction_check)
        self.Bind(wx.EVT_SCROLL, self._updateView, self._layer_scroll)
        self.Bind(wx.EVT_RADIOBUTTON, self._updateView, self._all_layers)
        self.Bind(wx.EVT_RADIOBUTTON, self._updateView, self._single_layer)

    def _translateProgressUpdate(self, progress, ready):
        if ready:
            layer_count = 0
            for obj in self._app.getScene().getObjects():
                layer_count += obj.getToolpathLayerCount()
            wx.CallAfter(self._layer_scroll.SetThumbPosition, 0)
            wx.CallAfter(self._setLayerCount, layer_count)

    def _updateView(self, e=None):
        renderer = self._app.getView().getToolpathRenderer()
        renderer.showOuterWall(self._outer_wall_check.GetValue())
        renderer.showInnerWall(self._inner_wall_check.GetValue())
        renderer.showInfill(self._infill_check.GetValue())
        renderer.showSupport(self._support_check.GetValue())
        renderer.showMoves(self._moves_check.GetValue())
        renderer.showRetraction(self._retraction_check.GetValue())
        renderer.setTopShowLayerNr(self._layer_scroll.GetRange() - self._layer_scroll.GetThumbPosition() + 1)
        renderer.setSingleLayer(self._single_layer.GetValue())
        self._layer_text.SetLabel("Layer: %d/%d" % (self._layer_scroll.GetRange() - self._layer_scroll.GetThumbPosition() + 1, self._layer_scroll.GetRange() + 1))
        self._app.getView().refresh()

    def _setLayerCount(self, count):
        self._layer_scroll.SetScrollbar(0, self._layer_scroll.GetThumbPosition(), count - 1, 10)
        self._updateView()


class MainWindow(wx.Frame):
    def __init__(self, app):
        super(MainWindow, self).__init__(None, title='Cura - Pink Unicorn edition')
        self._app = app

        #Create the global tooltip window so different parts can show tooltips.
        TooltipWindow(self)

        self._mainView = MainOpenGLView(self, app)
        self._settingsPanel = None
        self._topBarLeft = TopBarLeft(self._mainView, app)
        self._topBarRight = TopBarRight(self._mainView, app)
        self._app.getView().setOpenGLWindow(self._mainView)

        self._fileBrowser = FileBrowserPanel(self._mainView, app)
        self._toolpathTools = ToolpathToolsPanel(self._mainView, app)

        self._toolsPanel = ToolsPanel(self._mainView, app)

        self._profilePanel = ProfilePanel(self._mainView, app)

        self._notification = NotificationPanel(self._mainView)

        self._mainSizer = wx.BoxSizer(wx.VERTICAL)
        self._mainSizer.Add(self._mainView, 1, wx.EXPAND)
        self.SetSizer(self._mainSizer)

        self._floatSizer = FloatSizer(self)
        self._floatSizer.Add(self._toolsPanel, userData={'top': 0})
        self._floatSizer.Add(self._topBarLeft, userData={'top': 0, 'left': 0, 'width': self._toolsPanel})
        self._floatSizer.Add(self._topBarRight, userData={'top': 0, 'right': 0, 'width': self._toolsPanel})
        self._floatSizer.Add(self._fileBrowser, userData={'left': 0, 'top': 72})
        self._floatSizer.Add(self._toolpathTools, userData={'left': 0, 'top': 72})
        self._floatSizer.Add(self._profilePanel, userData={'right': 0, 'top': 72})
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

    def refreshProfilePanel(self):
        self.closeSettings()
        self._floatSizer.Detach(self._profilePanel)
        self._profilePanel.Destroy()
        self._profilePanel = ProfilePanel(self._mainView, self._app)
        self._floatSizer.Add(self._profilePanel, userData={'right': 0, 'top': 72})
        self._mainView.Layout()

    def openSettingCategory(self, categoryButton):
        category = categoryButton.category
        self.closeSettings()

        self._settingsPanel = SettingPanel(self._mainView, self._app, category)
        self._floatSizer.Add(self._settingsPanel, userData={'right': self._profilePanel, 'top': 72 + categoryButton.GetPosition()[1]})
        self._mainView.Layout()

    def _onMove(self, e):
        self._mainView.Layout()

    def setViewMode(self, mode):
        if mode == 'Toolpaths':
            self._fileBrowser.Hide()
            self._toolpathTools.Show()
        else:
            self._fileBrowser.Show()
            self._toolpathTools.Hide()

    def showNotification(self, title, message):
        self._notification.showNotification(title, message)
