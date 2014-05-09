import wx
from wx.lib.buttons import GenButton


class GradientButton(GenButton):
    def __init__(self, parent, label):
        self._small = False
        super(GradientButton, self).__init__(parent, label=label)
        self.SetMinSize((-1, 42))

        self._colorTop = wx.Colour(71, 188, 221)
        self._colorBottom = wx.Colour(109, 204, 226)
        self._fillAmount = 1.0

        gray = (self._colorTop.Red() + self._colorTop.Green() + self._colorTop.Blue()) / 3
        self._colorTopGray = wx.Colour(gray, gray, gray)
        gray = (self._colorBottom.Red() + self._colorBottom.Green() + self._colorBottom.Blue()) / 3
        self._colorBottomGray = wx.Colour(gray, gray, gray)

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

        dc = wx.PaintDC(self)
        dc.GradientFillLinear((0, 0, width, height), self._colorTopGray, self._colorBottomGray, wx.SOUTH)
        dc.GradientFillLinear((0, 0, width * self._fillAmount, height), self._colorTop, self._colorBottom, wx.SOUTH)
        dc.SetPen(wx.Pen((102, 102, 102)))
        dc.SetBrush(wx.Brush('#ffffff', wx.TRANSPARENT))
        dc.DrawRectangle(0, 0, width, height)

        if not self._small:
            self.DrawLabel(dc, width, height)

    def DoGetBestSize(self):
        w, h = super(GenButton, self).DoGetBestSize()
        if self._small:
            w = 46
        return w, h
