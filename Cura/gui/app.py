from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner
from kivy.uix.layout import Layout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButtonBehavior
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.actionbar import ActionBar
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.properties import ObjectProperty, NumericProperty, BooleanProperty, StringProperty, ListProperty, OptionProperty
from kivy.lang import Builder
from kivy.resources import resource_find
from kivy.graphics.transformation import Matrix
from kivy.graphics.opengl import *
from kivy.graphics import *

import sys

from Cura.gui.view3D.renderer import Renderer
from Cura.scene.printer3DScene import Printer3DScene
from Cura.machine.fdmprinter import FDMPrinter
from Cura.gui.view3D.printerView3D import PrinterView3D

Builder.load_string("""
<IconToggleButton>:
    BoxLayout:
        pos: self.parent.pos
        size: self.parent.size
        orientation: 'horizontal'
        padding: 2
        Image:
            source: self.parent.parent.icon
            width: self.height
            size_hint: (None, 1.0)
        Label:
            width: self.parent.size[0] - 32
            size_hint: (None, 1.0)
            text: self.parent.parent.button_text
            text_size: self.size
            valign: 'middle'
""")

class IconToggleButton(ToggleButtonBehavior, Button):
    button_text = StringProperty()
    icon = StringProperty()

    def __init__(self, **kwargs):
        self.button_text = kwargs['text']
        self.icon = kwargs['icon']
        kwargs['text'] = ''
        super(IconToggleButton, self).__init__(**kwargs)

class TopBarWidget(BoxLayout):
    pass

class TransformWidget(Widget):
    pass

class SettingsCategoriesWidget(BoxLayout):
    pass

class SettingCategoryButton(Button):
    category = ObjectProperty(None)

class SettingsDialog(BoxLayout):
    pass

class SettingWidget(BoxLayout):
    setting = ObjectProperty(None)

    def __init__(self, **kwargs):
        setting = kwargs['setting']
        super(SettingWidget, self).__init__(**kwargs)
        if setting.getType() == 'bool':
            self.add_widget(CheckBox(text=setting.getValue()))
        elif setting.getType() == 'float':
            self.add_widget(TextInput(text=setting.getValue()))
        elif type(setting.getType()) is list:
            self.add_widget(Spinner(text=setting.getValue(), values=setting.getType()))
        else:
            self.add_widget(TextInput(text=setting.getValue()))
            print 'Unknown setting type:', setting.getType()
        self.ids.label.text = setting.getLabel()

class CuraApp(App):
    def __init__(self):
        super(CuraApp, self).__init__()
        self._machine = FDMPrinter()
        self._scene = Printer3DScene()
        self._view = PrinterView3D()
        self._view.setScene(self._scene)
        self._view.setMachine(self._machine)

    def build(self):
        self.root.add_widget(self._view, len(self.root.children))
        self.update_setting_categories()
        #self.maximize()

    def update_setting_categories(self):
        settingsCategoryLayout = self.root.ids.settingsCategoriesDialog.ids.settingsCategoryLayout
        remove_list = []
        for c in settingsCategoryLayout.children:
            if isinstance(c, SettingCategoryButton):
                remove_list.append(c)
        for c in remove_list:
            settingsCategoryLayout.remove_widget(c)
        for category in self._machine.getSettingCategories():
            if category.isVisible():
                settingsCategoryLayout.add_widget(SettingCategoryButton(text=category.getLabel(), category=category), len(settingsCategoryLayout.children))

    def open_settings_category(self, categoryButton):
        settingsDialogLayout = self.root.ids.settingsDialogLayout
        while len(settingsDialogLayout.children) > 0:
            settingsDialogLayout.remove_widget(settingsDialogLayout.children[0])
        settingsDialog = SettingsDialog()
        self.root.ids.settingsDialogLayout.add_widget(settingsDialog)
        remove_list = []
        for c in settingsDialog.children:
            if isinstance(c, SettingWidget):
                remove_list.append(c)
        for c in remove_list:
            settingsDialog.remove_widget(c)
        for s in categoryButton.category.getSettings():
            widget = SettingWidget(setting=s)
            settingsDialog.add_widget(widget, len(settingsDialog.children) - 1)

        settingsDialogLayout.pos[0] = categoryButton.pos[0] - settingsDialog.size[0]
        settingsDialogLayout.pos[1] = -(settingsDialogLayout.size[1] - categoryButton.pos[1]) + categoryButton.size[1]

    def open_settings(self, *largs):
        pass #Stop the settings panel from showing on F1

    def maximize(self):
        if sys.platform.startswith('win'):
            import pygame
            from ctypes import windll
            SW_MAXIMIZE = 3
            windll.user32.ShowWindow(pygame.display.get_wm_info()['window'], SW_MAXIMIZE)
