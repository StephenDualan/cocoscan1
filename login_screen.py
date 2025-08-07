from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse, Line
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.popup import Popup
from kivy.properties import BooleanProperty

LOGO_URL = "assets/cocoscan.png"

class RoundedTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0, 0, 0, 0)
            self.bg_rect = RoundedRectangle(radius=[18], size=self.size, pos=self.pos)
        with self.canvas.after:
            Color(0.5, 0.5, 0.5, 1)
            self.outline = Line(width=1.2, rounded_rectangle=[self.x, self.y, self.width, self.height, 18])
        self.bind(pos=self.update_graphics, size=self.update_graphics)
        self.foreground_color = (0, 0, 0, 1)  # Always black text
    def update_graphics(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.outline.rounded_rectangle = [self.x, self.y, self.width, self.height, 18]

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = FloatLayout()

        # Green header with logo and gold circle
        header_height = 0.32
        header = Widget(size_hint=(1, header_height), pos_hint={'top': 1})
        with header.canvas:
            Color(0.15, 0.5, 0.32, 1)
            header.bg_rect = Rectangle(size=(self.width, self.height * header_height), pos=(0, self.height * (1 - header_height)))
        def update_header_rect(*args):
            header.bg_rect.size = (self.width, self.height * header_height)
            header.bg_rect.pos = (0, self.height * (1 - header_height))
        self.bind(size=update_header_rect, pos=update_header_rect)

        # Logo with gold circle (centered)
        logo_size = 90
        logo_container = FloatLayout(size_hint=(None, None), size=(logo_size, logo_size), pos_hint={'center_x': 0.5, 'center_y': 0.68})
        with logo_container.canvas:
            Color(0.95, 0.8, 0.3, 1)
            logo_container.circle = Ellipse(size=(logo_size, logo_size), pos=(0, 0))
        logo_img = Image(source=LOGO_URL, size_hint=(None, None), size=(logo_size * 0.7, logo_size * 0.7), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        logo_img.pos = (logo_size * 0.15, logo_size * 0.15)
        logo_container.add_widget(logo_img)
        header.add_widget(logo_container)
        root.add_widget(header)

        # White card with rounded top corners
        card_height = 0.68
        card = BoxLayout(orientation='vertical', padding=[24, 30, 24, 20], spacing=16, size_hint=(0.92, card_height), pos_hint={'center_x': 0.5, 'y': 0})
        with card.canvas.before:
            Color(1, 1, 1, 1)
            card.bg_rect = RoundedRectangle(size=(self.width * 0.92, self.height * card_height), pos=(self.width * 0.04, 0), radius=[(30, 30), (30, 30), (0, 0), (0, 0)])
        def update_card_rect(*args):
            card.bg_rect.size = (self.width * 0.92, self.height * card_height)
            card.bg_rect.pos = (self.width * 0.04, 0)
        self.bind(size=update_card_rect, pos=update_card_rect)

        # Login title
        title = Label(text="Login", font_size="22sp", color=(0, 0, 0, 1), size_hint=(1, 0.15), bold=True, halign="center", valign="middle")
        title.bind(size=title.setter('text_size'))
        card.add_widget(title)

        # Username field
        username_box = BoxLayout(orientation='vertical', size_hint=(1, 0.13), spacing=2)
        username_label = Label(text="Username:", color=(0, 0, 0, 1), font_size="15sp", size_hint=(1, 0.4), halign="left", valign="middle")
        username_label.bind(size=username_label.setter('text_size'))
        self.username_input = RoundedTextInput(multiline=False, size_hint=(1, 0.6), background_normal='', background_active='', background_color=(1, 1, 1, 1), foreground_color=(0, 0, 0, 1), padding=[10, 10, 10, 10], cursor_color=(0, 0.5, 0.32, 1), font_size="16sp", hint_text="Enter your username")
        username_box.add_widget(username_label)
        username_box.add_widget(self.username_input)
        card.add_widget(username_box)

        # Password field
        password_box = BoxLayout(orientation='vertical', size_hint=(1, 0.13), spacing=2)
        password_label = Label(text="Password:", color=(0, 0, 0, 1), font_size="15sp", size_hint=(1, 0.4), halign="left", valign="middle")
        password_label.bind(size=password_label.setter('text_size'))
        self.password_input = RoundedTextInput(password=True, multiline=False, size_hint=(1, 0.6), background_normal='', background_active='', background_color=(1, 1, 1, 1), foreground_color=(0, 0, 0, 1), padding=[10, 10, 10, 10], cursor_color=(0, 0.5, 0.32, 1), font_size="16sp", hint_text="Enter your password")
        password_box.add_widget(password_label)
        password_box.add_widget(self.password_input)
        card.add_widget(password_box)

        # Remember Me and Forgot Password
        options_row = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=10)
        self.remember_me = CheckBox(active=False, color=(0, 0.5, 0.32, 1), size_hint=(None, None), size=(22, 22))
        remember_label = Label(text="Remember Me", color=(0, 0, 0, 1), font_size="13sp", size_hint=(None, 1), width=110, halign="left", valign="middle")
        remember_label.bind(size=remember_label.setter('text_size'))
        forgot_btn = Button(text="Forgot Password?", background_normal='', background_color=(0, 0, 0, 0), color=(0.2, 0.5, 0.32, 1), font_size="13sp", size_hint=(None, 1), width=120, halign="right", valign="middle")
        forgot_btn.bind(on_release=self.forgot_password)
        options_row.add_widget(self.remember_me)
        options_row.add_widget(remember_label)
        options_row.add_widget(Widget())
        options_row.add_widget(forgot_btn)
        card.add_widget(options_row)

        # Enter button with shadow
        enter_btn_container = AnchorLayout(size_hint=(1, 0.18))
        enter_btn = Button(text="Enter", size_hint=(None, None), size=(110, 38), background_normal='', background_color=(0.15, 0.5, 0.32, 1), color=(1, 1, 1, 1), font_size="16sp", bold=True)
        with enter_btn.canvas.before:
            Color(0, 0, 0, 0.18)
            self.shadow = RoundedRectangle(size=(120, 48), pos=(enter_btn.x-5, enter_btn.y-5), radius=[12])
        def update_shadow(*args):
            self.shadow.size = (enter_btn.width+10, enter_btn.height+10)
            self.shadow.pos = (enter_btn.x-5, enter_btn.y-5)
        enter_btn.bind(pos=update_shadow, size=update_shadow)
        enter_btn.bind(on_release=self.attempt_login)
        enter_btn_container.add_widget(enter_btn)
        card.add_widget(enter_btn_container)

        # Signup link
        signup_btn = Button(text="Signup", background_normal='', background_color=(0, 0, 0, 0), color=(0.2, 0.5, 0.32, 1), font_size="14sp", size_hint=(1, 0.1))
        signup_btn.bind(on_release=self.go_to_signup)
        card.add_widget(signup_btn)

        root.add_widget(card)
        self.add_widget(root)

    def attempt_login(self, *_):
        # Implement your login logic here
        pass

    def forgot_password(self, *_):
        popup = Popup(title="Forgot Password", content=Label(text="Password reset not implemented."), size_hint=(0.7, 0.3))
        popup.open()

    def go_to_signup(self, *_):
        self.manager.current = 'signup'
