import wx
from wx.lib.buttons import GenToggleButton

from Cura.resources import getBitmap


class ProfileCategoryButton(GenToggleButton):
    def __init__(self, parent, label, icon):
        super(ProfileCategoryButton, self).__init__(parent, label=label, style=wx.BORDER_NONE)
        icon = 'icon_resolution.png'
        self._icon = getBitmap(icon)

    def DrawLabel(self, dc, width, height, dx=0, dy=0):
        dc.SetFont(self.GetFont())
        if self.IsEnabled():
            dc.SetTextForeground(self.GetForegroundColour())
        else:
            dc.SetTextForeground(wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT))
        label = self.GetLabel()
        tw, th = dc.GetTextExtent(label)
        dc.DrawText(label, 55, (height - th) / 2)

    def GetBackgroundBrush(self, dc):
        return wx.Brush(self.GetBackgroundColour(), wx.SOLID)

    def OnPaint(self, event):
        (width, height) = self.GetClientSizeTuple()

        dc = wx.BufferedPaintDC(self)
        brush = self.GetBackgroundBrush(dc)
        if brush is not None:
            dc.SetBackground(brush)
            dc.Clear()

        if not self.up:
            b = getBitmap('category_select_left.png')
            dc.DrawBitmap(b, 9, (height - b.GetHeight()) / 2)
            b = getBitmap('category_select_right.png')
            dc.DrawBitmap(b, width - 12, (height - b.GetHeight()) / 2)
            b = getBitmap('category_select_background.png')
            for n in xrange(11, width - 12):
                dc.DrawBitmap(b, n, (height - b.GetHeight()) / 2)
        b = self._icon
        dc.DrawBitmap(b, 22 - b.GetWidth() / 2, (height - b.GetHeight()) / 2)
        self.DrawLabel(dc, width, height)

    def DoGetBestSize(self):
        w, h = super(ProfileCategoryButton, self).DoGetBestSize()
        w += 55 + 20
        h = max(30, h)
        return w, h