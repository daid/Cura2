import wx

from wx.lib.buttons import GenToggleButton
from Cura.resources import getBitmap
from Cura.gui.tooltip import showTooltip, hideTooltip


class ToolButton(GenToggleButton):
    def __init__(self, parent, tooltip, image, size=(10, 10)):
        super(ToolButton, self).__init__(parent, size=size, style=wx.BORDER_NONE)
        self._image = image
        self._tooltip = tooltip
        self.SetBackgroundColour((214, 214 ,214))
        self.faceDnClr = (237, 237, 237)

        self.Bind(wx.EVT_ENTER_WINDOW, self._onEnter, self)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._onExit, self)

    def OnPaint(self, event):
        (width, height) = self.GetClientSizeTuple()

        dc = wx.PaintDC(self)
        brush = self.GetBackgroundBrush(dc)
        if brush is not None:
            dc.SetBackground(brush)
            dc.Clear()
        bitmap = getBitmap(self._image)
        dc.DrawBitmap(bitmap, (width - bitmap.GetWidth()) / 2, (height - bitmap.GetHeight()) / 2)

    def _onEnter(self, e):
        showTooltip(self._tooltip, self)

    def _onExit(self, e):
        hideTooltip(self)
