"""
Groups panel for Simple Text Expander
Manages expansion groups
"""
import customtkinter as ctk
from typing import Callable, Optional

from src.utils.input_dialog import InputDialog


class GroupsPanel(ctk.CTkFrame):
    """Panel for managing expansion groups"""
    
    def __init__(self, parent, on_group_selected: Optional[Callable[[str], None]] = None,
                 on_group_edit: Optional[Callable[[str], None]] = None):
        """
        Initialize groups panel
        
        Args:
            parent: Parent widget
            on_group_selected: Callback when a group is selected (group_id)
            on_group_edit: Callback when a group is double-clicked to edit (group_id)
        """
        super().__init__(parent)
        self.on_group_selected = on_group_selected
        self.on_group_edit = on_group_edit
        self.selected_group_id = None
        self.groups = []
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create UI widgets"""
        # Title
        title = ctk.CTkLabel(self, text="Groups", 
                            font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=10)
        
        # Buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        self.add_btn = ctk.CTkButton(button_frame, text="Add Group",
                                     command=self._add_group)
        self.add_btn.pack(side="left", padx=5)
        
        self.edit_btn = ctk.CTkButton(button_frame, text="Edit Group",
                                      command=self._edit_group)
        self.edit_btn.pack(side="left", padx=5)
        
        self.delete_btn = ctk.CTkButton(button_frame, text="Delete Group",
                                        command=self._delete_group)
        self.delete_btn.pack(side="left", padx=5)
        
        # Groups list
        list_label = ctk.CTkLabel(self, text="Expansion Groups:")
        list_label.pack(anchor="w", padx=10, pady=5)
        
        self.groups_listbox = ctk.CTkScrollableFrame(self, height=400)
        self.groups_listbox.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.group_buttons = []
    
    def update_groups(self, groups: list):
        """
        Update the groups list
        
        Args:
            groups: List of group dicts with 'id' and 'name'
        """
        self.groups = groups
        
        # Clear existing buttons
        for widget in self.groups_listbox.winfo_children():
            widget.destroy()
        self.group_buttons = []
        
        # Create buttons for each group
        for group in groups:
            group_id = group['id']
            group_name = group['name']
            expansion_count = len(group.get('expansions', []))
            
            btn = ctk.CTkButton(
                self.groups_listbox,
                text=f"{group_name} ({expansion_count} expansions)",
                command=lambda gid=group_id: self._select_group(gid),
                anchor="w",
                height=40
            )
            # Bind double-click to edit
            btn.bind("<Double-Button-1>", lambda e, gid=group_id: self._on_group_double_click(gid))
            btn.pack(fill="x", padx=5, pady=2)
            self.group_buttons.append((group_id, btn))
    
    def _select_group(self, group_id: str):
        """Select a group"""
        self.selected_group_id = group_id
        
        # Update button appearance
        for gid, btn in self.group_buttons:
            if gid == group_id:
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color=("gray70", "gray30"))
        
        if self.on_group_selected:
            self.on_group_selected(group_id)
    
    def _on_group_double_click(self, group_id: str):
        """Handle double-click on group to edit"""
        self._select_group(group_id)
        # Trigger edit callback
        if self.on_group_edit:
            self.on_group_edit(group_id)
    
    def _add_group(self):
        """Add a new group"""
        dialog = InputDialog(self, "Add Group", "Enter group name:")
        group_name = dialog.get_input()
        
        if group_name:
            return group_name
        return None
    
    def _edit_group(self):
        """Edit selected group"""
        if not self.selected_group_id:
            return None
        
        # Find group name
        group_name = ""
        for group in self.groups:
            if group['id'] == self.selected_group_id:
                group_name = group['name']
                break
        
        dialog = InputDialog(self, "Edit Group", "Enter new group name:", initial_value=group_name)
        new_name = dialog.get_input()
        
        if new_name:
            return (self.selected_group_id, new_name)
        return None
    
    def _delete_group(self):
        """Delete selected group"""
        if not self.selected_group_id:
            return None
        return self.selected_group_id
    
    def get_selected_group_id(self) -> Optional[str]:
        """Get currently selected group ID"""
        return self.selected_group_id

