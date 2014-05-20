import wx


class FloatingPanel(wx.Frame): #TODO: Move to seperate file; this has nothing to do with a sizer.
    def __init__(self, parent):
        super(FloatingPanel, self).__init__(parent, style=wx.FRAME_FLOAT_ON_PARENT | wx.NO_BORDER | wx.FRAME_NO_TASKBAR | wx.FRAME_SHAPED)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DFACE))
        wx.CallAfter(self.Show)


class FloatSizer(wx.PySizer):
    """
    The FloatSizer is a specialized wxPython sized which can put floating panels on top of the 3D window. It uses relative positioning
    """
    def __init__(self, parent):
        wx.PySizer.__init__(self)
        self._parent = parent

    def CalcMin(self):
        """
        This function is called from wxPython when a new layout for this sizer needs to be calculated.

        Report the minimal size that we need for this component. Which we do not use in this sizer.
        """
        return wx.Size(1, 1)

    def RecalcSizes(self):
        """
        This function is called from wxPython when a new layout for this sizer needs to be calculated.

        Calculate the size and position needed for each child element.
        """
        size = self.GetSize()
        for item in self.GetChildren():
            itemSize = item.CalcMin()
            data = item.GetUserData()

            if 'width' in data:
                if isinstance(data['width'], wx.Frame):
                    if 'left' in data:
                        x, y = self._parent.ScreenToClient(data['width'].GetPosition())
                        itemSize[0] = x
                    elif 'right' in data:
                        x, y = self._parent.ScreenToClient(data['width'].GetPosition())
                        itemSize[0] = size[0] - x - data['width'].GetSize().GetWidth()
                else:
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
                    x = self._parent.ScreenToClient(data['right'].GetPosition())[0] - itemSize[0]
                else:
                    x = size[0] - itemSize[0] - data['right']
            if 'bottom' in data:
                if isinstance(data['bottom'], wx.Window):
                    y = self._parent.ScreenToClient(data['bottom'].GetPosition())[1] - itemSize[1]
                else:
                    y = size[1] - itemSize[1] - data['bottom']

            if isinstance(item.GetWindow(), wx.Frame):
                x, y = self._parent.ClientToScreen((x, y))

            item.SetDimension((x, y), itemSize)
