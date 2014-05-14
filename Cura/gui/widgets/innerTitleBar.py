import wx

from Cura.resources import getBitmap


class InnerTitleBar(wx.Panel):
    def __init__(self, parent, caption):
        self._caption = caption
        self._icon = None
        super(InnerTitleBar, self).__init__(parent)
        self.SetMinSize((-1, 18))

        self.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBackground)
        self._small = False
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM) #HACK; required for linux to ensure that the EVT_ERASE_BACKGROUND is called.
        print("Title bar created")

    def setSmall(self, small):
        self._small = small
        self.Refresh()

    def isSmall(self):
        return self._small

    def setIcon(self, icon):
        self._icon = icon

    def onEraseBackground(self, evt):
        print("Title bar background")
        dc = evt.GetDC()
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        w, h = self.GetSizeTuple()
        dc.DrawBitmap(getBitmap("InnerTitleBar.png"), 0, 0)

        if self._icon is not None:
            icon = getBitmap(self._icon)
            dc.DrawBitmap(icon, w - icon.GetSize().GetWidth() - 16, (h - icon.GetSize().GetHeight()) / 2)
        if not self._small:
            dc.SetTextForeground(wx.WHITE)
            dc.SetFont(wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT))
            tw, th = dc.GetTextExtent(self._caption)
            dc.DrawText(self._caption, (w - tw) / 2, (h - th) / 2)
