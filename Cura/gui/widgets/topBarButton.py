import wx
from wx.lib.buttons import GenToggleButton


class TopBarButton(GenToggleButton):
    def __init__(self, parent, label, size=None):
        super(TopBarButton, self).__init__(parent, label=label, style=wx.BORDER_NONE, size=size)
        f = self.GetFont()
        self._boldFont = wx.Font(f.PointSize, f.Family, f.Style, wx.FONTWEIGHT_BOLD, False, f.FaceName)
        self._downColor = (57, 163, 213)

    def DrawLabel(self, dc, width, height, dx=0, dy=0):
        if self.up:
            dc.SetFont(self.GetFont())
        else:
            dc.SetFont(self._boldFont)
        if self.IsEnabled():
            if not self.up:
                dc.SetTextForeground(self._downColor)
            else:
                dc.SetTextForeground(self.GetForegroundColour())
        else:
            dc.SetTextForeground(wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT))
        label = self.GetLabel()
        tw, th = dc.GetTextExtent(label)
        if not self.up:
            dx = dy = self.labelDelta
        dc.DrawText(label, (width-tw)/2+dx, (height-th)/2+dy)

    def GetBackgroundBrush(self, dc):
        return wx.Brush(self.GetBackgroundColour(), wx.SOLID)
