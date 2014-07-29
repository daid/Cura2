import wx

from Cura.gui.widgets.gradientButton import GradientButton
from Cura.gui.fdmMachineConfigDialog import FDMMachineConfigDialog
from Cura.gui.newFDMprinterWizard import NewDFMPrinterWizard

class MachineButton(GradientButton):
    def __init__(self, parent, app):
        super(MachineButton, self).__init__(parent, 'Machine', '')
        self._app = app
        self.Bind(wx.EVT_BUTTON, self._onMachine)
        self.updateButton()

    def _onMachine(self, e):
        self._id_base = wx.NewId()
        popup = wx.Menu()
        machine_list = self._app.getMachineList()
        for machine in machine_list:
            wx.NewId()
            i = popup.AppendRadioItem(self._id_base + machine_list.index(machine), machine.getSettingValueByKey('machine_name'))
            if machine == self._app.getMachine():
                i.Check(True)
            i.machine = machine
            self.Bind(wx.EVT_MENU, self._onSwitchMachine, i)
        popup.AppendSeparator()
        i = popup.Append(-1, _("Edit machine configuration"))
        self.Bind(wx.EVT_MENU, self._onMachineEdit, i)
        i = popup.Append(-1, _("Add new machine"))
        self.Bind(wx.EVT_MENU, self._onNewMachine, i)
        self.PopupMenu(popup)

    def _onMachineEdit(self, e):
        FDMMachineConfigDialog(self._app).ShowModal()

    def _onNewMachine(self, e):
        wizard = NewDFMPrinterWizard()
        machine = wizard.run()
        if machine is not None:
            self._app.addMachine(machine)
            self._app.setMachine(machine)
            self.updateButton()

    def _onSwitchMachine(self, e):
        machine = self._app.getMachineList()[e.GetId() - self._id_base]
        if machine != self._app.getMachine():
            self._app.setMachine(machine)
            self.updateButton()

    def updateButton(self):
        self.SetLabel(self._app.getMachine().getSettingValueByKey('machine_name'))
        self.setIcon(self._app.getMachine().getSettingValueByKey('machine_icon'))