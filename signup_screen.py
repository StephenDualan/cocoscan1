from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from kivy.uix.popup import Popup

from database.db import create_user
from database.auth import create_simple_hash
from ui.clickable_logo import ClickableLogo, StyledClickableLogo

LOGO_URL = "assets/cocoscan.png"

class SignupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Beautiful Clickable Logo with shadow effects
        logo_btn = StyledClickableLogo(logo_source=LOGO_URL, size_hint=(1, 0.3))
        logo_btn.bind(on_release=self.go_to_welcome)
        layout.add_widget(logo_btn)
        layout.add_widget(Label(text="Sign Up for CocoScan", font_size="20sp", size_hint=(1, 0.1)))

        self.username = TextInput(hint_text="Choose a username", multiline=False, size_hint=(1, 0.1))
        self.password = TextInput(hint_text="Choose a password", multiline=False, password=True, size_hint=(1, 0.1))
        self.confirm = TextInput(hint_text="Confirm password", multiline=False, password=True, size_hint=(1, 0.1))
        self.email = TextInput(hint_text="Email (optional)", multiline=False, size_hint=(1, 0.1))

        layout.add_widget(self.username)
        layout.add_widget(self.password)
        layout.add_widget(self.confirm)
        layout.add_widget(self.email)

        signup_btn = Button(text="Sign Up", size_hint=(1, 0.15), background_color=(0.1, 0.6, 0.4, 1))
        signup_btn.bind(on_release=self.create_account)
        layout.add_widget(signup_btn)

        self.feedback = Label(text="", size_hint=(1, 0.1), color=(1, 0, 0, 1))
        layout.add_widget(self.feedback)

        back_btn = Button(text="⬅ Back to Login", size_hint=(1, 0.1))
        back_btn.bind(on_release=self.go_to_login)
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def create_account(self, *_):
        username = self.username.text.strip()
        password = self.password.text.strip()
        confirm = self.confirm.text.strip()
        email = self.email.text.strip()

        if not username or not password:
            self.feedback.text = "Username and password cannot be empty."
            return
        
        if len(username) < 3:
            self.feedback.text = "Username must be at least 3 characters long."
            return
        
        if len(password) < 6:
            self.feedback.text = "Password must be at least 6 characters long."
            return
        
        if password != confirm:
            self.feedback.text = "Passwords do not match."
            return
        
        # Hash the password
        password_hash = create_simple_hash(password)
        
        # Create user account
        user_id = create_user(username, password_hash, email if email else None)
        
        if user_id:
            self.show_success("Account created successfully! Please login.")
            self.clear_inputs()
            self.manager.current = "login"
        else:
            self.feedback.text = "Username already exists. Please choose another."
    
    def clear_inputs(self):
        """Clear all input fields"""
        self.username.text = ""
        self.password.text = ""
        self.confirm.text = ""
        self.email.text = ""
        self.feedback.text = ""
    
    def show_success(self, message):
        popup = Popup(title="Success", 
                     content=Label(text=message),
                     size_hint=(0.8, 0.4))
        popup.open()
        
    def go_to_welcome(self, *_):
        self.manager.current = 'welcome'
        
    def go_to_login(self, *_):
        self.manager.current = 'login'
