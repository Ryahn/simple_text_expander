"""
Main window for Simple Text Expander
"""
import customtkinter as ctk
import tkinter.filedialog as filedialog
from pathlib import Path
from typing import Optional

from src.core.data_manager import DataManager
from src.core.expansion_engine import ExpansionEngine
from src.gui.groups_panel import GroupsPanel
from src.gui.expansions_panel import ExpansionsPanel
from src.gui.settings_panel import SettingsPanel
from src.utils.update_checker import UpdateChecker
from src.utils.dialogs import show_message, show_question
from src.config import APP_NAME, APP_VERSION


class MainWindow(ctk.CTk):
    """Main application window"""
    
    def __init__(self):
        """Initialize main window"""
        super().__init__()
        
        # Set dark theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry("1000x700")
        
        # Initialize core components
        self.data_manager = DataManager()
        self.expansion_engine = ExpansionEngine(self.data_manager)
        self.expansion_engine.on_status_changed = self._on_engine_status_changed
        
        # Create UI
        self._create_widgets()
        
        # Load initial data
        self._refresh_groups()
        
        # Check for updates on startup (optional)
        # self._check_updates_on_startup()
    
    def _create_widgets(self):
        """Create main window widgets"""
        # Top bar with status and controls
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(fill="x", padx=10, pady=10)
        
        # Status label
        self.status_label = ctk.CTkLabel(top_frame, text="Status: Stopped",
                                        font=ctk.CTkFont(size=14, weight="bold"))
        self.status_label.pack(side="left", padx=10)
        
        # Start/Stop button
        self.start_stop_btn = ctk.CTkButton(top_frame, text="Start Monitoring",
                                           command=self._toggle_monitoring)
        self.start_stop_btn.pack(side="left", padx=10)
        
        # Menu buttons
        export_btn = ctk.CTkButton(top_frame, text="Export JSON",
                                  command=self._export_json)
        export_btn.pack(side="left", padx=5)
        
        import_btn = ctk.CTkButton(top_frame, text="Import JSON",
                                 command=self._import_json)
        import_btn.pack(side="left", padx=5)
        
        check_update_btn = ctk.CTkButton(top_frame, text="Check Updates",
                                       command=self._check_updates)
        check_update_btn.pack(side="left", padx=5)
        
        # Tab view
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Groups & Expansions tab
        expansions_tab = self.tabview.add("Expansions")
        
        # Split into two panes
        main_panes = ctk.CTkFrame(expansions_tab)
        main_panes.pack(fill="both", expand=True)
        
        # Left pane - Groups
        groups_pane = ctk.CTkFrame(main_panes, width=300)
        groups_pane.pack(side="left", fill="both", padx=5, pady=5)
        groups_pane.pack_propagate(False)
        
        self.groups_panel = GroupsPanel(groups_pane, 
                                        on_group_selected=self._on_group_selected,
                                        on_group_edit=self._edit_group)
        self.groups_panel.pack(fill="both", expand=True)
        
        # Wire up group panel buttons directly
        self.groups_panel.add_btn.configure(command=self._add_group)
        self.groups_panel.edit_btn.configure(command=self._edit_group)
        self.groups_panel.delete_btn.configure(command=self._delete_group)
        
        # Right pane - Expansions
        expansions_pane = ctk.CTkFrame(main_panes)
        expansions_pane.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        self.expansions_panel = ExpansionsPanel(expansions_pane,
                                               on_expansion_changed=self._on_expansion_changed)
        self.expansions_panel.pack(fill="both", expand=True)
        
        # Wire up expansion panel buttons directly
        self.expansions_panel.add_btn.configure(command=self._add_expansion)
        self.expansions_panel.edit_btn.configure(command=self._edit_expansion)
        self.expansions_panel.delete_btn.configure(command=self._delete_expansion)
        
        # Settings tab
        settings_tab = self.tabview.add("Settings")
        
        self.settings_panel = SettingsPanel(settings_tab, self.data_manager,
                                           on_settings_changed=self._on_settings_changed)
        self.settings_panel.pack(fill="both", expand=True)
        
        # About tab
        about_tab = self.tabview.add("About")
        self._create_about_tab(about_tab)
    
    def _create_about_tab(self, parent):
        """Create about tab content"""
        about_text = f"""
{APP_NAME}

Version {APP_VERSION}

A cross-platform text expansion application.

Features:
• Global keyboard monitoring
• Application whitelisting
• Grouped expansions
• Custom prefixes
• Immediate or delayed triggers
• JSON import/export
• Automatic updates

© 2024
"""
        about_label = ctk.CTkLabel(parent, text=about_text,
                                  font=ctk.CTkFont(size=12),
                                  justify="left")
        about_label.pack(pady=50)
    
    def _toggle_monitoring(self):
        """Toggle expansion engine on/off"""
        if self.expansion_engine.is_running:
            self.expansion_engine.stop()
        else:
            self.expansion_engine.start()
    
    def _on_engine_status_changed(self, is_running: bool):
        """Handle expansion engine status change"""
        if is_running:
            self.status_label.configure(text="Status: Running", 
                                       text_color="green")
            self.start_stop_btn.configure(text="Stop Monitoring")
        else:
            self.status_label.configure(text="Status: Stopped",
                                       text_color="red")
            self.start_stop_btn.configure(text="Start Monitoring")
    
    def _refresh_groups(self):
        """Refresh groups display"""
        groups = self.data_manager.get_groups()
        self.groups_panel.update_groups(groups)
    
    def _on_group_selected(self, group_id: str):
        """Handle group selection"""
        group = self.data_manager.get_group(group_id)
        if group:
            self.expansions_panel.update_group(
                group_id,
                group['name'],
                group.get('expansions', [])
            )
    
    def _on_expansion_changed(self):
        """Handle expansion changes"""
        self.expansion_engine.refresh_expansions()
        # Refresh current group display
        selected_id = self.groups_panel.get_selected_group_id()
        if selected_id:
            self._on_group_selected(selected_id)
    
    def _on_settings_changed(self):
        """Handle settings changes"""
        # Settings changed, expansion engine will check whitelist on next trigger
        pass
    
    def _add_group(self):
        """Add a new group"""
        group_name = self.groups_panel._add_group()
        if group_name:
            self.data_manager.add_group(group_name)
            self._refresh_groups()
    
    def _edit_group(self):
        """Edit selected group"""
        result = self.groups_panel._edit_group()
        if result:
            group_id, new_name = result
            self.data_manager.update_group(group_id, new_name)
            self._refresh_groups()
    
    def _delete_group(self):
        """Delete selected group"""
        group_id = self.groups_panel._delete_group()
        if group_id:
            self.data_manager.delete_group(group_id)
            self._refresh_groups()
            self.expansions_panel.clear()
            self.expansion_engine.refresh_expansions()
    
    def _add_expansion(self):
        """Add a new expansion"""
        selected_id = self.groups_panel.get_selected_group_id()
        if not selected_id:
            show_message(self, "Error", "Please select a group first!")
            return
        
        result = self.expansions_panel._add_expansion()
        if result:
            # Check prefix uniqueness
            if not self.data_manager.is_prefix_unique(result['prefix']):
                show_message(self, "Error", "Prefix already exists!")
                return
            
            self.data_manager.add_expansion(
                selected_id,
                result['prefix'],
                result['text'],
                result['description'],
                result['trigger_immediate'],
                result['trigger_delay_ms']
            )
            self._on_expansion_changed()
    
    def _edit_expansion(self):
        """Edit selected expansion"""
        selected_group_id = self.groups_panel.get_selected_group_id()
        if not selected_group_id:
            show_message(self, "Error", "Please select a group first!")
            return
        
        result = self.expansions_panel._edit_expansion()
        if result:
            expansion_id = self.expansions_panel.get_selected_expansion_id()
            if not expansion_id:
                show_message(self, "Error", "Please select an expansion to edit!")
                return
            
            # Get the original expansion to check prefix uniqueness
            group = self.data_manager.get_group(selected_group_id)
            original_expansion = None
            for exp in group.get('expansions', []):
                if exp['id'] == expansion_id:
                    original_expansion = exp
                    break
            
            # Check prefix uniqueness (excluding current expansion's prefix)
            if original_expansion and result['prefix'] != original_expansion.get('prefix'):
                if not self.data_manager.is_prefix_unique(result['prefix']):
                    show_message(self, "Error", "Prefix already exists!")
                    return
            
            # Update the expansion
            self.data_manager.update_expansion(
                selected_group_id,
                expansion_id,
                result['prefix'],
                result['text'],
                result['description'],
                result['trigger_immediate'],
                result['trigger_delay_ms']
            )
            self._on_expansion_changed()
    
    def _delete_expansion(self):
        """Delete selected expansion"""
        selected_id = self.groups_panel.get_selected_group_id()
        if not selected_id:
            show_message(self, "Error", "Please select a group first!")
            return
        
        # TODO: Implement selection tracking for expansions
        show_message(self, "Info", "Expansion deletion - select expansion to delete (coming soon)")
    
    def _export_json(self):
        """Export data to JSON file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Expansions"
        )
        
        if file_path:
            if self.data_manager.export_json(Path(file_path)):
                show_message(self, "Success", "Expansions exported successfully!")
            else:
                show_message(self, "Error", "Failed to export expansions!")
    
    def _import_json(self):
        """Import data from JSON file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Import Expansions"
        )
        
        if file_path:
            response = show_question(self, "Import Options",
                                    "Replace all data or merge?",
                                    ["Replace", "Merge", "Cancel"])
            
            if response == "Replace":
                merge = False
            elif response == "Merge":
                merge = True
            else:
                return
            
            if self.data_manager.import_json(Path(file_path), merge=merge):
                self._refresh_groups()
                self.expansion_engine.refresh_expansions()
                show_message(self, "Success", "Expansions imported successfully!")
            else:
                show_message(self, "Error", "Failed to import expansions!")
    
    def _check_updates(self):
        """Check for application updates"""
        checker = UpdateChecker()
        is_available, latest_version, download_url, release_notes = checker.is_update_available()
        
        if is_available:
            message = f"Update available!\n\nCurrent: {APP_VERSION}\nLatest: {latest_version}\n\n{release_notes[:200] if release_notes else 'No release notes'}..."
            response = show_question(self, "Update Available",
                                    message,
                                    ["Download", "Later"])
            
            if response == "Download" and download_url:
                # Download update (simplified - in production, handle this better)
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".exe" if download_url.endswith(".exe") else "",
                    title="Save Update"
                )
                if file_path:
                    if checker.download_update(download_url, file_path):
                        show_message(self, "Success", 
                                   "Update downloaded! Please install it manually.")
        else:
            show_message(self, "No Updates",
                       f"You are running the latest version ({APP_VERSION})")
    
    def on_closing(self):
        """Handle window closing"""
        self.expansion_engine.stop()
        self.destroy()

