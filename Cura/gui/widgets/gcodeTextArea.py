__copyright__ = "Copyright (C) 2013 David Braam - Released under terms of the AGPLv3 License"

import wx
import wx.stc
import sys


class GcodeTextArea(wx.stc.StyledTextCtrl):
    def __init__(self, parent):
        super(GcodeTextArea, self).__init__(parent)

        self.SetLexer(wx.stc.STC_LEX_CONTAINER)
        self.Bind(wx.stc.EVT_STC_STYLENEEDED, self.OnStyle)

        fontSize = wx.SystemSettings.GetFont(wx.SYS_ANSI_VAR_FONT).GetPointSize()
        fontName = wx.Font(wx.SystemSettings.GetFont(wx.SYS_ANSI_VAR_FONT).GetPointSize(), wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL).GetFaceName()
        self.SetStyleBits(5)
        self.StyleSetSpec(0, "face:%s,size:%d" % (fontName, fontSize))
        self.StyleSetSpec(1, "fore:#006000,face:%s,size:%d" % (fontName, fontSize))
        self.StyleSetSpec(2, "fore:#0000FF,face:%s,size:%d" % (fontName, fontSize))
        self.StyleSetSpec(3, "fore:#800080,face:%s,size:%d" % (fontName, fontSize))
        self.IndicatorSetStyle(0, wx.stc.STC_INDIC_TT)
        self.IndicatorSetForeground(0, "#0000FF")
        self.IndicatorSetStyle(1, wx.stc.STC_INDIC_SQUIGGLE)
        self.IndicatorSetForeground(1, "#FF0000")
        self.SetWrapMode(wx.stc.STC_WRAP_NONE)
        self.SetScrollWidth(1000)
        if sys.platform == 'darwin':
            self.Bind(wx.EVT_KEY_DOWN, self.OnMacKeyDown)

        #GCodes and MCodes as supported by Marlin
        #GCode 21 is not really supported by Marlin, but we still do not report it as error as it's often used.
        self.supportedGCodes = [0,1,2,3,4,21,28,90,91,92]
        self.supportedMCodes = [17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,42,80,81,82,83,84,85,92,104,105,106,107,109,114,115,117,119,140,190,201,202,203,204,205,206,220,221,240,301,302,303,400,500,501,502,503,999]

    def OnMacKeyDown(self, e):
        code = e.GetKeyCode();
        stopPropagation = True
        #Command
        if e.CmdDown():
            if code == wx._core.WXK_LEFT:
                self.GotoLine(self.GetCurrentLine())
            elif code == wx._core.WXK_RIGHT:
                self.GotoPos(self.GetLineEndPosition(self.GetCurrentLine()))
            elif code == wx._core.WXK_UP:
                self.GotoPos(0)
            elif code == wx._core.WXK_DOWN:
                self.GotoPos(self.GetLength())
            else:
                stopPropagation = False
        # Control
        elif e.GetModifiers() & 0xF0:
            if code == 65: # A
                self.GotoLine(self.GetCurrentLine())
            elif code == 69: # E
                self.GotoPos(self.GetLineEndPosition(self.GetCurrentLine()))
            else:
                stopPropagation = False
        else:
            stopPropagation = False
        # Event propagation
        if stopPropagation:
            e.StopPropagation()
        else:
            e.Skip()

    def OnStyle(self, e):
        lineNr = self.LineFromPosition(self.GetEndStyled())
        while self.PositionFromLine(lineNr) > -1:
            line = self.GetLine(lineNr)
            start = self.PositionFromLine(lineNr)
            length = self.LineLength(lineNr)
            self.StartStyling(start, 255)
            self.SetStyling(length, 0)
            if ';' in line:
                pos = line.index(';')
                self.StartStyling(start + pos, 31)
                self.SetStyling(length - pos, 1)
                length = pos

            has_g = False
            has_m = False
            pos = 0
            while pos < length:
                if line[pos] in " \t\n\r":
                    while pos < length and line[pos] in " \t\n\r":
                        pos += 1
                else:
                    end = pos
                    while end < length and not line[end] in " \t\n\r":
                        end += 1
                    if self.checkGCodePart(line[pos:end], start + pos):
                        self.StartStyling(start + pos, 0x20)
                        self.SetStyling(end - pos, 0x20)
                    if line[pos] == 'G':
                        has_g = True
                    if line[pos] == 'M':
                        has_m = True
                    pos = end
            if has_m:
                self.StartStyling(start, 31)
                self.SetStyling(length, 2)
            elif has_g:
                self.StartStyling(start, 31)
                self.SetStyling(length, 3)
            lineNr += 1

    def checkGCodePart(self, part, pos):
        if len(part) < 2:
            self.StartStyling(pos, 0x40)
            self.SetStyling(1, 0x40)
            return True
        if not part[0] in "GMXYZFESTBPIDCJ":
            self.StartStyling(pos, 0x40)
            self.SetStyling(1, 0x40)
            return True
        if part[1] == '{':
            if part[-1] != '}':
                return True
            tag = part[2:-1]
            # if not profile.isProfileSetting(tag) and not profile.isPreference(tag):
            #     self.StartStyling(pos + 2, 0x40)
            #     self.SetStyling(len(tag), 0x40)
            #     return True
        elif part[0] in "GM":
            try:
                code = int(part[1:])
            except ValueError:
                self.StartStyling(pos + 1, 0x40)
                self.SetStyling(len(part) - 1, 0x40)
                return True
            if part[0] == 'G':
                if not code in self.supportedGCodes:
                    return True
            if part[0] == 'M':
                if not code in self.supportedMCodes:
                    return True
        else:
            try:
                float(part[1:])
            except ValueError:
                self.StartStyling(pos + 1, 0x40)
                self.SetStyling(len(part) - 1, 0x40)
                return True
        return False

    def GetValue(self):
        return self.GetText()

    def SetValue(self, s):
        self.SetText(s)
