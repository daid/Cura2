import wx
from wx.lib.buttons import GenButton

from Cura.resources import getBitmap


class GradientButton(GenButton):
    def __init__(self, parent, label, icon, icon_align=wx.ALIGN_LEFT):
        self._small = False
        self._icon = icon
        self._icon_align = icon_align
        super(GradientButton, self).__init__(parent, label=label)
        self.SetMinSize((-1, 42))
        self.SetForegroundColour((255, 255, 255))
        f = self.GetFont()
        self.SetFont(wx.Font(16, f.Family, f.Style, wx.FONTWEIGHT_NORMAL, False, f.FaceName))

        self._colorTop = wx.Colour(71, 188, 221)
        self._colorBottom = wx.Colour(109, 204, 226)
        self._fillAmount = 1.0

        gray = (self._colorTop.Red() + self._colorTop.Green() + self._colorTop.Blue()) / 3
        self._colorTopGray = wx.Colour(gray, gray, gray)
        gray = (self._colorBottom.Red() + self._colorBottom.Green() + self._colorBottom.Blue()) / 3
        self._colorBottomGray = wx.Colour(gray, gray, gray)

    def setIcon(self, icon):
        self._icon = icon
        self.Refresh()

    def setSmall(self, small):
        self._small = small
        self.Refresh()

    def isSmall(self):
        return self._small

    def setFillAmount(self, fill):
        self._fillAmount = fill
        self.Refresh()

    def OnPaint(self, event):
        (width, height) = self.GetClientSizeTuple()

        dc = wx.BufferedPaintDC(self)
        fillWidth = width * self._fillAmount
        if fillWidth < width:
            dc.GradientFillLinear((fillWidth, 0, width - fillWidth, height), self._colorTopGray, self._colorBottomGray, wx.SOUTH)
        dc.GradientFillLinear((0, 0, fillWidth, height), self._colorTop, self._colorBottom, wx.SOUTH)
        dc.SetPen(wx.Pen((102, 102, 102)))
        dc.SetBrush(wx.Brush('#ffffff', wx.TRANSPARENT))
        dc.DrawRectangle(0, 0, width, height)

        icon = getBitmap(self._icon)
        if not self._small:
            dc.SetFont(self.GetFont())
            label = self.GetLabel()
            tw, th = dc.GetTextExtent(label)
            icon_spacing = 8
            if self._icon_align == wx.ALIGN_RIGHT:
                x = (width - tw - icon.GetWidth() - icon_spacing) / 2
            else:
                x = (width - tw - icon.GetWidth() - icon_spacing) / 2 + icon.GetWidth() + icon_spacing

            dc.SetTextForeground(wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT))
            dc.DrawText(label, x + 1, (height-th)/2 + 1)
            if self.IsEnabled():
                dc.SetTextForeground(self.GetForegroundColour())
            else:
                dc.SetTextForeground((64, 64, 64))
            dc.DrawText(label, x, (height-th)/2)
            dc.DrawText(label, x, (height-th)/2)
            if self._icon_align == wx.ALIGN_RIGHT:
                dc.DrawBitmap(icon, x + tw + icon_spacing, (height - icon.GetHeight()) / 2)
            else:
                dc.DrawBitmap(icon, x - icon.GetWidth() - icon_spacing, (height - icon.GetHeight()) / 2)
        else:
            dc.DrawBitmap(icon, (width - icon.GetWidth()) / 2, (height - icon.GetHeight()) / 2)

    def DoGetBestSize(self):
        w, h = super(GenButton, self).DoGetBestSize()
        if self._small:
            w = 46
        return w, h
