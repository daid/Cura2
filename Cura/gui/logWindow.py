import wx


class LogWindow(wx.Frame):
    def __init__(self, log_data):
        super(LogWindow, self).__init__(None)

        self._text = wx.TextCtrl(self, -1, log_data, style=wx.TE_MULTILINE)
        self.SetSizer(wx.BoxSizer(wx.VERTICAL))
        self.GetSizer().Add(self._text, 1, wx.EXPAND)