import wx

from Cura.resources import getBitmap


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
        dc.SetTextForeground(wx.WHITE)
        dc.SetFont(wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT))
        tw, th = dc.GetTextExtent(self._caption)
        dc.DrawBitmap(getBitmap("InnerTitleBar.png"), 0, 0)
        dc.DrawText(self._caption, (self.GetSize().GetWidth() - tw) / 2, (self.GetSize().GetHeight() - th) / 2)
