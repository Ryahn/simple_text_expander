"""
Input dialog utility for Simple Text Expander
"""
import customtkinter as ctk


class InputDialog(ctk.CTkToplevel):
    """Simple input dialog"""
    
    def __init__(self, parent, title: str, prompt: str, initial_value: str = ""):
        """
        Initialize input dialog
        
        Args:
            parent: Parent widget
            title: Dialog title
            prompt: Prompt text
            initial_value: Initial input value
        """
        super().__init__(parent)
        self.title(title)
        self.geometry("400x150")
        self.result = None
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Prompt label
        label = ctk.CTkLabel(self, text=prompt, font=ctk.CTkFont(size=12))
        label.pack(pady=20, padx=20)
        
        # Input entry
        self.entry = ctk.CTkEntry(self, width=350)
        self.entry.pack(pady=10, padx=20)
        if initial_value:
            self.entry.insert(0, initial_value)
        self.entry.focus()
        
        # Buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=10)
        
        ok_btn = ctk.CTkButton(button_frame, text="OK", command=self._ok_clicked, width=100)
        ok_btn.pack(side="left", padx=5)
        
        cancel_btn = ctk.CTkButton(button_frame, text="Cancel", command=self._cancel_clicked, width=100)
        cancel_btn.pack(side="left", padx=5)
        
        # Bind Enter key
        self.entry.bind("<Return>", lambda e: self._ok_clicked())
    
    def _ok_clicked(self):
        """Handle OK button"""
        self.result = self.entry.get()
        self.destroy()
    
    def _cancel_clicked(self):
        """Handle Cancel button"""
        self.result = None
        self.destroy()
    
    def get_input(self):
        """Show dialog and return input"""
        self.wait_window()
        return self.result

