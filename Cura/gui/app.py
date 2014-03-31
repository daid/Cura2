from Cura.scene.printer3DScene import Printer3DScene
from Cura.machine.fdmprinter import FDMPrinter
from Cura.gui.view3D.printerView3D import PrinterView3D

import sys
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


class TransformWidget(Widget):
    pass


class Renderer(Widget):
    def __init__(self, **kwargs):

        self.canvas = RenderContext(compute_normal_mat=True)
        self.canvas.shader.source = resource_find('simple.glsl')
        if(self.canvas.shader.source is None):
            print "Could not load shader" #todo; Add better checking for this!
        super(Renderer, self).__init__(**kwargs)
        with self.canvas:
            self.cb = Callback(self.setup_gl_context)
            ClearColor(0.8,0.8,0.8,1.0)
            ClearBuffers()
            PushMatrix()
            Color(1, 1, 1, 1)
            Translate(0, 0, -3)
            self.rot = Rotate(180, 0, 1, 0)
            UpdateNormalMatrix()
            Mesh(
                vertices=[0.0, 0.0, 0.0, 2.0,0.0,0.0, 0.0,2.0,0.0, 0.0,0.0,2.0],
                indices=[0,1,2,0,1,3],
                fmt=[('v_pos', 3, 'float')],
                mode='triangles',
            )
            PopMatrix()
            self.cb = Callback(self.reset_gl_context)

        Clock.schedule_interval(self.update_glsl, 1 / 60.)

    def setup_gl_context(self, *args):
        glEnable(GL_DEPTH_TEST)
        glViewport(self.pos[0], self.pos[1], self.width, self.height)

    def reset_gl_context(self, *args):
        glDisable(GL_DEPTH_TEST)
        glViewport(0, 0, self.get_root_window().width, self.get_root_window().height)

    def update_glsl(self, *args):
        asp = self.width / float(self.height)
        proj = Matrix().view_clip(-asp, asp, -1, 1, 1, 100, 1)
        self.canvas['projection_mat'] = proj
        self.canvas['diffuse_light'] = (1.0, 1.0, 0.8)
        self.canvas['ambient_light'] = (0.1, 0.1, 0.1)
        self.rot.angle += 1

class CuraApp(App):
    def __init__(self):
        super(CuraApp, self).__init__()
        self._machine = FDMPrinter()
        self._scene = Printer3DScene()
        self._view = PrinterView3D()
        self._view.setScene(self._scene)

    def build(self):
        pass
        '''mainLayout = FloatLayout()

        renderer = Renderer(size_hint=(1.0, 1.0), pos_hint={'x': 0, 'y': 0})
        mainLayout.add_widget(renderer)

        settingGroupsWidget = BoxLayout(orientation='vertical', size_hint=(None, None))
        for name in ['Resolution', 'Material', 'Support advice', 'Waterproof', 'Infill', 'Retraction', 'Fan/Cool', 'Skirt/Brim/Raft', 'Plugins', 'Load profile']:
            settingGroup = IconToggleButton(text=name, group='SettingGroup', icon='atlas://data/images/defaulttheme/checkbox_on')
            settingGroupsWidget.add_widget(settingGroup)
        settingGroupsWidget.size = (220, 40 * len(settingGroupsWidget.children))

        viewDirectionWidget = BoxLayout(orientation='horizontal')
        button3d = Button(text='3D')
        button3d.font_size = 9
        buttonRight = Button(text='Right')
        buttonRight.font_size = 9
        buttonFront = Button(text='Front')
        buttonFront.font_size = 9
        buttonTop = Button(text='Top')
        buttonTop.font_size = 9
        viewDirectionWidget.add_widget(button3d)
        viewDirectionWidget.add_widget(buttonRight)
        viewDirectionWidget.add_widget(buttonFront)
        viewDirectionWidget.add_widget(buttonTop)
        viewDirectionWidget.size = (40*4, 40)
        viewDirectionWidget.size_hint = (None, None)

        viewMode = Button(text='view mode', padding=(0,0))
        viewMode.font_size = 9
        viewMode.size = (40, 40)
        viewMode.size_hint = (None, None)

        b = StackLayout(orientation='lr-bt', spacing=25)
        b.add_widget(viewDirectionWidget)
        b.add_widget(viewMode)
        b.size_hint = (1.0, 1.0)
        b.pos_hint = {'x': 0, 'y': 0}
        mainLayout.add_widget(b)

        b = StackLayout(orientation='lr-tb', spacing=25)
        b.add_widget(settingGroupsWidget)
        b.size_hint = (1.0, 1.0)
        b.pos_hint = {'x': 0, 'y': 0}
        mainLayout.add_widget(b)

        #self.maximize()'''

        #return mainLayout

    def open_settings(self, *largs):
        pass #Stop the settings panel from showing on F1

    def maximize(self):
        if sys.platform.startswith('win'):
            import pygame
            from ctypes import windll
            SW_MAXIMIZE = 3
            windll.user32.ShowWindow(pygame.display.get_wm_info()['window'], SW_MAXIMIZE)
