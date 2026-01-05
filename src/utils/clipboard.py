"""
Clipboard utilities for Simple Text Expander
"""
import sys

if sys.platform == 'win32':
    try:
        import win32clipboard
        CLIPBOARD_AVAILABLE = True
    except ImportError:
        CLIPBOARD_AVAILABLE = False
        try:
            import pyperclip
            USE_PYPERCLIP = True
        except ImportError:
            USE_PYPERCLIP = False
else:
    try:
        import pyperclip
        USE_PYPERCLIP = True
    except ImportError:
        USE_PYPERCLIP = False
    CLIPBOARD_AVAILABLE = False


def copy_to_clipboard(text: str) -> bool:
    """
    Copy text to clipboard
    
    Args:
        text: Text to copy
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if sys.platform == 'win32' and CLIPBOARD_AVAILABLE:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text)
            win32clipboard.CloseClipboard()
            return True
        elif USE_PYPERCLIP:
            import pyperclip
            pyperclip.copy(text)
            return True
        else:
            print("No clipboard support available")
            return False
    except Exception as e:
        print(f"Error copying to clipboard: {e}")
        return False


def get_clipboard_text() -> str:
    """
    Get text from clipboard
    
    Returns:
        Clipboard text, or empty string if error
    """
    try:
        if sys.platform == 'win32' and CLIPBOARD_AVAILABLE:
            win32clipboard.OpenClipboard()
            try:
                text = win32clipboard.GetClipboardData()
            except TypeError:
                text = ""
            win32clipboard.CloseClipboard()
            return text
        elif USE_PYPERCLIP:
            import pyperclip
            return pyperclip.paste()
        else:
            return ""
    except Exception as e:
        print(f"Error getting clipboard text: {e}")
        return ""

