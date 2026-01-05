"""
Main entry point for Simple Text Expander
"""
import sys
import os
from pathlib import Path
import customtkinter as ctk

# Add project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.gui.main_window import MainWindow
from src.config import APP_NAME


def main():
    """Main application entry point"""
    # Set appearance mode
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Create and run main window
    app = MainWindow()
    
    # Handle window closing
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Run main loop
    app.mainloop()


if __name__ == "__main__":
    main()

