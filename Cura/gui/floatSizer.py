import wx


class FloatingPanel(wx.Frame):
    def __init__(self, parent):
        super(FloatingPanel, self).__init__(parent, style=wx.FRAME_FLOAT_ON_PARENT|wx.NO_BORDER|wx.FRAME_NO_TASKBAR)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DFACE))
        wx.CallAfter(self.Show)


class FloatSizer(wx.PySizer):
    def __init__(self, parent):
        wx.PySizer.__init__(self)
        self._parent = parent

    def CalcMin(self):
        return wx.Size(1, 1)

    def RecalcSizes(self):
        size = self.GetSize()
        for item in self.GetChildren():
            itemSize = item.CalcMin()
            data = item.GetUserData()

            if 'width' in data:
                itemSize[0] = size[0] * data['width']
            if 'height' in data:
                itemSize[1] = size[1] * data['height']

            x = (size[0] - itemSize[0]) / 2
            y = (size[1] - itemSize[1]) / 2

            if 'left' in data:
                x = data['left']
            if 'top' in data:
                y = data['top']
            if 'right' in data:
                if isinstance(data['right'], wx.Window):
                    x = data['right'].GetPosition()[0] - itemSize[0]
                else:
                    x = size[0] - itemSize[0] - data['right']
            if 'bottom' in data:
                if isinstance(data['bottom'], wx.Window):
                    y = data['bottom'].GetPosition()[1] - itemSize[1]
                else:
                    y = size[1] - itemSize[1] - data['bottom']

            if isinstance(item.GetWindow(), wx.Frame):
                x, y = self._parent.ClientToScreen((x, y))

            item.SetDimension((x, y), itemSize)
