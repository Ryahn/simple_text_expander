"""
Keyboard monitoring for Simple Text Expander
Monitors global keyboard input to detect prefix triggers
"""
import time
import threading
from typing import Callable, Optional
from pynput import keyboard


class KeyboardMonitor:
    """Monitors keyboard input for prefix detection"""
    
    def __init__(self, on_expansion_triggered: Callable[[str, str], None]):
        """
        Initialize keyboard monitor
        
        Args:
            on_expansion_triggered: Callback function(prefix, expanded_text) when expansion should occur
        """
        self.on_expansion_triggered = on_expansion_triggered
        self.listener: Optional[keyboard.Listener] = None
        self.is_monitoring = False
        self.buffer = ""
        self.buffer_lock = threading.Lock()
        self.max_buffer_size = 100  # Maximum characters to keep in buffer
        self.expansions_map = {}  # prefix -> expansion data
        self._update_lock = threading.Lock()
    
    def update_expansions(self, expansions: list):
        """
        Update the expansions map
        
        Args:
            expansions: List of expansion dicts with 'prefix', 'text', 'trigger_immediate', 'trigger_delay_ms'
        """
        with self._update_lock:
            self.expansions_map = {}
            for exp in expansions:
                prefix = exp.get('prefix', '')
                if prefix:
                    self.expansions_map[prefix] = exp
    
    def _on_press(self, key):
        """Handle key press events"""
        if not self.is_monitoring:
            return
        
        try:
            # Handle special keys
            if key == keyboard.Key.backspace:
                with self.buffer_lock:
                    if self.buffer:
                        self.buffer = self.buffer[:-1]
                return
            
            if key == keyboard.Key.space:
                char = ' '
            elif key == keyboard.Key.enter:
                char = '\n'
            elif hasattr(key, 'char') and key.char:
                char = key.char
            else:
                # Special key, clear buffer
                with self.buffer_lock:
                    self.buffer = ""
                return
            
            # Add character to buffer
            with self.buffer_lock:
                self.buffer += char
                # Limit buffer size
                if len(self.buffer) > self.max_buffer_size:
                    self.buffer = self.buffer[-self.max_buffer_size:]
            
            # Check for prefix matches
            self._check_prefixes()
            
        except Exception as e:
            print(f"Error in keyboard monitor: {e}")
    
    def _check_prefixes(self):
        """Check if buffer ends with any known prefix"""
        with self.buffer_lock:
            buffer = self.buffer
        
        with self._update_lock:
            # Check all prefixes (longest first to match most specific)
            sorted_prefixes = sorted(self.expansions_map.keys(), key=len, reverse=True)
            
            for prefix in sorted_prefixes:
                if buffer.endswith(prefix):
                    expansion = self.expansions_map[prefix]
                    
                    # Determine delay
                    if expansion.get('trigger_immediate', True):
                        delay_ms = 0
                    else:
                        delay_ms = expansion.get('trigger_delay_ms', 0)
                    
                    # Trigger expansion with delay
                    if delay_ms > 0:
                        threading.Timer(delay_ms / 1000.0, 
                                       lambda: self.on_expansion_triggered(prefix, expansion['text'])).start()
                    else:
                        self.on_expansion_triggered(prefix, expansion['text'])
                    
                    # Clear buffer after match
                    with self.buffer_lock:
                        self.buffer = ""
                    break
    
    def start(self):
        """Start monitoring keyboard"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.listener = keyboard.Listener(on_press=self._on_press)
        self.listener.start()
    
    def stop(self):
        """Stop monitoring keyboard"""
        self.is_monitoring = False
        if self.listener:
            self.listener.stop()
            self.listener = None
        with self.buffer_lock:
            self.buffer = ""
    
    def clear_buffer(self):
        """Clear the keyboard buffer"""
        with self.buffer_lock:
            self.buffer = ""

