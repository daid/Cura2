import wx

from Cura.gui.widgets.innerTitleBar import InnerTitleBar


class SettingPanel(wx.Panel):
    def __init__(self, parent, app, category):
        super(SettingPanel, self).__init__(parent, style=wx.SIMPLE_BORDER, size=(0, 0))
        self._app = app

        sizer = wx.GridBagSizer(2, 2)
        sizer.Add(InnerTitleBar(self, category.getLabel()), pos=(0, 0), span=(1, 2), flag=wx.EXPAND)
        n = 1
        for s in category.getSettings():
            sizer.Add(wx.StaticText(self, label=s.getLabel()), pos=(n, 0), span=(1, 1), flag=wx.ALIGN_CENTER_VERTICAL)
            sizer.Add(wx.TextCtrl(self, value=s.getValue()), pos=(n, 1), span=(1, 1), flag=wx.EXPAND)
            n += 1
        self.SetSizer(sizer)
