import wx
import wx.wizard
from wx.lib.buttons import GenBitmapToggleButton

from Cura.machine.ultimaker2 import Ultimaker2
from Cura.machine.fdmprinter import FDMPrinter
from Cura.resources import getBitmap


class WizardPageBase(wx.wizard.PyWizardPage):
    def __init__(self, parent, title):
        super(WizardPageBase, self).__init__(parent)

        sizer = wx.GridBagSizer(2, 2)
        self._title = wx.StaticText(self, -1, title)
        self._title.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        sizer.Add(self._title, pos=(0, 0), span=(1, 2), flag=wx.ALIGN_CENTER)
        sizer.Add(wx.StaticLine(self), pos=(1, 0), span=(1, 2), flag=wx.EXPAND)
        self.SetSizer(sizer)
        self._row_nr = 2

        sizer.AddGrowableCol(1)

    def _addSettingTextBox(self, label, default_value):
        self.GetSizer().Add(wx.StaticText(self, -1, label), pos=(self._row_nr, 0))
        ctrl = wx.TextCtrl(self, -1, default_value)
        self.GetSizer().Add(ctrl, pos=(self._row_nr, 1))
        self._row_nr += 1
        return ctrl

    def _addLine(self):
        self.GetSizer().Add(wx.StaticLine(self), pos=(self._row_nr, 0), span=(1, 2), flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=10)
        self._row_nr += 1

    def _addText(self, text):
        self.GetSizer().Add(wx.StaticText(self, -1, text), pos=(self._row_nr, 0), span=(1, 2))
        self._row_nr += 1


class MainMachineSelectPage(wx.wizard.PyWizardPage):
    def __init__(self, parent):
        super(MainMachineSelectPage, self).__init__(parent)

        self._custom_page = CustomPrinterPage(self.GetParent())

        sizer = wx.GridBagSizer(2, 2)
        self._title = wx.StaticText(self, -1, _('Select your machine:'))
        self._title.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        sizer.Add(self._title, pos=(0, 0), span=(1, 2), flag=wx.ALIGN_CENTER)
        sizer.Add(wx.StaticLine(self), pos=(1, 0), span=(1, 2), flag=wx.EXPAND)
        self.SetSizer(sizer)

        self._printers = []

        self._addPrinterButton('ultimaker2.png', Ultimaker2Page(self.GetParent()))
        self._addPrinterButton('ultimaker_original.png', self._custom_page)
        self._addPrinterButton('other_printer.png', self._custom_page)

        sizer.AddGrowableCol(0)
        sizer.AddGrowableCol(1)
        self.GetParent().FindWindowById(wx.ID_FORWARD).Disable()

    def _addPrinterButton(self, image_name, next_page):
        printer = GenBitmapToggleButton(self, -1, getBitmap(image_name))
        self.GetSizer().Add(printer, pos=(2 + int(len(self._printers) / 2), len(self._printers) % 2))
        printer.Bind(wx.EVT_BUTTON, self._onPrinterSelect)
        printer.next_page = next_page
        self._printers.append(printer)

    def _onPrinterSelect(self, e):
        for printer in self._printers:
            printer.SetValue(False)
        printer_button = e.GetEventObject()
        printer_button.SetValue(True)
        self.GetParent().FindWindowById(wx.ID_FORWARD).Enable()

    def GetNext(self):
        for printer in self._printers:
            if printer.GetValue():
                return printer.next_page
        return self._custom_page


class Ultimaker2Page(WizardPageBase):
    def __init__(self, parent):
        super(Ultimaker2Page, self).__init__(parent, _('Ultimaker2'))

    def getMachine(self):
        return Ultimaker2()


class CustomPrinterPage(WizardPageBase):
    def __init__(self, parent):
        super(CustomPrinterPage, self).__init__(parent, _('Custom printer'))

        self._addText(_('Please configure the settings for your custom defined printer'))
        self._addLine()
        self._machine_name = self._addSettingTextBox(_('Machine name:'), 'RepRap (custom)')
        self._build_area_width = self._addSettingTextBox(_('Build area width (mm):'), '60')
        self._build_area_depth = self._addSettingTextBox(_('Build area depth (mm):'), '60')
        self._build_area_height = self._addSettingTextBox(_('Build area height (mm):'), '60')
        self._nozzle_size = self._addSettingTextBox(_('Nozzle diameter (mm):'), '0.5')
        self._addLine()
        self._addText(_('More advanced machine configuration settings can be set in the machine configuration later.'))

    def getMachine(self):
        machine = FDMPrinter()
        machine.getSettingByKey('machine_name').setValue(self._machine_name.GetValue())
        machine.getSettingByKey('machine_width').setValue(self._build_area_width.GetValue())
        machine.getSettingByKey('machine_depth').setValue(self._build_area_depth.GetValue())
        machine.getSettingByKey('machine_height').setValue(self._build_area_height.GetValue())
        machine.getSettingByKey('machine_nozzle_size').setValue(self._nozzle_size.GetValue())
        return machine


class NewDFMPrinterWizard(wx.wizard.Wizard):
    def __init__(self):
        super(NewDFMPrinterWizard, self).__init__(None, -1, 'New Printer')
        self._main_page = MainMachineSelectPage(self)

        self.FitToPage(self._main_page)
        self.GetPageAreaSizer().Add(self._main_page)

    def run(self):
        if self.RunWizard(self._main_page):
            final_page = self._main_page
            while final_page.GetNext() is not None:
                final_page = final_page.GetNext()
            self.Destroy()
            return final_page.getMachine()
        self.Destroy()
        return None
