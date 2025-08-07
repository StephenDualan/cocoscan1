from kivy.config import Config
Config.set('graphics', 'width', '375')
Config.set('graphics', 'height', '812')
Config.set('graphics', 'resizable', '1')  # Allow window resizing

from kivy.core.window import Window
import sys
import os
import threading

if sys.platform in ['win32', 'linux', 'darwin']:
    os.environ['KIVY_WINDOW_CENTERED'] = '1'

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.uix.floatlayout import FloatLayout
from kivy.core.text import LabelBase

# Register a cartoon-like font if available (fallback to bold system font)
try:
    LabelBase.register(name="CocoFont", fn_regular="assets/comicbd.ttf")  # Place your cartoon font in assets/
    FONT_NAME = "CocoFont"
except Exception:
    FONT_NAME = None

from login_screen import LoginScreen
from home_screen import HomeScreen
from signup_screen import SignupScreen
from database.db import init_db

LOGO_URL = "assets/cocoscan.png"  # CocoScan logo

# --- Responsive Rounded Logo Widget ---
class ResponsiveRoundedLogo(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(1, 1, 1, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[100, 100, 100, 100])
        self.img = Image(source=LOGO_URL, allow_stretch=True, keep_ratio=True)
        self.add_widget(self.img)
        self.bind(pos=self.update_rect, size=self.update_rect)
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.img.size = self.size
        self.img.pos = self.pos

class LogoCircle(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            # Draw gold/yellow circle
            Color(0.95, 0.8, 0.3, 1)
            self.circle = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.width/2])
        self.logo = Image(source=LOGO_URL, allow_stretch=True, keep_ratio=True)
        self.add_widget(self.logo)
        self.bind(pos=self.update_graphics, size=self.update_graphics)
    def update_graphics(self, *args):
        d = min(self.width, self.height)
        self.circle.pos = (self.center_x - d/2, self.center_y - d/2)
        self.circle.size = (d, d)
        self.logo.size = (d*0.8, d*0.8)
        self.logo.pos = (self.center_x - d*0.4, self.center_y - d*0.4)

# --- Welcome Screen ---
class WelcomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Solid green background
        with self.canvas.before:
            Color(0.15, 0.5, 0.32, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        # Centered layout
        layout = BoxLayout(orientation='vertical', spacing=10, padding=[0, 0, 0, 0])
        layout.size_hint = (1, 1)
        layout.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

        # Spacer for vertical centering
        layout.add_widget(Widget(size_hint_y=0.38))

        # Palm tree emoji icon as a button
        icon_btn = Button(
            text="🌴",
            font_size="54sp",
            size_hint=(1, 0.12),
            background_normal='',
            background_down='',
            background_color=(0, 0, 0, 0),  # Fully transparent
            color=(1, 1, 1, 1),  # White emoji
            halign="center",
            valign="middle"
        )
        icon_btn.bind(on_release=self.go_to_login)
        layout.add_widget(icon_btn)

        # COCOSCAN text
        label_kwargs = dict(
            text="COCOSCAN",
            color=(1, 1, 1, 1),
            font_size="28sp",
            bold=True,
            size_hint=(1, 0.1),
            halign="center",
            valign="middle"
        )
        if FONT_NAME:
            label_kwargs['font_name'] = FONT_NAME
        title_label = Label(**label_kwargs)
        title_label.bind(size=title_label.setter('text_size'))
        layout.add_widget(title_label)

        # Spacer for vertical centering
        layout.add_widget(Widget(size_hint_y=0.4))

        self.add_widget(layout)

    def _update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def go_to_login(self, *_):
        self.manager.current = 'login'

# --- App Launcher ---
class CocoScanApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "CocoScan - Coconut Leaf Analyzer"
        self.icon = "assets/cocoscan.png"
    
    def build(self):
        # Initialize database in a background thread to avoid UI freeze
        threading.Thread(target=init_db, daemon=True).start()

        sm = ScreenManager()
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(SignupScreen(name='signup'))
        sm.add_widget(HomeScreen(name='home'))

        self.sm = sm
        return sm

if __name__ == '__main__':
    CocoScanApp().run()
