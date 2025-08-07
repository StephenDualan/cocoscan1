from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image  # Use Image for local files
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.camera import Camera
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.properties import StringProperty, BooleanProperty
from kivy.graphics import Color, Rectangle
import os
import datetime
import cv2
import numpy as np
import threading

from database.db import get_user_scans, get_scan_statistics, save_scan, get_leaf_types, get_health_statuses, save_scan_with_error
from ui.clickable_logo import ClickableLogo, StyledClickableLogo
from ai_leaf_analyzer import LeafAnalyzer

LOGO_URL = "assets/cocoscan.png"

class DropZone(Widget):
    """Custom widget for drag and drop file upload"""
    file_path = StringProperty('')
    is_dragging = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Remove the problematic bindings that cause signature errors
        # Window.bind(on_drop_file=self.on_drop_file)
        
    def on_drop_file(self, window, file_path):
        """Handle dropped files"""
        try:
            # Convert bytes to string if needed
            if isinstance(file_path, bytes):
                file_path = file_path.decode('utf-8')
            
            # Check if it's an image file
            valid_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff']
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext in valid_extensions:
                self.file_path = file_path
                print(f"File dropped: {file_path}")
                # Trigger the callback
                if hasattr(self, 'on_file_dropped'):
                    self.on_file_dropped(file_path)
            else:
                print(f"Invalid file type: {file_ext}")
                
        except Exception as e:
            print(f"Error handling dropped file: {e}")
    
    def on_touch_down(self, touch):
        """Handle touch down for visual feedback"""
        if self.collide_point(*touch.pos):
            self.is_dragging = True
        return super().on_touch_down(touch)
    
    def on_touch_move(self, touch):
        """Handle touch move for visual feedback"""
        if self.collide_point(*touch.pos):
            self.is_dragging = True
        else:
            self.is_dragging = False
        return super().on_touch_move(touch)
    
    def on_touch_up(self, touch):
        """Handle touch up for visual feedback - Fixed signature"""
        if hasattr(self, 'is_dragging'):
            self.is_dragging = False
        return super().on_touch_up(touch)

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_user_id = None
        
        # Initialize AI analyzer
        self.ai_analyzer = LeafAnalyzer()
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Beautiful Clickable Logo with shadow effects
        logo_btn = StyledClickableLogo(logo_source=LOGO_URL, size_hint=(1, 0.3))
        logo_btn.bind(on_release=self.go_to_welcome)
        layout.add_widget(logo_btn)
        layout.add_widget(Label(text="Welcome to CocoScan - Coconut Leaf Analyzer", font_size="20sp", size_hint=(1, 0.1)))

        capture_btn = Button(text="📸 Capture Coconut Leaf", size_hint=(1, 0.1))
        capture_btn.bind(on_release=self.capture_leaf)
        layout.add_widget(capture_btn)

        history_btn = Button(text="📂 View Scan History", size_hint=(1, 0.1))
        history_btn.bind(on_release=self.view_history)
        layout.add_widget(history_btn)

        logout_btn = Button(text="🚪 Logout", size_hint=(1, 0.1), background_color=(0.8, 0.2, 0.2, 1))
        logout_btn.bind(on_release=self.logout)
        layout.add_widget(logout_btn)

        self.add_widget(layout)

    def set_user_id(self, user_id):
        """Set the current user ID"""
        self.current_user_id = user_id

    def capture_leaf(self, instance):
        # Option popup: Camera or Upload
        option_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        upload_btn = Button(text="🖼 Upload from File")
        upload_btn.bind(on_release=self.choose_file)

        camera_btn = Button(text="📷 Use Camera (simulated)")
        camera_btn.bind(on_release=self.use_camera)

        option_layout.add_widget(camera_btn)
        option_layout.add_widget(upload_btn)

        self.capture_popup = Popup(title="Choose Capture Method", content=option_layout,
                                   size_hint=(0.8, 0.4))
        self.capture_popup.open()

    def get_valid_default_directory(self):
        """Get a valid default directory that exists on the system"""
        possible_dirs = [
            os.path.expanduser("~\\Desktop"),
            os.path.expanduser("~\\Downloads"),
            os.path.expanduser("~\\Documents"),
            os.path.expanduser("~\\Pictures"),
            os.path.expanduser("~"),
            "C:\\",
        ]
        
        for directory in possible_dirs:
            if os.path.exists(directory) and os.path.isdir(directory):
                return directory
        
        # Fallback to current directory
        return os.getcwd()

    def choose_file(self, instance):
        self.capture_popup.dismiss()

        # Get a valid default directory
        default_dir = self.get_valid_default_directory()

        # Create enhanced file chooser layout
        chooser_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Drag and Drop Zone
        drop_zone_layout = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, 0.15))
        drop_zone_layout.canvas.before.add(Color(0.9, 0.95, 1, 1))  # Light blue background
        drop_zone_layout.canvas.before.add(Rectangle(pos=drop_zone_layout.pos, size=drop_zone_layout.size))
        
        drop_label = Label(
            text="🥥 Drag & Drop Coconut Leaf Images Here\nor click to browse files",
            size_hint=(1, 0.8),
            color=(0.2, 0.4, 0.8, 1),
            font_size="14sp"
        )
        drop_zone_layout.add_widget(drop_label)
        
        # Create drop zone widget
        drop_zone = DropZone(size_hint=(1, 0.2))
        drop_zone_layout.add_widget(drop_zone)
        
        chooser_layout.add_widget(drop_zone_layout)
        
        # Current path display (editable) - Full path visibility
        from kivy.uix.textinput import TextInput
        path_display = TextInput(
            text=default_dir,
            size_hint=(1, 0.12),  # Made larger for full path visibility
            readonly=False,  # Now editable
            background_color=(0.9, 0.9, 0.9, 1),
            foreground_color=(0, 0, 0, 1),
            font_size="11sp",  # Slightly smaller font to fit more text
            multiline=False,
            padding=(10, 10),  # Add padding for better visibility
            hint_text="Type or paste full path here and press Enter"
        )
        chooser_layout.add_widget(Label(text="📁 Full Directory Path (Editable):", size_hint=(1, 0.06)))
        chooser_layout.add_widget(path_display)
        
        # File chooser with better settings - Show full paths
        try:
            chooser = FileChooserIconView(
                path=default_dir,
                filters=['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.gif', '*.tiff'],
                dirselect=True,
                multiselect=False
            )
        except Exception as e:
            # Fallback to current directory if default_dir fails
            try:
                chooser = FileChooserIconView(
                    path=os.getcwd(),
                    filters=['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.gif', '*.tiff'],
                    dirselect=True,
                    multiselect=False
                )
                path_display.text = os.getcwd()
                file_info.text = f"Using fallback directory: {os.getcwd()}"
                file_info.color = (0.7, 0.5, 0, 1)
            except Exception as e2:
                # Last resort - use root directory
                chooser = FileChooserIconView(
                    path="C:\\",
                    filters=['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.gif', '*.tiff'],
                    dirselect=True,
                    multiselect=False
                )
                path_display.text = "C:\\"
                file_info.text = f"Using root directory due to errors: {str(e2)}"
                file_info.color = (0.7, 0, 0, 1)
        
        chooser_layout.add_widget(chooser)
        
        # Navigation buttons
        nav_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.1))
        
        # Quick access buttons
        home_btn = Button(text="🏠 Home", size_hint=(0.2, 1))
        pictures_btn = Button(text="🖼 Pictures", size_hint=(0.2, 1))
        desktop_btn = Button(text="🖥 Desktop", size_hint=(0.2, 1))
        downloads_btn = Button(text="📥 Downloads", size_hint=(0.2, 1))
        up_btn = Button(text="⬆️ Up", size_hint=(0.2, 1))
        
        nav_layout.add_widget(home_btn)
        nav_layout.add_widget(pictures_btn)
        nav_layout.add_widget(desktop_btn)
        nav_layout.add_widget(downloads_btn)
        nav_layout.add_widget(up_btn)
        
        chooser_layout.add_widget(nav_layout)
        
        # Action buttons
        action_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.1))
        
        select_btn = Button(text="📸 Select Coconut Leaf Image", size_hint=(0.7, 1), background_color=(0, 0.7, 0, 1))
        cancel_btn = Button(text="❌ Cancel", size_hint=(0.3, 1), background_color=(0.7, 0, 0, 1))
        
        action_layout.add_widget(select_btn)
        action_layout.add_widget(cancel_btn)
        chooser_layout.add_widget(action_layout)
        
        # Selected file info - Show full paths
        file_info = Label(
            text="No file selected", 
            size_hint=(1, 0.12),  # Made larger for full path display
            color=(0.5, 0.5, 0.5, 1),
            font_size="10sp",  # Smaller font to fit more text
            text_size=(None, None),  # Allow text to wrap
            halign='left',
            valign='top'
        )
        chooser_layout.add_widget(file_info)
        
        # Create popup
        popup = Popup(
            title="🥥 Select Coconut Leaf Image",
            content=chooser_layout,
            size_hint=(0.95, 0.9)
        )
        
        # Handle dropped files
        def on_file_dropped(file_path):
            print(f"Processing dropped file: {file_path}")
            # Copy file to Downloads folder
            downloads_path = self.copy_to_downloads(file_path)
            if downloads_path:
                self.process_scan_result("Healthy", 0.95, downloads_path)
                popup.dismiss()
            else:
                self.show_error("Failed to copy dropped file to Downloads")
        
        # Set the callback for dropped files
        drop_zone.on_file_dropped = on_file_dropped
        
        # Navigation functions
        def go_home(instance):
            try:
                home_path = os.path.expanduser("~")
                if os.path.exists(home_path) and os.path.isdir(home_path):
                    chooser.path = home_path
                    path_display.text = home_path
                    file_info.text = f"Navigated to: {home_path}"
                    file_info.color = (0, 0.7, 0, 1)
                else:
                    file_info.text = f"Home directory not accessible: {home_path}"
                    file_info.color = (0.7, 0, 0, 1)
            except Exception as e:
                file_info.text = f"Error accessing home directory: {str(e)}"
                file_info.color = (0.7, 0, 0, 1)
        
        def go_pictures(instance):
            try:
                pictures_path = os.path.expanduser("~\\Pictures")
                if os.path.exists(pictures_path) and os.path.isdir(pictures_path):
                    chooser.path = pictures_path
                    path_display.text = pictures_path
                    file_info.text = f"Navigated to Pictures: {pictures_path}"
                    file_info.color = (0, 0.7, 0, 1)
                else:
                    # Try alternative paths
                    alt_paths = [
                        os.path.expanduser("~\\OneDrive\\Pictures"),
                        os.path.expanduser("~\\Documents\\Pictures"),
                        os.path.expanduser("~\\Desktop")
                    ]
                    for alt_path in alt_paths:
                        if os.path.exists(alt_path) and os.path.isdir(alt_path):
                            chooser.path = alt_path
                            path_display.text = alt_path
                            file_info.text = f"Using alternative path: {alt_path}"
                            file_info.color = (0.7, 0.5, 0, 1)
                            return
                    file_info.text = "Pictures folder not found. Try Desktop or Downloads."
                    file_info.color = (0.7, 0, 0, 1)
            except Exception as e:
                file_info.text = f"Error accessing Pictures: {str(e)}"
                file_info.color = (0.7, 0, 0, 1)
        
        def go_desktop(instance):
            try:
                desktop_path = os.path.expanduser("~\\Desktop")
                if os.path.exists(desktop_path) and os.path.isdir(desktop_path):
                    chooser.path = desktop_path
                    path_display.text = desktop_path
                    file_info.text = f"Navigated to Desktop: {desktop_path}"
                    file_info.color = (0, 0.7, 0, 1)
                else:
                    # Try alternative paths
                    alt_paths = [
                        os.path.expanduser("~\\OneDrive\\Desktop"),
                        os.path.expanduser("~\\Documents"),
                        os.path.expanduser("~")
                    ]
                    for alt_path in alt_paths:
                        if os.path.exists(alt_path) and os.path.isdir(alt_path):
                            chooser.path = alt_path
                            path_display.text = alt_path
                            file_info.text = f"Using alternative path: {alt_path}"
                            file_info.color = (0.7, 0.5, 0, 1)
                            return
                    file_info.text = "Desktop folder not found. Try Home directory."
                    file_info.color = (0.7, 0, 0, 1)
            except Exception as e:
                file_info.text = f"Error accessing Desktop: {str(e)}"
                file_info.color = (0.7, 0, 0, 1)
        
        def go_downloads(instance):
            try:
                downloads_path = os.path.expanduser("~\\Downloads")
                if os.path.exists(downloads_path) and os.path.isdir(downloads_path):
                    chooser.path = downloads_path
                    path_display.text = downloads_path
                    file_info.text = f"Navigated to Downloads: {downloads_path}"
                    file_info.color = (0, 0.7, 0, 1)
                else:
                    # Try alternative paths
                    alt_paths = [
                        os.path.expanduser("~\\OneDrive\\Downloads"),
                        os.path.expanduser("~\\Desktop"),
                        os.path.expanduser("~")
                    ]
                    for alt_path in alt_paths:
                        if os.path.exists(alt_path) and os.path.isdir(alt_path):
                            chooser.path = alt_path
                            path_display.text = alt_path
                            file_info.text = f"Using alternative path: {alt_path}"
                            file_info.color = (0.7, 0.5, 0, 1)
                            return
                    file_info.text = "Downloads folder not found. Try Desktop."
                    file_info.color = (0.7, 0, 0, 1)
            except Exception as e:
                file_info.text = f"Error accessing Downloads: {str(e)}"
                file_info.color = (0.7, 0, 0, 1)
        
        def go_up(instance):
            try:
                current_path = chooser.path
                parent_path = os.path.dirname(current_path)
                if parent_path and parent_path != current_path and os.path.exists(parent_path):
                    chooser.path = parent_path
                    path_display.text = parent_path
                    file_info.text = f"Navigated up to: {parent_path}"
                    file_info.color = (0, 0.7, 0, 1)
                else:
                    file_info.text = f"Cannot go up from: {current_path}"
                    file_info.color = (0.7, 0, 0, 1)
            except Exception as e:
                file_info.text = f"Error navigating up: {str(e)}"
                file_info.color = (0.7, 0, 0, 1)
        
        # Allow manual path entry with better validation
        def on_path_enter(instance):
            try:
                new_path = path_display.text.strip()
                if os.path.isdir(new_path):
                    chooser.path = new_path
                    file_info.text = f"Navigated to: {new_path}"
                    file_info.color = (0, 0.7, 0, 1)
                else:
                    file_info.text = f"Invalid directory: {new_path}"
                    file_info.color = (0.7, 0, 0, 1)
            except Exception as e:
                file_info.text = f"Error with path: {str(e)}"
                file_info.color = (0.7, 0, 0, 1)
        path_display.bind(on_text_validate=on_path_enter)
        
        # File selection function
        def on_file_select(instance, selection, touch=None):
            if selection:
                original_path = selection[0]
                file_info.text = f"Selected: {original_path}"
                file_info.color = (0, 0.7, 0, 1)  # Green for selected
                print(f"Selected coconut leaf image: {original_path}")
        
        # Final selection function
        def on_select_confirm(instance):
            if chooser.selection:
                original_path = chooser.selection[0]
                print(f"Processing coconut leaf image: {original_path}")
                
                # Copy file to Downloads folder
                downloads_path = self.copy_to_downloads(original_path)
                if downloads_path:
                    self.process_scan_result("Healthy", 0.95, downloads_path)
                else:
                    self.show_error("Failed to copy image to Downloads")
                popup.dismiss()
            else:
                self.show_error("Please select a coconut leaf image first")
        
        def on_cancel(instance):
            popup.dismiss()
        
        # Bind events
        home_btn.bind(on_release=go_home)
        pictures_btn.bind(on_release=go_pictures)
        desktop_btn.bind(on_release=go_desktop)
        downloads_btn.bind(on_release=go_downloads)
        up_btn.bind(on_release=go_up)
        
        chooser.bind(on_submit=on_file_select)
        chooser.bind(selection=lambda instance, value: on_file_select(instance, value))
        
        select_btn.bind(on_release=on_select_confirm)
        cancel_btn.bind(on_release=on_cancel)
        
        # Update path display when directory changes
        def update_path(instance, value):
            path_display.text = value
        
        chooser.bind(path=update_path)
        
        popup.open()

    def copy_to_downloads(self, original_path):
        """Copy selected image to Downloads folder"""
        try:
            import shutil
            from pathlib import Path
            
            # Get Downloads folder path
            downloads_path = str(Path.home() / "Downloads")
            
            # Create CocoScan folder in Downloads if it doesn't exist
            cocoscan_downloads = os.path.join(downloads_path, "CocoScan")
            if not os.path.exists(cocoscan_downloads):
                os.makedirs(cocoscan_downloads)
            
            # Generate unique filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            original_filename = os.path.basename(original_path)
            name, ext = os.path.splitext(original_filename)
            new_filename = f"leaf_upload_{timestamp}{ext}"
            
            # Full path for the new file
            new_path = os.path.join(cocoscan_downloads, new_filename)
            
            # Copy the file
            shutil.copy2(original_path, new_path)
            
            print(f"Image copied to: {new_path}")
            self.show_success(f"Image saved to Downloads/CocoScan/{new_filename}")
            
            return new_path
            
        except Exception as e:
            print(f"Error copying file: {e}")
            self.show_error(f"Failed to copy file: {e}")
            return None

    def use_camera(self, instance):
        self.capture_popup.dismiss()
        self.show_camera_capture()

    def show_camera_capture(self):
        """Show HD camera capture interface"""
        # Create camera layout
        camera_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # HD camera widget
        try:
            self.camera = Camera(play=True, resolution=(1280, 720))  # HD quality
            camera_layout.add_widget(self.camera)
        except Exception as e:
            # Fallback to SD if HD not available
            try:
                self.camera = Camera(play=True, resolution=(640, 480))
                camera_layout.add_widget(self.camera)
            except Exception as e2:
                camera_layout.add_widget(Label(text=f"Camera not available: {e2}"))
                self.camera = None
        
        # Simple camera controls
        controls_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.2))
        
        capture_btn = Button(text="📸 Capture", size_hint=(0.5, 1))
        capture_btn.bind(on_release=self.capture_image)
        
        close_btn = Button(text="❌ Close", size_hint=(0.5, 1))
        close_btn.bind(on_release=self.close_camera)
        
        controls_layout.add_widget(capture_btn)
        controls_layout.add_widget(close_btn)
        camera_layout.add_widget(controls_layout)
        
        # Create popup
        self.camera_popup = Popup(
            title="📷 HD Camera",
            content=camera_layout,
            size_hint=(0.9, 0.8)
        )
        self.camera_popup.open()

    def capture_image(self, instance):
        """Capture HD image from camera"""
        if not hasattr(self, 'camera') or self.camera is None:
            self.show_error("Camera not available")
            return
            
        try:
            if self.camera.play:
                # Create images directory if it doesn't exist
                images_dir = "images"
                if not os.path.exists(images_dir):
                    os.makedirs(images_dir)
                
                # Generate filename with quality info
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                resolution = f"{self.camera.resolution[0]}x{self.camera.resolution[1]}"
                filename = f"leaf_capture_{timestamp}_{resolution}.png"
                filepath = os.path.join(images_dir, filename)
                
                # Capture the image
                self.camera.export_to_png(filepath)
                
                # Store the image for AI analysis
                self.last_captured_image = cv2.imread(filepath)
                
                # Close camera popup
                self.camera_popup.dismiss()
                
                # Show success message
                self.show_success(f"HD Image captured: {filename}")
                
                # Process the scan
                self.process_scan_result("Healthy", 0.95, filepath)
            else:
                self.show_error("Camera is not playing")
                
        except Exception as e:
            self.show_error(f"Failed to capture image: {e}")

    def close_camera(self, instance):
        """Close camera"""
        if hasattr(self, 'camera') and self.camera.play:
            self.camera.play = False
        self.camera_popup.dismiss()

    def retake_photo(self, instance):
        """Retake photo - just close and reopen camera"""
        self.camera_popup.dismiss()
        Clock.schedule_once(lambda dt: self.show_camera_capture(), 0.1)

    def show_capture_preview(self, image_path, image_info=None):
        """Show captured image preview with confirm/cancel options"""
        preview_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Image preview
        try:
            preview_image = Image(source=image_path, size_hint=(1, 0.7))
            preview_layout.add_widget(preview_image)
        except Exception as e:
            preview_layout.add_widget(Label(text=f"Preview not available: {e}"))
        
        # Action buttons
        buttons_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.2))
        
        confirm_btn = Button(text="✅ Use This Image", size_hint=(0.5, 1), background_color=(0, 0.7, 0, 1))
        confirm_btn.bind(on_release=lambda x: self.confirm_capture(image_path))
        
        cancel_btn = Button(text="❌ Retake", size_hint=(0.5, 1), background_color=(0.7, 0, 0, 1))
        cancel_btn.bind(on_release=self.cancel_capture)
        
        buttons_layout.add_widget(confirm_btn)
        buttons_layout.add_widget(cancel_btn)
        preview_layout.add_widget(buttons_layout)
        
        # Preview popup
        self.preview_popup = Popup(
            title="📸 Image Preview",
            content=preview_layout,
            size_hint=(0.8, 0.7)
        )
        self.preview_popup.open()

    def confirm_capture(self, image_path):
        """Confirm the captured image and process it"""
        self.preview_popup.dismiss()
        
        # Stop camera if it's still running
        if hasattr(self, 'camera') and self.camera.play:
            self.camera.play = False
        
        # Process the scan (AI detection will be handled in process_scan_result)
        self.process_scan_result("Healthy", 0.95, image_path)

    def cancel_capture(self, instance):
        """Cancel the capture and return to camera"""
        self.preview_popup.dismiss()
        Clock.schedule_once(lambda dt: self.show_camera_capture(), 0.1)

    def process_scan_result(self, health_status, confidence, image_path):
        """Process and save scan result with AI analysis (now responsive, with error reporting)"""
        if not self.current_user_id:
            self.show_error("Please login first")
            return

        self.show_ai_analysis_progress()  # Show progress popup immediately

        def background_task():
            try:
                # Perform AI analysis (heavy work)
                analysis_results = self.ai_analyzer.analyze_leaf(image_path)

                # Check for Opisina arenosella detection
                if analysis_results.get('disease_name', '').strip().lower() == 'opisina arenosella':
                    Clock.schedule_once(lambda dt: self.show_success("Opisina arenosella detected in the image!"))

                # Save analysis results
                self.ai_analyzer.save_analysis(analysis_results, image_path)

                # Use AI results for database
                ai_health_status = analysis_results['disease_name']
                ai_confidence = analysis_results['overall_confidence']
                ai_leaf_type = analysis_results['leaf_name']

                # Save to database with AI results (with error reporting)
                scan_id, db_error = save_scan_with_error(
                    user_id=self.current_user_id,
                    leaf_type=ai_leaf_type,
                    health_status=ai_health_status,
                    confidence=ai_confidence,
                    image_path=image_path
                )

                def show_results(dt):
                    if scan_id:
                        self.show_ai_analysis_results(analysis_results, scan_id)
                    else:
                        self.show_error(f"Failed to save scan: {db_error}")

                Clock.schedule_once(show_results)

            except Exception as e:
                Clock.schedule_once(lambda dt: self.show_error(f"Error processing scan: {e}"))

        threading.Thread(target=background_task).start()

    def show_ai_analysis_progress(self):
        """Show AI analysis progress popup"""
        progress_layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        progress_layout.add_widget(Label(text="🤖 AI Analysis in Progress...", font_size="18sp"))
        progress_layout.add_widget(Label(text="Analyzing leaf image for disease detection", font_size="14sp"))
        progress_layout.add_widget(Label(text="Please wait...", font_size="12sp"))
        
        self.progress_popup = Popup(
            title="AI Analysis",
            content=progress_layout,
            size_hint=(0.7, 0.4)
        )
        self.progress_popup.open()

    def show_ai_analysis_results(self, analysis_results, scan_id):
        """Show detailed AI analysis results"""
        # Close progress popup
        if hasattr(self, 'progress_popup'):
            self.progress_popup.dismiss()
        
        # Create results layout
        results_layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        # Header
        header_text = f"🤖 AI Analysis Results (Scan #{scan_id})"
        results_layout.add_widget(Label(text=header_text, font_size="16sp", size_hint=(1, 0.1)))
        
        # Create scrollable content
        scroll = ScrollView(size_hint=(1, 0.8))
        content_layout = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        # Disease Detection
        disease_text = f"""
🔍 Disease Detection:
• Status: {analysis_results['disease_name']}
• Confidence: {analysis_results['disease_confidence']:.2%}
• Overall Confidence: {analysis_results['overall_confidence']:.2%}
        """
        content_layout.add_widget(Label(text=disease_text, size_hint_y=None, height=80))
        
        # Leaf Type
        leaf_text = f"""
🌿 Leaf Type:
• Type: {analysis_results['leaf_name']}
• Confidence: {analysis_results['leaf_confidence']:.2%}
        """
        content_layout.add_widget(Label(text=leaf_text, size_hint_y=None, height=60))
        
        # Image Quality
        if 'image_quality' in analysis_results:
            quality = analysis_results['image_quality']
            quality_text = f"""
📸 Image Quality:
• Quality Level: {quality.get('quality_level', 'Unknown')}
• Sharpness: {quality.get('sharpness', 0):.1f}
• Brightness: {quality.get('brightness', 0):.1f}
• Contrast: {quality.get('contrast', 0):.1f}
            """
            content_layout.add_widget(Label(text=quality_text, size_hint_y=None, height=100))
        
        # Color Analysis
        if 'color_analysis' in analysis_results:
            color = analysis_results['color_analysis']
            color_text = f"""
🎨 Color Analysis:
• Color Health: {color.get('color_health', 'Unknown')}
• Green Ratio: {color.get('green_ratio', 0):.2%}
• Yellow Ratio: {color.get('yellow_ratio', 0):.2%}
• Brown Ratio: {color.get('brown_ratio', 0):.2%}
            """
            content_layout.add_widget(Label(text=color_text, size_hint_y=None, height=100))
        
        # Texture Analysis
        if 'texture_analysis' in analysis_results:
            texture = analysis_results['texture_analysis']
            texture_text = f"""
🔍 Texture Analysis:
• Pattern: {texture.get('texture_pattern', 'Unknown')}
• Edge Density: {texture.get('edge_density', 0):.3f}
• Texture Variance: {texture.get('texture_variance', 0):.1f}
            """
            content_layout.add_widget(Label(text=texture_text, size_hint_y=None, height=80))
        
        # Recommendations
        if 'recommendations' in analysis_results:
            recommendations = analysis_results['recommendations']
            rec_text = "💡 Recommendations:\n"
            for i, rec in enumerate(recommendations, 1):
                rec_text += f"• {rec}\n"
            content_layout.add_widget(Label(text=rec_text, size_hint_y=None, height=len(recommendations) * 30 + 30))
        
        # Model Info
        model_text = f"""
🤖 Model Information:
• Model Used: {analysis_results.get('model_used', 'Unknown')}
• Analysis Time: {analysis_results.get('analysis_timestamp', 'Unknown')}
        """
        content_layout.add_widget(Label(text=model_text, size_hint_y=None, height=60))
        
        scroll.add_widget(content_layout)
        results_layout.add_widget(scroll)
        
        # Action buttons
        buttons_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.1))
        
        save_btn = Button(text="💾 Save Report", size_hint=(0.5, 1), background_color=(0, 0.7, 0, 1))
        save_btn.bind(on_release=lambda x: self.save_ai_report(analysis_results, scan_id))
        
        close_btn = Button(text="✅ Close", size_hint=(0.5, 1), background_color=(0.7, 0.7, 0.7, 1))
        close_btn.bind(on_release=self.close_ai_results)
        
        buttons_layout.add_widget(save_btn)
        buttons_layout.add_widget(close_btn)
        results_layout.add_widget(buttons_layout)
        
        # Show results popup
        self.ai_results_popup = Popup(
            title="🤖 AI Analysis Complete",
            content=results_layout,
            size_hint=(0.9, 0.8)
        )
        self.ai_results_popup.open()

    def save_ai_report(self, analysis_results, scan_id):
        """Save AI analysis report"""
        try:
            # The report is already saved by the analyzer
            self.show_success("✅ AI Report saved successfully!")
        except Exception as e:
            self.show_error(f"Error saving report: {e}")

    def close_ai_results(self, instance):
        """Close AI results popup"""
        if hasattr(self, 'ai_results_popup'):
            self.ai_results_popup.dismiss()

    def view_history(self, instance):
        if not self.current_user_id:
            self.show_error("Please login first")
            return

        try:
            scans = get_user_scans(self.current_user_id, limit=20)
        except Exception as e:
            self.show_error(f"Error loading history: {e}")
            return

        if not scans:
            self.show_info("No scan history found")
            return

        content = BoxLayout(orientation='vertical', spacing=5, padding=10)
        content.add_widget(Label(text="Scan History", size_hint=(1, 0.1), font_size="16sp"))

        scroll = ScrollView(size_hint=(1, 0.9))
        history_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        history_layout.bind(minimum_height=history_layout.setter('height'))

        for scan in scans:
            scan_id, leaf_type, health_status, confidence, image_path, notes, location, weather, scan_date = scan
            scan_text = f"ID: {scan_id} | {leaf_type} | {health_status} | {confidence:.2f} | {scan_date}"
            scan_label = Label(text=scan_text, size_hint_y=None, height=30)
            history_layout.add_widget(scan_label)

        scroll.add_widget(history_layout)
        content.add_widget(scroll)

        popup = Popup(title="Scan History", content=content, size_hint=(0.9, 0.8))
        popup.open()

    def view_statistics(self, instance):
        if not self.current_user_id:
            self.show_error("Please login first")
            return

        try:
            stats = get_scan_statistics(self.current_user_id)
        except Exception as e:
            self.show_error(f"Error loading statistics: {e}")
            return

        if not stats:
            self.show_info("No statistics available")
            return

        # Handle both dict and tuple/list return types
        if isinstance(stats, dict):
            total_scans = stats.get('total_scans', 0)
            avg_confidence = stats.get('avg_confidence', 0)
            healthy_count = stats.get('healthy_count', 0)
            diseased_count = stats.get('diseased_count', 0)
        elif isinstance(stats, (tuple, list)) and len(stats) >= 4:
            total_scans, avg_confidence, healthy_count, diseased_count = stats[:4]
        else:
            self.show_error("Statistics format error")
            return

        stats_text = f"""
        📊 Your Scan Statistics:

        Total Scans: {total_scans}
        Average Confidence: {avg_confidence}%
        Healthy Leaves: {healthy_count}
        Diseased Leaves: {diseased_count}
        """

        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        content.add_widget(Label(text=stats_text, size_hint=(1, 1)))

        popup = Popup(title="Statistics", content=content, size_hint=(0.8, 0.6))
        popup.open()

    def show_ai_tools(self, instance):
        """Show coconut-specific AI analysis tools menu"""
        tools_layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        # Header
        header = Label(text="🥥 Coconut AI Analysis Tools", font_size="18sp", size_hint=(1, 0.15))
        tools_layout.add_widget(header)
        
        # AI Tools Grid
        tools_grid = GridLayout(cols=2, spacing=10, size_hint=(1, 0.8))
        
        # Coconut Disease Pattern Detection
        disease_btn = Button(
            text="🔍 Coconut Diseases\nDetect lethal yellowing, bud rot, etc.",
            size_hint=(1, 1),
            background_color=(0.8, 0.2, 0.2, 1)
        )
        disease_btn.bind(on_release=self.detect_disease_patterns)
        tools_grid.add_widget(disease_btn)
        
        # Coconut Nutrient Analysis
        nutrient_btn = Button(
            text="🌱 Coconut Nutrients\nDetect coconut-specific deficiencies",
            size_hint=(1, 1),
            background_color=(0.2, 0.8, 0.2, 1)
        )
        nutrient_btn.bind(on_release=self.analyze_nutrients)
        tools_grid.add_widget(nutrient_btn)
        
        # Coconut Treatment Planning
        treatment_btn = Button(
            text="💊 Coconut Treatment\nGenerate coconut-specific treatments",
            size_hint=(1, 1),
            background_color=(0.2, 0.2, 0.8, 1)
        )
        treatment_btn.bind(on_release=self.generate_treatment_plan)
        tools_grid.add_widget(treatment_btn)
        
        # Coconut Disease Progression
        progression_btn = Button(
            text="📈 Coconut Progression\nPredict coconut disease timeline",
            size_hint=(1, 1),
            background_color=(0.8, 0.8, 0.2, 1)
        )
        progression_btn.bind(on_release=self.predict_progression)
        tools_grid.add_widget(progression_btn)
        
        # Coconut Trend Analysis
        trend_btn = Button(
            text="📊 Coconut Trends\nCompare coconut scan history",
            size_hint=(1, 1),
            background_color=(0.8, 0.2, 0.8, 1)
        )
        trend_btn.bind(on_release=self.analyze_trends)
        tools_grid.add_widget(trend_btn)
        
        # Coconut Image Enhancement
        enhance_btn = Button(
            text="✨ Coconut Image\nOptimize for coconut analysis",
            size_hint=(1, 1),
            background_color=(0.2, 0.8, 0.8, 1)
        )
        enhance_btn.bind(on_release=self.enhance_image)
        tools_grid.add_widget(enhance_btn)
        
        tools_layout.add_widget(tools_grid)
        
        # Close button
        close_btn = Button(text="❌ Close", size_hint=(1, 0.1), background_color=(0.7, 0.7, 0.7, 1))
        close_btn.bind(on_release=self.close_ai_tools)
        tools_layout.add_widget(close_btn)
        
        # Create popup
        self.ai_tools_popup = Popup(
            title="🥥 Coconut AI Analysis Tools",
            content=tools_layout,
            size_hint=(0.9, 0.8)
        )
        self.ai_tools_popup.open()

    def detect_disease_patterns(self, instance):
        """Detect specific disease patterns in the last captured image"""
        if not hasattr(self, 'last_captured_image'):
            self.show_error("No image available. Please capture an image first.")
            return
        
        try:
            # Show progress
            self.show_ai_analysis_progress()
            
            # Perform disease pattern detection
            patterns = self.ai_analyzer.detect_disease_patterns(self.last_captured_image)
            
            # Close progress
            if hasattr(self, 'progress_popup'):
                self.progress_popup.dismiss()
            
            # Show results
            self.show_disease_patterns_results(patterns)
            
        except Exception as e:
            self.show_error(f"Error detecting disease patterns: {e}")

    def analyze_nutrients(self, instance):
        """Analyze nutrient deficiencies"""
        if not hasattr(self, 'last_captured_image'):
            self.show_error("No image available. Please capture an image first.")
            return
        
        try:
            self.show_ai_analysis_progress()
            
            nutrients = self.ai_analyzer.analyze_nutrient_deficiency(self.last_captured_image)
            
            if hasattr(self, 'progress_popup'):
                self.progress_popup.dismiss()
            
            self.show_nutrient_analysis_results(nutrients)
            
        except Exception as e:
            self.show_error(f"Error analyzing nutrients: {e}")

    def generate_treatment_plan(self, instance):
        """Generate treatment plan based on analysis"""
        if not hasattr(self, 'last_analysis_results'):
            self.show_error("No analysis results available. Please analyze an image first.")
            return
        
        try:
            treatment_plan = self.ai_analyzer.generate_treatment_plan(self.last_analysis_results)
            self.show_treatment_plan_results(treatment_plan)
            
        except Exception as e:
            self.show_error(f"Error generating treatment plan: {e}")

    def predict_progression(self, instance):
        """Predict disease progression"""
        if not hasattr(self, 'last_analysis_results'):
            self.show_error("No analysis results available. Please analyze an image first.")
            return
        
        try:
            progression = self.ai_analyzer.predict_disease_progression(self.last_analysis_results)
            self.show_progression_results(progression)
            
        except Exception as e:
            self.show_error(f"Error predicting progression: {e}")

    def analyze_trends(self, instance):
        """Analyze trends with previous scans"""
        if not self.current_user_id:
            self.show_error("Please login first")
            return
        
        try:
            trends = self.ai_analyzer.compare_with_previous_scans(self.last_analysis_results, self.current_user_id)
            self.show_trend_analysis_results(trends)
            
        except Exception as e:
            self.show_error(f"Error analyzing trends: {e}")

    def enhance_image(self, instance):
        """Enhance image for better analysis"""
        if not hasattr(self, 'last_captured_image'):
            self.show_error("No image available. Please capture an image first.")
            return
        
        try:
            enhanced_image = self.enhance_image_quality(self.last_captured_image)
            self.show_enhanced_image_results(enhanced_image)
            
        except Exception as e:
            self.show_error(f"Error enhancing image: {e}")

    def close_ai_tools(self, instance):
        """Close AI tools popup"""
        if hasattr(self, 'ai_tools_popup'):
            self.ai_tools_popup.dismiss()

    def show_disease_patterns_results(self, patterns):
        """Show coconut disease pattern detection results"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        results_text = f"""
🥥 Coconut Disease Pattern Analysis:

🔍 Lethal Yellowing:
• Detected: {'Yes' if patterns.get('yellowing_detected', {}).get('detected', False) else 'No'}
• Confidence: {patterns.get('yellowing_detected', {}).get('confidence', 0):.1%}
• Severity: {patterns.get('yellowing_detected', {}).get('severity', 'Unknown')}

🌿 Root Wilt Signs:
• Detected: {'Yes' if patterns.get('root_wilt_signs', {}).get('detected', False) else 'No'}
• Confidence: {patterns.get('root_wilt_signs', {}).get('confidence', 0):.1%}
• Severity: {patterns.get('root_wilt_signs', {}).get('severity', 'Unknown')}

🍂 Bud Rot Indicators:
• Detected: {'Yes' if patterns.get('bud_rot_indicators', {}).get('detected', False) else 'No'}
• Confidence: {patterns.get('bud_rot_indicators', {}).get('confidence', 0):.1%}
• Severity: {patterns.get('bud_rot_indicators', {}).get('severity', 'Unknown')}

🔴 Leaf Spots:
• Detected: {'Yes' if patterns.get('leaf_spots', {}).get('detected', False) else 'No'}
• Confidence: {patterns.get('leaf_spots', {}).get('confidence', 0):.1%}
• Severity: {patterns.get('leaf_spots', {}).get('severity', 'Unknown')}

✅ Analysis: Coconut-specific pattern detection completed
        """
        
        content.add_widget(Label(text=results_text, size_hint=(1, 1)))
        
        popup = Popup(title="🥥 Coconut Disease Patterns", content=content, size_hint=(0.8, 0.7))
        popup.open()

    def show_nutrient_analysis_results(self, nutrients):
        """Show coconut-specific nutrient analysis results"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        results_text = "🥥 Coconut Nutrient Deficiency Analysis:\n\n"
        
        # Coconut-specific nutrients
        coconut_nutrients = {
            'nitrogen': 'Nitrogen (N) - Leaf growth',
            'phosphorus': 'Phosphorus (P) - Root development',
            'potassium': 'Potassium (K) - Fruit quality',
            'magnesium': 'Magnesium (Mg) - Chlorophyll',
            'iron': 'Iron (Fe) - Green color',
            'zinc': 'Zinc (Zn) - Leaf size',
            'boron': 'Boron (B) - Nut development'
        }
        
        for nutrient, description in coconut_nutrients.items():
            deficient = nutrients.get(nutrient, False)
            status = "❌ Deficient" if deficient else "✅ Normal"
            results_text += f"• {description}: {status}\n"
        
        results_text += "\n💡 Coconut-specific recommendations:\n"
        results_text += "• Apply balanced coconut fertilizer\n"
        results_text += "• Check soil pH (6.0-7.0 optimal)\n"
        results_text += "• Consider foliar feeding for quick recovery"
        
        content.add_widget(Label(text=results_text, size_hint=(1, 1)))
        
        popup = Popup(title="🥥 Coconut Nutrient Analysis", content=content, size_hint=(0.8, 0.7))
        popup.open()

    def show_treatment_plan_results(self, treatment_plan):
        """Show coconut-specific treatment plan results"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        scroll = ScrollView(size_hint=(1, 0.9))
        plan_layout = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        plan_layout.bind(minimum_height=plan_layout.setter('height'))
        
        # Immediate actions
        if treatment_plan.get('immediate_actions'):
            plan_layout.add_widget(Label(text="🚨 Immediate Coconut Actions:", size_hint_y=None, height=30))
            for action in treatment_plan['immediate_actions']:
                plan_layout.add_widget(Label(text=f"• {action}", size_hint_y=None, height=25))
        
        # Short term treatments
        if treatment_plan.get('short_term_treatments'):
            plan_layout.add_widget(Label(text="💊 Coconut Treatments:", size_hint_y=None, height=30))
            for treatment in treatment_plan['short_term_treatments']:
                plan_layout.add_widget(Label(text=f"• {treatment}", size_hint_y=None, height=25))
        
        # Monitoring schedule
        if treatment_plan.get('monitoring_schedule'):
            plan_layout.add_widget(Label(text="📅 Coconut Monitoring:", size_hint_y=None, height=30))
            for schedule in treatment_plan['monitoring_schedule']:
                plan_layout.add_widget(Label(text=f"• {schedule}", size_hint_y=None, height=25))
        
        scroll.add_widget(plan_layout)
        content.add_widget(scroll)
        
        popup = Popup(title="🥥 Coconut Treatment Plan", content=content, size_hint=(0.9, 0.8))
        popup.open()

    def show_progression_results(self, progression):
        """Show coconut disease progression results"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        results_text = f"""
🥥 Coconut Disease Progression:

• Current Stage: {progression.get('current_stage', 'Unknown')}
• Next Stage: {progression.get('next_stage', 'Unknown')}
• Time to Next Stage: {progression.get('time_to_next_stage', 'Unknown')}
• Recovery Probability: {progression.get('recovery_probability', 0):.1%}
• Spread Risk: {progression.get('spread_risk', 'Unknown')}
• Coconut-Specific Risk: {progression.get('coconut_risk', 'Unknown')}
        """
        
        content.add_widget(Label(text=results_text, size_hint=(1, 1)))
        
        popup = Popup(title="🥥 Coconut Disease Progression", content=content, size_hint=(0.8, 0.6))
        popup.open()

    def show_trend_analysis_results(self, trends):
        """Show coconut trend analysis results"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        results_text = f"""
🥥 Coconut Trend Analysis:

• Trend: {trends.get('trend', 'Unknown')}
• Change: {trends.get('change_percentage', 0):.1f}%
• Coconut Scans: {trends.get('scans_compared', 0)}
• Time Period: {trends.get('time_period', 'Unknown')}
• Coconut Recommendation: {trends.get('recommendation', 'Unknown')}
        """
        
        content.add_widget(Label(text=results_text, size_hint=(1, 1)))
        
        popup = Popup(title="🥥 Coconut Trend Analysis", content=content, size_hint=(0.8, 0.6))
        popup.open()

    def enhance_image_quality(self, img):
        """Enhance image quality for better analysis"""
        try:
            # Apply basic image enhancement
            enhanced = cv2.convertScaleAbs(img, alpha=1.2, beta=10)  # Increase contrast and brightness
            
            # Apply Gaussian blur to reduce noise
            enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)
            
            # Apply sharpening
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            enhanced = cv2.filter2D(enhanced, -1, kernel)
            
            return enhanced
            
        except Exception as e:
            print(f"Error enhancing image: {e}")
            return img

    def show_enhanced_image_results(self, enhanced_image):
        """Show enhanced image results"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        
        content.add_widget(Label(text="✨ Image Enhancement Complete", size_hint=(1, 0.2)))
        content.add_widget(Label(text="Enhanced image is ready for better analysis", size_hint=(1, 0.8)))
        
        popup = Popup(title="✨ Image Enhancement", content=content, size_hint=(0.8, 0.6))
        popup.open()

    def logout(self, instance):
        self.current_user_id = None
        self.manager.current = 'login'

    def go_to_welcome(self, *_):
        self.manager.current = 'welcome'

    def show_error(self, message):
        popup = Popup(title="Error",
                     content=Label(text=message),
                     size_hint=(0.8, 0.4))
        popup.open()

    def show_success(self, message):
        popup = Popup(title="Success",
                     content=Label(text=message),
                     size_hint=(0.8, 0.4))
        popup.open()

    def show_info(self, message):
        popup = Popup(title="Information",
                     content=Label(text=message),
                     size_hint=(0.8, 0.4))
        popup.open()

    def on_leave(self):
        """Clean up resources when leaving the screen"""
        # Stop camera if it's running
        if hasattr(self, 'camera') and self.camera.play:
            self.camera.play = False
        
        # Close any open popups
        if hasattr(self, 'camera_popup'):
            self.camera_popup.dismiss()
        if hasattr(self, 'preview_popup'):
            self.preview_popup.dismiss()
        if hasattr(self, 'capture_popup'):
            self.capture_popup.dismiss()
        if hasattr(self, 'ai_tools_popup'):
            self.ai_tools_popup.dismiss()
