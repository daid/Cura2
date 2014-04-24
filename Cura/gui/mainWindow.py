import wx

from Cura.gui.openGLPanel import OpenGLPanel


class InnerTitleBar(wx.Panel):
    def __init__(self, parent, caption):
        self._caption = caption
        super(InnerTitleBar, self).__init__(parent)
        self.SetMinSize((-1, 18))

        self.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBackground)

    def onEraseBackground(self, evt):
        dc = evt.GetDC()
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        dc.Background = wx.Brush(wx.RED)
        dc.Clear()
        dc.SetTextForeground(wx.WHITE)
        dc.SetFont(wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT))
        tw, th = dc.GetTextExtent(self._caption)
        dc.DrawText(self._caption, (self.GetSize().GetWidth() - tw) / 2, (self.GetSize().GetHeight() - th) / 2)
        #bmp = wx.Bitmap("butterfly.jpg")
        #dc.DrawBitmap(bmp, 0, 0)


class PrintPofilePanel(wx.Panel):
    def __init__(self, parent, app):
        self._app = app
        super(PrintPofilePanel, self).__init__(parent, style=wx.SIMPLE_BORDER)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(InnerTitleBar(self, 'Print profile'), flag=wx.EXPAND)

        for c in self._app.getMachine().getSettingCategories():
            if c.isVisible():
                sizer.Add(wx.Button(self, -1, c.getLabel()), flag=wx.EXPAND)
        sizer.Add(wx.Button(self, -1, 'Plugins'), flag=wx.EXPAND)
        sizer.Add(wx.Button(self, -1, 'Load profile'), flag=wx.EXPAND)
        sizer.Add(wx.Button(self, -1, 'Save GCode'), flag=wx.EXPAND)
        self.SetSizer(sizer)


class MainWindow(wx.Frame):
    def __init__(self, app):
        super(MainWindow, self).__init__(None, title='Cura - Pink Unicorn edition')
        self._app = app

        self._topbar = wx.Panel(self)
        self._mainView = OpenGLPanel(self)

        self._fileBrowser = wx.Panel(self._mainView)
        self._fileBrowser.SetSize((185, 400))
        self._fileBrowser.SetPosition((0, 32))
        self._fileBrowser.SetBackgroundColour(wx.GREEN)

        self._transformTools = wx.Panel(self._mainView)
        self._transformTools.SetSize((165, 54))
        self._transformTools.SetPosition((400, 0))
        self._transformTools.SetBackgroundColour(wx.BLUE)

        self._printProfilePanel = PrintPofilePanel(self._mainView, app)
        self._printProfilePanel.Fit()
        self._printProfilePanel.SetPosition((600, 32))

        self._topbar.SetBackgroundColour(wx.RED)
        self._topbar.SetMinSize((1,39))

        self._mainSizer = wx.BoxSizer(wx.VERTICAL)
        self._mainSizer.Add(self._topbar, 0, wx.EXPAND)
        self._mainSizer.Add(self._mainView, 1, wx.EXPAND)
        self.SetSizer(self._mainSizer)
