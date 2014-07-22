import wx
from wx.lib.buttons import GenToggleButton

from Cura.resources import getBitmap
from Cura.gui.tooltip import showTooltip, hideTooltip


class ProfileCategoryButton(GenToggleButton):
    """
    Button that 'holds' a set of settings, which will be expanded when clicked upon.
    """
    def __init__(self, parent, label, icon):
        icon = 'icon_resolution.png'
        self._icon = getBitmap(icon)
        self._small = False
        super(ProfileCategoryButton, self).__init__(parent, label=label, style=wx.BORDER_NONE)

        self.Bind(wx.EVT_ENTER_WINDOW, self._onEnter, self)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._onExit, self)

    def setSmall(self, small):
        self._small = small
        self.Refresh()

    def isSmall(self):
        return self._small

    def DrawLabel(self, dc, width, height, dx=0, dy=0):
        """
        draw the text of the button. TODO: Naming not consistent. Should start with lower case?
        """
        dc.SetFont(self.GetFont())
        if self.IsEnabled():
            dc.SetTextForeground(self.GetForegroundColour())
        else:
            dc.SetTextForeground(wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT))
        label = self.GetLabel()
        tw, th = dc.GetTextExtent(label)
        dc.DrawText(label, 55, (height - th) / 2)

    def GetBackgroundBrush(self, dc):
        """
        TODO: Naming not consistent. Should start with lower case?
        """
        return wx.Brush(self.GetBackgroundColour(), wx.SOLID)

    def OnPaint(self, event):
        """
        Rendering of the button.
        """
        (width, height) = self.GetClientSizeTuple()

        dc = wx.BufferedPaintDC(self)
        brush = self.GetBackgroundBrush(dc)
        if brush is not None:
            dc.SetBackground(brush)
            dc.Clear()
        #Draw border around active categories
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
        if not self._small:
            self.DrawLabel(dc, width, height)

    def DoGetBestSize(self):
        """
        TODO: Naming not consistent. Should start with lower case?
        """
        w, h = super(ProfileCategoryButton, self).DoGetBestSize()
        if not self._small:
            w += 55 + 20
        else:
            w = 46
        h = max(30, h)
        return w, h

    def _onEnter(self, e):
        if self._small:
            showTooltip(self.GetLabel(), self)

    def _onExit(self, e):
        hideTooltip(self)
