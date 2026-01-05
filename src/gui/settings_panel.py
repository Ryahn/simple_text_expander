"""
Settings panel for Simple Text Expander
Manages whitelist and update preferences
"""
import customtkinter as ctk
from typing import Callable, Optional

from src.core.data_manager import DataManager
from src.core.app_monitor import AppMonitor
from src.utils.dialogs import SimpleDialog


class SettingsPanel(ctk.CTkFrame):
    """Settings panel for managing whitelist and updates"""
    
    def __init__(self, parent, data_manager: DataManager, 
                 on_settings_changed: Optional[Callable] = None):
        """
        Initialize settings panel
        
        Args:
            parent: Parent widget
            data_manager: DataManager instance
            on_settings_changed: Callback when settings change
        """
        super().__init__(parent)
        self.data_manager = data_manager
        self.app_monitor = AppMonitor()
        self.on_settings_changed = on_settings_changed
        
        self._create_widgets()
        self._load_settings()
    
    def _create_widgets(self):
        """Create UI widgets"""
        # Title
        title = ctk.CTkLabel(self, text="Settings", 
                            font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=20)
        
        # Whitelist section
        whitelist_frame = ctk.CTkFrame(self)
        whitelist_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        whitelist_title = ctk.CTkLabel(whitelist_frame, text="Application Whitelist",
                                      font=ctk.CTkFont(size=18, weight="bold"))
        whitelist_title.pack(pady=10)
        
        # Whitelist toggle
        self.whitelist_enabled_var = ctk.BooleanVar()
        whitelist_toggle = ctk.CTkSwitch(whitelist_frame, 
                                        text="Enable Whitelist",
                                        variable=self.whitelist_enabled_var,
                                        command=self._on_whitelist_toggle)
        whitelist_toggle.pack(pady=10)
        
        whitelist_info = ctk.CTkLabel(whitelist_frame, 
                                     text="When disabled or empty, runs globally on all applications",
                                     font=ctk.CTkFont(size=12))
        whitelist_info.pack(pady=5)
        
        # Whitelist list
        list_frame = ctk.CTkFrame(whitelist_frame)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        list_label = ctk.CTkLabel(list_frame, text="Whitelisted Applications:")
        list_label.pack(anchor="w", padx=10, pady=5)
        
        # Scrollable list
        self.whitelist_listbox = ctk.CTkScrollableFrame(list_frame, height=200)
        self.whitelist_listbox.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Buttons
        button_frame = ctk.CTkFrame(whitelist_frame)
        button_frame.pack(pady=10)
        
        add_btn = ctk.CTkButton(button_frame, text="Add Application",
                               command=self._add_application)
        add_btn.pack(side="left", padx=5)
        
        remove_btn = ctk.CTkButton(button_frame, text="Remove Selected",
                                  command=self._remove_application)
        remove_btn.pack(side="left", padx=5)
        
        refresh_btn = ctk.CTkButton(button_frame, text="Refresh Running Apps",
                                   command=self._refresh_running_apps)
        refresh_btn.pack(side="left", padx=5)
        
        # Running apps dropdown (for adding)
        self.running_apps_frame = ctk.CTkFrame(whitelist_frame)
        self.running_apps_frame.pack(fill="x", padx=10, pady=5)
        
        self.running_apps_var = ctk.StringVar(value="Select an application...")
        self.running_apps_dropdown = ctk.CTkComboBox(self.running_apps_frame,
                                                    variable=self.running_apps_var,
                                                    values=["Select an application..."])
        self.running_apps_dropdown.pack(side="left", padx=5, fill="x", expand=True)
        
        add_from_running_btn = ctk.CTkButton(self.running_apps_frame, text="Add",
                                            command=self._add_from_running)
        add_from_running_btn.pack(side="left", padx=5)
        
        self._refresh_running_apps()
    
    def _load_settings(self):
        """Load settings from data manager"""
        settings = self.data_manager.get_settings()
        self.whitelist_enabled_var.set(settings.get('whitelist_enabled', False))
        self._refresh_whitelist_list()
    
    def _refresh_whitelist_list(self):
        """Refresh the whitelist display"""
        # Clear existing items
        for widget in self.whitelist_listbox.winfo_children():
            widget.destroy()
        
        # Add whitelist items
        settings = self.data_manager.get_settings()
        whitelist_apps = settings.get('whitelist_apps', [])
        
        self.whitelist_items = []
        for i, app in enumerate(whitelist_apps):
            item_frame = ctk.CTkFrame(self.whitelist_listbox)
            item_frame.pack(fill="x", padx=5, pady=2)
            
            process_name = app.get('process_name', '')
            window_title = app.get('window_title', '')
            display_text = f"{process_name}"
            if window_title and window_title != process_name:
                display_text += f" - {window_title}"
            
            label = ctk.CTkLabel(item_frame, text=display_text, anchor="w")
            label.pack(side="left", padx=10, pady=5, fill="x", expand=True)
            
            self.whitelist_items.append((i, item_frame))
    
    def _on_whitelist_toggle(self):
        """Handle whitelist toggle"""
        enabled = self.whitelist_enabled_var.get()
        self.data_manager.update_settings({'whitelist_enabled': enabled})
        if self.on_settings_changed:
            self.on_settings_changed()
    
    def _add_application(self):
        """Show dialog to add application manually"""
        # Create input dialog for process name
        input_dialog = ctk.CTkToplevel(self)
        input_dialog.title("Add Application")
        input_dialog.geometry("400x200")
        input_dialog.transient(self)
        input_dialog.grab_set()
        
        process_name_var = ctk.StringVar()
        window_title_var = ctk.StringVar()
        result = [None, None]
        
        def save_and_close():
            result[0] = process_name_var.get().strip()
            result[1] = window_title_var.get().strip()
            input_dialog.destroy()
        
        ctk.CTkLabel(input_dialog, text="Process name (e.g., notepad.exe):").pack(pady=10, padx=20)
        process_entry = ctk.CTkEntry(input_dialog, textvariable=process_name_var, width=300)
        process_entry.pack(pady=5, padx=20)
        
        ctk.CTkLabel(input_dialog, text="Window title (optional):").pack(pady=10, padx=20)
        title_entry = ctk.CTkEntry(input_dialog, textvariable=window_title_var, width=300)
        title_entry.pack(pady=5, padx=20)
        
        btn_frame = ctk.CTkFrame(input_dialog)
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Add", command=save_and_close).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Cancel", command=input_dialog.destroy).pack(side="left", padx=5)
        
        input_dialog.wait_window()
        process_name = result[0]
        window_title = result[1] or ""
        
        if process_name:
            settings = self.data_manager.get_settings()
            whitelist_apps = settings.get('whitelist_apps', [])
            whitelist_apps.append({
                'process_name': process_name,
                'window_title': window_title
            })
            self.data_manager.update_settings({'whitelist_apps': whitelist_apps})
            self._refresh_whitelist_list()
            if self.on_settings_changed:
                self.on_settings_changed()
    
    def _add_from_running(self):
        """Add selected running application"""
        selected = self.running_apps_var.get()
        if selected == "Select an application..." or not selected:
            return
        
        # Parse the selection (format: "process_name - window_title")
        parts = selected.split(" - ", 1)
        process_name = parts[0]
        window_title = parts[1] if len(parts) > 1 else ""
        
        settings = self.data_manager.get_settings()
        whitelist_apps = settings.get('whitelist_apps', [])
        
        # Check if already added
        for app in whitelist_apps:
            if app.get('process_name') == process_name:
                return  # Already in whitelist
        
        whitelist_apps.append({
            'process_name': process_name,
            'window_title': window_title
        })
        self.data_manager.update_settings({'whitelist_apps': whitelist_apps})
        self._refresh_whitelist_list()
        if self.on_settings_changed:
            self.on_settings_changed()
    
    def _remove_application(self):
        """Remove selected application from whitelist"""
        # Find selected item (simple implementation - could be improved)
        # For now, remove last item or implement selection
        settings = self.data_manager.get_settings()
        whitelist_apps = settings.get('whitelist_apps', [])
        
        if whitelist_apps:
            # Remove last item (TODO: implement proper selection)
            whitelist_apps.pop()
            self.data_manager.update_settings({'whitelist_apps': whitelist_apps})
            self._refresh_whitelist_list()
            if self.on_settings_changed:
                self.on_settings_changed()
    
    def _refresh_running_apps(self):
        """Refresh list of running applications"""
        running_apps = self.app_monitor.get_running_apps()
        app_strings = ["Select an application..."]
        
        for app in running_apps[:50]:  # Limit to 50 apps
            process_name = app.get('process_name', '')
            window_title = app.get('window_title', '')
            if window_title and window_title != process_name:
                app_strings.append(f"{process_name} - {window_title}")
            else:
                app_strings.append(process_name)
        
        self.running_apps_dropdown.configure(values=app_strings)
        self.running_apps_var.set("Select an application...")

