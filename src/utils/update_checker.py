"""
Update checker for Simple Text Expander
Checks GitHub releases for updates
"""
import re
import sys
import requests
from typing import Optional, Tuple
from packaging import version

from src.config import GITHUB_REPO, APP_VERSION


class UpdateChecker:
    """Checks for application updates from GitHub"""
    
    def __init__(self, repo: str = GITHUB_REPO):
        """
        Initialize update checker
        
        Args:
            repo: GitHub repository in format 'owner/repo'
        """
        self.repo = repo
        self.api_url = f"https://api.github.com/repos/{repo}/releases/latest"
    
    def get_latest_version(self) -> Optional[Tuple[str, str, str]]:
        """
        Get the latest version from GitHub releases
        
        Returns:
            Tuple of (version_string, download_url, release_notes) or None if error
        """
        try:
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            latest_version = data.get('tag_name', '')
            
            # Remove 'v' prefix if present
            if latest_version.startswith('v'):
                latest_version = latest_version[1:]
            
            # Get download URL (prefer platform-specific)
            download_url = None
            assets = data.get('assets', [])
            
            if sys.platform == 'win32':
                # Look for Windows installer or portable
                for asset in assets:
                    name = asset.get('name', '').lower()
                    if 'setup.exe' in name or 'installer.exe' in name:
                        download_url = asset.get('browser_download_url')
                        break
                    elif 'portable.exe' in name and not download_url:
                        download_url = asset.get('browser_download_url')
            elif sys.platform == 'darwin':
                # Look for macOS DMG or ZIP
                for asset in assets:
                    name = asset.get('name', '').lower()
                    if '.dmg' in name:
                        download_url = asset.get('browser_download_url')
                        break
                    elif '.zip' in name and not download_url:
                        download_url = asset.get('browser_download_url')
            
            # Fallback to first asset if no platform-specific found
            if not download_url and assets:
                download_url = assets[0].get('browser_download_url')
            
            release_notes = data.get('body', '')
            
            return (latest_version, download_url, release_notes)
            
        except requests.RequestException as e:
            print(f"Error checking for updates: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error checking for updates: {e}")
            return None
    
    def is_update_available(self) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
        """
        Check if an update is available
        
        Returns:
            Tuple of (is_available, latest_version, download_url, release_notes)
        """
        result = self.get_latest_version()
        if not result:
            return (False, None, None, None)
        
        latest_version, download_url, release_notes = result
        
        try:
            current = version.parse(APP_VERSION)
            latest = version.parse(latest_version)
            is_available = latest > current
            return (is_available, latest_version, download_url, release_notes)
        except Exception as e:
            print(f"Error comparing versions: {e}")
            return (False, None, None, None)
    
    def download_update(self, download_url: str, save_path: str) -> bool:
        """
        Download update file
        
        Args:
            download_url: URL to download from
            save_path: Path to save the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return True
        except Exception as e:
            print(f"Error downloading update: {e}")
            return False

