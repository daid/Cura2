import wx

popupWindow = None


def showTooltip(text, ctrl=None):
    global popupWindow
    if popupWindow is None:
        return
    popupWindow.setText(text)

    if ctrl is None:
        position = wx.GetMousePosition() + (25, 25)
    else:
        position = ctrl.ClientToScreen(ctrl.GetSizeTuple())
    w = popupWindow.GetSize().GetWidth()
    if wx.Display.GetFromPoint((position[0] + w, position[1])) == wx.NOT_FOUND:
        position = position - (w, 0)

    popupWindow.SetPosition(position)
    popupWindow.Show()


def hideTooltip():
    global popupWindow
    if popupWindow is None:
        return
    popupWindow.Hide()


class TooltipWindow(wx.PopupWindow):
    def __init__(self, mainWindow):
        super(TooltipWindow, self).__init__(mainWindow, flags=wx.BORDER_SIMPLE)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_INFOBK))
        self._text = wx.StaticText(self, -1, 'XXX')
        self._text.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_INFOTEXT))
        self._sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._sizer.Add(self._text, 1, border=3, flag=wx.ALL)
        self.SetSizer(self._sizer)
        self.Layout()

        global popupWindow
        popupWindow = self

    def setText(self, text):
        if text != self._text.GetLabel():
            self._text.SetLabel(text)
            self._text.Wrap(350)
            self.Fit()
