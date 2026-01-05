"""
Expansion engine for Simple Text Expander
Coordinates keyboard monitoring, app monitoring, and expansion execution
"""
import time
import threading
from typing import Callable, Optional
from pynput.keyboard import Key, Controller as KeyboardController

from src.core.keyboard_monitor import KeyboardMonitor
from src.core.app_monitor import AppMonitor
from src.core.data_manager import DataManager
from src.utils.clipboard import copy_to_clipboard


class ExpansionEngine:
    """Main engine that coordinates expansion functionality"""
    
    def __init__(self, data_manager: DataManager):
        """
        Initialize expansion engine
        
        Args:
            data_manager: DataManager instance
        """
        self.data_manager = data_manager
        self.app_monitor = AppMonitor()
        self.keyboard_monitor = KeyboardMonitor(self._on_expansion_detected)
        self.keyboard_controller = KeyboardController()
        self.is_running = False
        self.on_status_changed: Optional[Callable[[bool], None]] = None
        
        # Update expansions when data changes
        self._update_expansions()
    
    def _update_expansions(self):
        """Update keyboard monitor with current expansions"""
        expansions = self.data_manager.get_all_expansions()
        self.keyboard_monitor.update_expansions(expansions)
    
    def _on_expansion_detected(self, prefix: str, expanded_text: str):
        """
        Called when a prefix is detected and should be expanded
        
        Args:
            prefix: The prefix that was detected
            expanded_text: The text to expand to
        """
        # Check whitelist
        settings = self.data_manager.get_settings()
        whitelist_enabled = settings.get('whitelist_enabled', False)
        whitelist_apps = settings.get('whitelist_apps', [])
        
        if not self.app_monitor.is_app_whitelisted(whitelist_apps, whitelist_enabled):
            return
        
        # Perform expansion
        self._perform_expansion(prefix, expanded_text)
    
    def _perform_expansion(self, prefix: str, expanded_text: str):
        """
        Perform the actual text expansion
        
        Args:
            prefix: The prefix to remove
            expanded_text: The text to insert
        """
        try:
            # Delete the prefix (backspace)
            for _ in range(len(prefix)):
                self.keyboard_controller.press(Key.backspace)
                self.keyboard_controller.release(Key.backspace)
                time.sleep(0.01)  # Small delay between backspaces
            
            # Copy expanded text to clipboard
            if copy_to_clipboard(expanded_text):
                # Paste using Ctrl+V
                time.sleep(0.05)  # Small delay to ensure clipboard is ready
                self.keyboard_controller.press(Key.ctrl)
                self.keyboard_controller.press('v')
                self.keyboard_controller.release('v')
                self.keyboard_controller.release(Key.ctrl)
        except Exception as e:
            print(f"Error performing expansion: {e}")
    
    def start(self):
        """Start the expansion engine"""
        if self.is_running:
            return
        
        self.is_running = True
        self._update_expansions()
        self.keyboard_monitor.start()
        
        if self.on_status_changed:
            self.on_status_changed(True)
    
    def stop(self):
        """Stop the expansion engine"""
        if not self.is_running:
            return
        
        self.is_running = False
        self.keyboard_monitor.stop()
        
        if self.on_status_changed:
            self.on_status_changed(False)
    
    def refresh_expansions(self):
        """Refresh expansions from data manager"""
        self._update_expansions()
    
    def get_status(self) -> bool:
        """Get current running status"""
        return self.is_running

