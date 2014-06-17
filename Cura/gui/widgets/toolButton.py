import wx

from wx.lib.buttons import GenToggleButton
from Cura.resources import getBitmap


class ToolButton(GenToggleButton):
    def __init__(self, parent, image, size=(10, 10)):
        super(ToolButton, self).__init__(parent, size=size, style=wx.BORDER_NONE)
        self.image = image
        self.SetBackgroundColour((214, 214 ,214))
        self.faceDnClr = (237, 237, 237)

    def OnPaint(self, event):
        (width, height) = self.GetClientSizeTuple()

        dc = wx.PaintDC(self)
        brush = self.GetBackgroundBrush(dc)
        if brush is not None:
            dc.SetBackground(brush)
            dc.Clear()
        bitmap = getBitmap(self.image)
        dc.DrawBitmap(bitmap, (width - bitmap.GetWidth()) / 2, (height - bitmap.GetHeight()) / 2)
