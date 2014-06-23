import wx

from Cura.gui.floatSizer import FloatingPanel
from Cura.gui.widgets.topBarButton import TopBarButton
from Cura.resources import getBitmap
from Cura.gui.preferencesDialog import PreferencesDialog

"""
TODO: Should be renamed to toBars or something like that.
"""

class TopBarLeft(FloatingPanel):
    def __init__(self, parent, app):
        super(TopBarLeft, self).__init__(parent)
        self._app = app

        self._3dViewButton = TopBarButton(self, '3D', size=(38, 38))
        self._rightViewButton = TopBarButton(self, 'Right', size=(38, 38))
        self._frontViewButton = TopBarButton(self, 'Front', size=(38, 38))
        self._topViewButton = TopBarButton(self, 'Top', size=(38, 38))

        self._3dViewButton.SetValue(True)

        self.SetBackgroundColour((214, 214, 214)) #TODO; extract this from a color setting file instead of hard coding it.

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.StaticBitmap(self, bitmap=getBitmap('small_logo.png')), 0, flag=wx.EXPAND)
        sizer.Add(wx.Panel(self, size=(100, 1)), 0, flag=wx.EXPAND)

        sizer.Add(wx.StaticBitmap(self, bitmap=getBitmap('top_bar_line.png')), 0, flag=wx.EXPAND)
        sizer.Add(self._3dViewButton, 0, flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(wx.StaticBitmap(self, bitmap=getBitmap('top_bar_line.png')), 0, flag=wx.EXPAND)
        sizer.Add(self._rightViewButton, 0, flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(wx.StaticBitmap(self, bitmap=getBitmap('top_bar_line.png')), 0, flag=wx.EXPAND)
        sizer.Add(self._frontViewButton, 0, flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(wx.StaticBitmap(self, bitmap=getBitmap('top_bar_line.png')), 0, flag=wx.EXPAND)
        sizer.Add(self._topViewButton, 0, flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(wx.StaticBitmap(self, bitmap=getBitmap('top_bar_line.png')), 0, flag=wx.EXPAND)

        sizer.Add(wx.Panel(self), 1, flag=wx.EXPAND)

        self.SetSizer(sizer)
        self.SetMinSize((-1, 39))

        self.Bind(wx.EVT_BUTTON, lambda e: self._setViewDirection('3D'), self._3dViewButton)
        self.Bind(wx.EVT_BUTTON, lambda e: self._setViewDirection('Right'), self._rightViewButton)
        self.Bind(wx.EVT_BUTTON, lambda e: self._setViewDirection('Front'), self._frontViewButton)
        self.Bind(wx.EVT_BUTTON, lambda e: self._setViewDirection('Top'), self._topViewButton)

    def _setViewDirection(self, viewDirection):
        self._3dViewButton.SetValue(viewDirection == '3D')
        self._rightViewButton.SetValue(viewDirection == 'Right')
        self._frontViewButton.SetValue(viewDirection == 'Front')
        self._topViewButton.SetValue(viewDirection == 'Top')
        self._app.getView().setViewDirection(viewDirection)


class TopBarRight(FloatingPanel):
    def __init__(self, parent, app):
        super(TopBarRight, self).__init__(parent)
        self._app = app

        self._settingsButton = TopBarButton(self, 'Settings')
        self._helpButton = TopBarButton(self, 'Help')

        self.SetBackgroundColour((214, 214, 214))  #TODO; extract this from a color setting file instead of hard coding it.

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(wx.Panel(self), 1, flag=wx.EXPAND)
        sizer.Add(wx.StaticBitmap(self, bitmap=getBitmap('top_bar_line.png')), 0, flag=wx.EXPAND)
        sizer.Add(wx.Panel(self, size=(10, 1)), 0, flag=wx.EXPAND)
        sizer.Add(wx.StaticText(self, label='View settings'), 0, flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(wx.Panel(self, size=(10, 1)), 0, flag=wx.EXPAND)
        viewOptions = [_('Normal'), _('Toolpaths')]
        self._view_mode_combo = wx.ComboBox(self, value=viewOptions[0], choices=viewOptions, style=wx.CB_DROPDOWN|wx.CB_READONLY)
        sizer.Add(self._view_mode_combo, 0, flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(wx.Panel(self, size=(10, 1)), 0, flag=wx.EXPAND)
        sizer.Add(wx.StaticBitmap(self, bitmap=getBitmap('top_bar_line.png')), 0, flag=wx.EXPAND)
        sizer.Add(self._settingsButton, 0, flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(wx.StaticBitmap(self, bitmap=getBitmap('top_bar_line.png')), 0, flag=wx.EXPAND)
        sizer.Add(self._helpButton, 0, flag=wx.ALIGN_CENTER_VERTICAL)

        self.SetSizer(sizer)
        self.SetMinSize((-1, 39))

        self._view_mode_combo.Bind(wx.EVT_COMBOBOX, self._onViewChange)
        self.Bind(wx.EVT_BUTTON, self.onPreferences, self._settingsButton)

    def onPreferences(self, e):
        PreferencesDialog(self._app).ShowModal()
        self._settingsButton.SetValue(False)

    def _onViewChange(self, e):
        self._app.getView().setViewMode(self._view_mode_combo.GetValue())