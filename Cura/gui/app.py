from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.layout import Layout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButtonBehavior
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.stacklayout import StackLayout
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


class TestRenderer(Renderer):
    def __init__(self):
        super(TestRenderer, self).__init__()

    def _update(self, instructions):
        instructions.add(UpdateNormalMatrix())
        instructions.add(Mesh(
                vertices=[0.0, 0.0, 0.0, 2.0,0.0,0.0, 0.0,2.0,0.0, 0.0,0.0,2.0],
                indices=[0,1,2,0,1,3],
                fmt=[('v_pos', 3, 'float')],
                mode='triangles',
            ))


class TransformWidget(Widget):
    pass

class CuraApp(App):
    def __init__(self):
        super(CuraApp, self).__init__()
        self._machine = FDMPrinter()
        self._scene = Printer3DScene()
        self._view = PrinterView3D()
        self._view.setScene(self._scene)

    def build(self):
        self.root.add_widget(self._view, len(self.root.children))
        #self.maximize()

    def open_settings(self, *largs):
        pass #Stop the settings panel from showing on F1

    def maximize(self):
        if sys.platform.startswith('win'):
            import pygame
            from ctypes import windll
            SW_MAXIMIZE = 3
            windll.user32.ShowWindow(pygame.display.get_wm_info()['window'], SW_MAXIMIZE)
