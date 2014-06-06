import wx
from wx.lib.buttons import GenToggleButton


class ToolButton(GenToggleButton):
    def __init__(self, parent, size=(10, 10)):
        super(ToolButton, self).__init__(parent, label="tool", size=size, style=wx.BORDER_NONE)
