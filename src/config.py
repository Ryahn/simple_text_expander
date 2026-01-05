"""
Configuration constants for Simple Text Expander
"""
import os
from pathlib import Path

# Application info
APP_NAME = "Simple Text Expander"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Simple Text Expander"

# Data storage location
if os.name == 'nt':  # Windows
    DOCUMENTS_DIR = Path(os.path.expanduser("~/Documents"))
else:  # macOS/Linux
    DOCUMENTS_DIR = Path(os.path.expanduser("~/Documents"))

DATA_DIR = DOCUMENTS_DIR / "SimpleTextExpander"
DATA_FILE = DATA_DIR / "data.json"

# GitHub repository for updates
GITHUB_REPO = "Ryahn/simple_text_expander"

# Default data structure
DEFAULT_DATA = {
    "version": APP_VERSION,
    "settings": {
        "whitelist_enabled": False,
        "whitelist_apps": []
    },
    "groups": []
}

