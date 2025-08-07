from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.properties import StringProperty, NumericProperty
from kivy.animation import Animation
from kivy.core.window import Window

class ClickableLogo(Button):
    """A beautiful clickable logo widget with hover effects and styling"""
    
    def __init__(self, logo_source="assets/cocoscan.png", **kwargs):
        super().__init__(**kwargs)
        
        # Set button properties for better appearance
        self.background_color = (0, 0, 0, 0)  # Transparent background
        self.border = (0, 0, 0, 0)  # No border
        self.background_normal = ''  # No default background
        self.background_down = ''    # No pressed background
        
        # Store the logo source
        self.logo_source = logo_source
        
        # Create the image widget with better properties
        self.image = AsyncImage(
            source=logo_source,
            allow_stretch=True,
            keep_ratio=True,
            anim_delay=0.1,
            anim_loop=0
        )
        self.add_widget(self.image)
        
        # Bind events for hover effects
        self.bind(size=self._update_image_size, pos=self._update_image_pos)
        self.bind(on_press=self._on_press)
        self.bind(on_release=self._on_release)
        
        # Animation properties
        self.scale = 1.0
        self.original_size = None
        
    def _update_image_size(self, instance, value):
        """Update the image size to match the button size"""
        if self.original_size is None:
            self.original_size = self.size
        self.image.size = self.size
    
    def _update_image_pos(self, instance, value):
        """Update the image position to match the button position"""
        self.image.pos = self.pos
    
    def _on_press(self, instance):
        """Handle press event with animation"""
        # Scale down slightly when pressed
        anim = Animation(scale=0.95, duration=0.1)
        anim.start(self)
        
    def _on_release(self, instance):
        """Handle release event with animation"""
        # Scale back to normal
        anim = Animation(scale=1.0, duration=0.1)
        anim.start(self)
    
    def on_scale(self, instance, value):
        """Update the widget size based on scale animation"""
        if self.original_size:
            self.size = (self.original_size[0] * value, self.original_size[1] * value)

class StyledClickableLogo(ClickableLogo):
    """Enhanced clickable logo with rounded corners and shadow effects"""
    
    def __init__(self, logo_source="assets/cocoscan.png", corner_radius=20, **kwargs):
        super().__init__(logo_source, **kwargs)
        
        self.corner_radius = corner_radius
        self.shadow_offset = 5
        
        # Add shadow and rounded corners
        with self.canvas.before:
            # Shadow
            Color(0, 0, 0, 0.3)
            self.shadow_rect = RoundedRectangle(
                size=self.size,
                pos=(self.x + self.shadow_offset, self.y - self.shadow_offset),
                radius=[self.corner_radius]
            )
            
            # Background with rounded corners
            Color(1, 1, 1, 0.1)
            self.bg_rect = RoundedRectangle(
                size=self.size,
                pos=self.pos,
                radius=[self.corner_radius]
            )
        
        # Bind size and pos changes to update graphics
        self.bind(size=self._update_graphics, pos=self._update_graphics)
    
    def _update_graphics(self, instance, value):
        """Update shadow and background graphics when size/pos changes"""
        if hasattr(self, 'shadow_rect'):
            self.shadow_rect.size = self.size
            self.shadow_rect.pos = (self.x + self.shadow_offset, self.y - self.shadow_offset)
            
        if hasattr(self, 'bg_rect'):
            self.bg_rect.size = self.size
            self.bg_rect.pos = self.pos

class GlowingClickableLogo(StyledClickableLogo):
    """Clickable logo with glowing effect on hover"""
    
    def __init__(self, logo_source="assets/cocoscan.png", **kwargs):
        super().__init__(logo_source, **kwargs)
        
        self.glow_animation = None
        self.is_hovered = False
        
        # Bind mouse events for hover detection
        Window.bind(mouse_pos=self._on_mouse_pos)
    
    def _on_mouse_pos(self, instance, pos):
        """Handle mouse position for hover effects"""
        if self.collide_point(*self.to_widget(*pos)):
            if not self.is_hovered:
                self.is_hovered = True
                self._start_glow()
        else:
            if self.is_hovered:
                self.is_hovered = False
                self._stop_glow()
    
    def _start_glow(self):
        """Start glowing animation"""
        if self.glow_animation:
            self.glow_animation.cancel(self)
        
        # Create pulsing glow effect
        self.glow_animation = Animation(scale=1.05, duration=0.5) + Animation(scale=1.0, duration=0.5)
        self.glow_animation.repeat = True
        self.glow_animation.start(self)
    
    def _stop_glow(self):
        """Stop glowing animation"""
        if self.glow_animation:
            self.glow_animation.cancel(self)
            self.glow_animation = None
        
        # Return to normal size
        anim = Animation(scale=1.0, duration=0.2)
        anim.start(self) 