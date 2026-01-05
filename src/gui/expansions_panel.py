"""
Expansions panel for Simple Text Expander
Manages expansions within a selected group
"""
import customtkinter as ctk
from typing import Callable, Optional, List, Dict, Any


class ExpansionsPanel(ctk.CTkFrame):
    """Panel for managing expansions in a group"""
    
    def __init__(self, parent, on_expansion_changed: Optional[Callable] = None):
        """
        Initialize expansions panel
        
        Args:
            parent: Parent widget
            on_expansion_changed: Callback when expansions change
        """
        super().__init__(parent)
        self.on_expansion_changed = on_expansion_changed
        self.current_group_id = None
        self.expansions = []
        self.selected_expansion_id = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create UI widgets"""
        # Title
        self.title_label = ctk.CTkLabel(self, text="Expansions", 
                                        font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(pady=10)
        
        # Buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        self.add_btn = ctk.CTkButton(button_frame, text="Add Expansion",
                                    command=self._add_expansion)
        self.add_btn.pack(side="left", padx=5)
        
        self.edit_btn = ctk.CTkButton(button_frame, text="Edit Expansion",
                                     command=self._edit_expansion)
        self.edit_btn.pack(side="left", padx=5)
        
        self.delete_btn = ctk.CTkButton(button_frame, text="Delete Expansion",
                                       command=self._delete_expansion)
        self.delete_btn.pack(side="left", padx=5)
        
        # Expansions list
        list_label = ctk.CTkLabel(self, text="Expansions in Group:")
        list_label.pack(anchor="w", padx=10, pady=5)
        
        self.expansions_listbox = ctk.CTkScrollableFrame(self, height=400)
        self.expansions_listbox.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.expansion_items = []
    
    def update_group(self, group_id: str, group_name: str, expansions: List[Dict[str, Any]]):
        """
        Update the panel with a group's expansions
        
        Args:
            group_id: ID of the group
            group_name: Name of the group
            expansions: List of expansion dicts
        """
        self.current_group_id = group_id
        self.expansions = expansions
        self.selected_expansion_id = None  # Reset selection when group changes
        
        self.title_label.configure(text=f"Expansions - {group_name}")
        
        # Clear existing items
        for widget in self.expansions_listbox.winfo_children():
            widget.destroy()
        self.expansion_items = []
        
        # Create items for each expansion
        for expansion in expansions:
            self._add_expansion_item(expansion)
    
    def _add_expansion_item(self, expansion: Dict[str, Any]):
        """Add an expansion item to the list"""
        item_frame = ctk.CTkFrame(self.expansions_listbox)
        item_frame.pack(fill="x", padx=5, pady=5)
        
        expansion_id = expansion['id']
        
        # Set initial frame color (unselected)
        item_frame.configure(fg_color=("gray70", "gray30"))
        
        # Bind click to select and double-click to edit
        item_frame.bind("<Button-1>", lambda e, eid=expansion_id: self._select_expansion(eid))
        item_frame.bind("<Double-Button-1>", lambda e, eid=expansion_id: self._on_expansion_double_click(eid))
        
        # Make all child widgets also respond to clicks
        def bind_to_children(widget):
            widget.bind("<Button-1>", lambda e, eid=expansion_id: self._select_expansion(eid))
            widget.bind("<Double-Button-1>", lambda e, eid=expansion_id: self._on_expansion_double_click(eid))
            for child in widget.winfo_children():
                bind_to_children(child)
        
        # Prefix
        prefix_label = ctk.CTkLabel(item_frame, 
                                   text=f"Prefix: {expansion.get('prefix', '')}",
                                   font=ctk.CTkFont(weight="bold"))
        prefix_label.pack(anchor="w", padx=10, pady=2)
        bind_to_children(prefix_label)
        
        # Description
        description = expansion.get('description', '')
        if description:
            desc_label = ctk.CTkLabel(item_frame, text=description,
                                     font=ctk.CTkFont(size=12))
            desc_label.pack(anchor="w", padx=10, pady=2)
            bind_to_children(desc_label)
        
        # Preview text (truncated)
        text = expansion.get('text', '')
        preview = text[:50] + "..." if len(text) > 50 else text
        text_label = ctk.CTkLabel(item_frame, text=f"→ {preview}",
                                 font=ctk.CTkFont(size=11))
        text_label.pack(anchor="w", padx=10, pady=2)
        bind_to_children(text_label)
        
        # Trigger info
        trigger_info = "Immediate" if expansion.get('trigger_immediate', True) else f"Delay: {expansion.get('trigger_delay_ms', 0)}ms"
        trigger_label = ctk.CTkLabel(item_frame, text=trigger_info,
                                    font=ctk.CTkFont(size=10))
        trigger_label.pack(anchor="w", padx=10, pady=2)
        bind_to_children(trigger_label)
        
        self.expansion_items.append((expansion_id, item_frame))
    
    def _add_expansion(self):
        """Show dialog to add expansion"""
        dialog = ExpansionDialog(self, "Add Expansion")
        result = dialog.get_result()
        
        if result:
            return result
        return None
    
    def _select_expansion(self, expansion_id: str):
        """Select an expansion"""
        self.selected_expansion_id = expansion_id
        
        # Update visual selection (highlight selected item)
        for eid, item_frame in self.expansion_items:
            if eid == expansion_id:
                item_frame.configure(fg_color=("gray75", "gray25"))
            else:
                item_frame.configure(fg_color=("gray70", "gray30"))
    
    def _on_expansion_double_click(self, expansion_id: str):
        """Handle double-click on expansion to edit"""
        self._select_expansion(expansion_id)
        # Find the expansion data and trigger edit
        expansion = None
        for exp in self.expansions:
            if exp['id'] == expansion_id:
                expansion = exp
                break
        
        if expansion:
            dialog = ExpansionDialog(self, "Edit Expansion", expansion)
            result = dialog.get_result()
            
            if result:
                return result
        return None
    
    def _edit_expansion(self):
        """Edit selected expansion"""
        if not self.selected_expansion_id:
            return None
        
        # Find the expansion data
        expansion = None
        for exp in self.expansions:
            if exp['id'] == self.selected_expansion_id:
                expansion = exp
                break
        
        if not expansion:
            return None
        
        dialog = ExpansionDialog(self, "Edit Expansion", expansion)
        result = dialog.get_result()
        
        if result:
            return result
        return None
    
    def _delete_expansion(self):
        """Delete selected expansion"""
        # For now, return None (TODO: implement selection)
        # In a full implementation, you'd track selected expansion and return its ID
        return None
    
    def clear(self):
        """Clear the panel"""
        self.current_group_id = None
        self.expansions = []
        self.selected_expansion_id = None
        self.title_label.configure(text="Expansions")
        
        for widget in self.expansions_listbox.winfo_children():
            widget.destroy()
        self.expansion_items = []
    
    def get_selected_expansion_id(self) -> Optional[str]:
        """Get currently selected expansion ID"""
        return self.selected_expansion_id


class ExpansionDialog(ctk.CTkToplevel):
    """Dialog for adding/editing expansions"""
    
    def __init__(self, parent, title: str, expansion: Optional[Dict[str, Any]] = None):
        """
        Initialize expansion dialog
        
        Args:
            parent: Parent widget
            title: Dialog title
            expansion: Existing expansion data (for editing) or None (for adding)
        """
        super().__init__(parent)
        self.title(title)
        self.geometry("600x500")
        self.result = None
        
        # Make dialog modal and bring to front
        self.transient(parent)
        self.grab_set()
        self.lift()
        self.focus()
        
        if expansion:
            self.expansion = expansion
        else:
            self.expansion = {
                'prefix': '',
                'text': '',
                'description': '',
                'trigger_immediate': True,
                'trigger_delay_ms': 0
            }
        
        self._create_widgets()
        self._load_data()
    
    def _create_widgets(self):
        """Create dialog widgets"""
        # Prefix
        prefix_label = ctk.CTkLabel(self, text="Prefix (e.g., /info, .info, $info):")
        prefix_label.pack(anchor="w", padx=20, pady=(20, 5))
        
        self.prefix_entry = ctk.CTkEntry(self, width=400)
        self.prefix_entry.pack(fill="x", padx=20, pady=5)
        
        # Expanded Text
        text_label = ctk.CTkLabel(self, text="Expanded Text:")
        text_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.text_textbox = ctk.CTkTextbox(self, height=150)
        self.text_textbox.pack(fill="both", expand=True, padx=20, pady=5)
        
        # Description
        desc_label = ctk.CTkLabel(self, text="Description (optional):")
        desc_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        self.desc_entry = ctk.CTkEntry(self, width=400)
        self.desc_entry.pack(fill="x", padx=20, pady=5)
        
        # Trigger options
        trigger_frame = ctk.CTkFrame(self)
        trigger_frame.pack(fill="x", padx=20, pady=10)
        
        self.trigger_immediate_var = ctk.BooleanVar(value=True)
        immediate_radio = ctk.CTkRadioButton(trigger_frame, text="Trigger Immediately",
                                            variable=self.trigger_immediate_var,
                                            value=True,
                                            command=self._on_trigger_change)
        immediate_radio.pack(side="left", padx=10, pady=10)
        
        delay_radio = ctk.CTkRadioButton(trigger_frame, text="Trigger After Delay",
                                        variable=self.trigger_immediate_var,
                                        value=False,
                                        command=self._on_trigger_change)
        delay_radio.pack(side="left", padx=10, pady=10)
        
        self.delay_entry = ctk.CTkEntry(trigger_frame, width=100, placeholder_text="ms")
        self.delay_entry.pack(side="left", padx=10, pady=10)
        self.delay_entry.configure(state="disabled")
        
        # Buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        save_btn = ctk.CTkButton(button_frame, text="Save",
                                command=self._save)
        save_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(button_frame, text="Cancel",
                                 command=self._cancel)
        cancel_btn.pack(side="left", padx=10)
    
    def _load_data(self):
        """Load expansion data into widgets"""
        self.prefix_entry.insert(0, self.expansion.get('prefix', ''))
        self.text_textbox.insert("1.0", self.expansion.get('text', ''))
        self.desc_entry.insert(0, self.expansion.get('description', ''))
        
        immediate = self.expansion.get('trigger_immediate', True)
        self.trigger_immediate_var.set(immediate)
        
        if not immediate:
            delay = self.expansion.get('trigger_delay_ms', 0)
            self.delay_entry.insert(0, str(delay))
            self.delay_entry.configure(state="normal")
        else:
            self.delay_entry.configure(state="disabled")
    
    def _on_trigger_change(self):
        """Handle trigger option change"""
        if self.trigger_immediate_var.get():
            self.delay_entry.configure(state="disabled")
            self.delay_entry.delete(0, "end")
        else:
            self.delay_entry.configure(state="normal")
    
    def _save(self):
        """Save expansion data"""
        prefix = self.prefix_entry.get().strip()
        text = self.text_textbox.get("1.0", "end-1c").strip()
        description = self.desc_entry.get().strip()
        immediate = self.trigger_immediate_var.get()
        
        delay_ms = 0
        if not immediate:
            try:
                delay_ms = int(self.delay_entry.get() or "0")
            except ValueError:
                delay_ms = 0
        
        if not prefix or not text:
            # Show error
            return
        
        self.result = {
            'prefix': prefix,
            'text': text,
            'description': description,
            'trigger_immediate': immediate,
            'trigger_delay_ms': delay_ms
        }
        self.destroy()
    
    def _cancel(self):
        """Cancel dialog"""
        self.destroy()
    
    def get_result(self):
        """Get dialog result"""
        self.wait_window()
        return self.result

