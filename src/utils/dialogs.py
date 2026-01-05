"""
Dialog utilities for Simple Text Expander
"""
import customtkinter as ctk


class SimpleDialog(ctk.CTkToplevel):
    """Simple dialog for messages"""
    
    def __init__(self, parent, title: str, message: str, buttons: list = None):
        """
        Initialize dialog
        
        Args:
            parent: Parent widget
            title: Dialog title
            message: Message text
            buttons: List of button texts (default: ["OK"])
        """
        super().__init__(parent)
        self.title(title)
        self.geometry("400x200")
        self.result = None
        
        if buttons is None:
            buttons = ["OK"]
        
        self.buttons = buttons
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Message label
        msg_label = ctk.CTkLabel(self, text=message, 
                                font=ctk.CTkFont(size=12),
                                wraplength=350)
        msg_label.pack(pady=30, padx=20)
        
        # Buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=20)
        
        for i, btn_text in enumerate(buttons):
            btn = ctk.CTkButton(button_frame, text=btn_text,
                               command=lambda b=btn_text: self._button_clicked(b),
                               width=100)
            btn.pack(side="left", padx=5)
    
    def _button_clicked(self, button_text: str):
        """Handle button click"""
        self.result = button_text
        self.destroy()
    
    def show(self):
        """Show dialog and return result"""
        self.wait_window()
        return self.result


def show_message(parent, title: str, message: str):
    """Show a simple message dialog"""
    dialog = SimpleDialog(parent, title, message)
    dialog.show()


def show_question(parent, title: str, message: str, buttons: list = None) -> str:
    """
    Show a question dialog
    
    Args:
        parent: Parent widget
        title: Dialog title
        message: Message text
        buttons: List of button texts (default: ["Yes", "No"])
        
    Returns:
        Selected button text
    """
    if buttons is None:
        buttons = ["Yes", "No"]
    
    dialog = SimpleDialog(parent, title, message, buttons)
    return dialog.show()

