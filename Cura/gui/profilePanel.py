import wx

from Cura.gui.widgets.profileCategoryButton import ProfileCategoryButton
from Cura.gui.widgets.innerTitleBar import InnerTitleBar


class ProfilePanel(wx.Panel):
    def __init__(self, parent, app):
        super(ProfilePanel, self).__init__(parent, style=wx.SIMPLE_BORDER)

        self._app = app
        self._categoryButtons = []

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(InnerTitleBar(self, 'Print profile'), flag=wx.EXPAND)

        n = 0
        for c in self._app.getMachine().getSettingCategories():
            if c.isVisible():
                b = ProfileCategoryButton(self, c.getLabel())
                b.category = c
                sizer.Add(b, flag=wx.EXPAND)
                b.Bind(wx.EVT_BUTTON, self.onCategoryButton)
                self._categoryButtons.append(b)

                n += 1
                if n % 4 == 0:
                    sizer.Add(wx.StaticLine(self), flag=wx.EXPAND)

        sizer.Add(ProfileCategoryButton(self, 'Plugins'), flag=wx.EXPAND)
        sizer.Add(ProfileCategoryButton(self, 'Load profile'), flag=wx.EXPAND)
        sizer.Add(wx.Button(self, label='Save GCode'), flag=wx.EXPAND)
        self.SetSizer(sizer)

    def onCategoryButton(self, e):
        button = e.GetEventObject()
        if not button.GetValue():
            button = None
        for b in self._categoryButtons:
            if b != button:
                b.SetValue(False)
        if button is None:
            self._app.getMainWindow().closeSettings()
        else:
            self._app.getMainWindow().openSettingCategory(button.category)
