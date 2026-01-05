"""
Application monitoring for Simple Text Expander
Detects active application for whitelist checking
"""
import sys
import platform

if sys.platform == 'win32':
    try:
        import win32gui
        import win32process
        import psutil
        WINDOWS_AVAILABLE = True
    except ImportError:
        WINDOWS_AVAILABLE = False
elif sys.platform == 'darwin':
    try:
        from AppKit import NSWorkspace
        MACOS_AVAILABLE = True
    except ImportError:
        MACOS_AVAILABLE = False
else:
    WINDOWS_AVAILABLE = False
    MACOS_AVAILABLE = False


class AppMonitor:
    """Monitors the active application"""
    
    def __init__(self):
        self.platform = platform.system()
    
    def get_active_app_info(self) -> dict:
        """
        Get information about the currently active application
        
        Returns:
            dict with keys: 'process_name', 'window_title'
        """
        if self.platform == 'Windows' and WINDOWS_AVAILABLE:
            return self._get_windows_app_info()
        elif self.platform == 'Darwin' and MACOS_AVAILABLE:
            return self._get_macos_app_info()
        else:
            return {'process_name': 'unknown', 'window_title': 'unknown'}
    
    def _get_windows_app_info(self) -> dict:
        """Get active app info on Windows"""
        try:
            # Get active window
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd)
            
            # Get process name
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                process = psutil.Process(pid)
                process_name = process.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                process_name = "unknown"
            
            return {
                'process_name': process_name.lower() if process_name else 'unknown',
                'window_title': window_title
            }
        except Exception as e:
            print(f"Error getting Windows app info: {e}")
            return {'process_name': 'unknown', 'window_title': 'unknown'}
    
    def _get_macos_app_info(self) -> dict:
        """Get active app info on macOS"""
        try:
            workspace = NSWorkspace.sharedWorkspace()
            active_app = workspace.activeApplication()
            
            process_name = active_app.get('NSApplicationName', 'unknown')
            window_title = active_app.get('NSApplicationPath', 'unknown')
            
            return {
                'process_name': process_name.lower() if process_name else 'unknown',
                'window_title': window_title
            }
        except Exception as e:
            print(f"Error getting macOS app info: {e}")
            return {'process_name': 'unknown', 'window_title': 'unknown'}
    
    def is_app_whitelisted(self, whitelist_apps: list, 
                          whitelist_enabled: bool) -> bool:
        """
        Check if the current app should allow expansion
        
        Args:
            whitelist_apps: List of whitelist entries (dicts with 'process_name' and/or 'window_title')
            whitelist_enabled: Whether whitelist is enabled
            
        Returns:
            True if expansion should be allowed, False otherwise
        """
        # If whitelist is disabled or empty, allow globally
        if not whitelist_enabled or not whitelist_apps:
            return True
        
        app_info = self.get_active_app_info()
        
        # Check each whitelist entry
        for entry in whitelist_apps:
            match = True
            
            # Check process name if specified
            if 'process_name' in entry and entry['process_name']:
                entry_process = entry['process_name'].lower()
                app_process = app_info['process_name']
                if entry_process not in app_process and app_process not in entry_process:
                    match = False
            
            # Check window title if specified
            if 'window_title' in entry and entry['window_title']:
                entry_title = entry['window_title'].lower()
                app_title = app_info['window_title'].lower()
                if entry_title not in app_title:
                    match = False
            
            # If this entry matches, allow expansion
            if match:
                return True
        
        # No match found
        return False
    
    def get_running_apps(self) -> list:
        """
        Get list of currently running applications
        
        Returns:
            List of dicts with 'process_name' and 'window_title'
        """
        apps = []
        
        if self.platform == 'Windows' and WINDOWS_AVAILABLE:
            apps = self._get_windows_running_apps()
        elif self.platform == 'Darwin' and MACOS_AVAILABLE:
            apps = self._get_macos_running_apps()
        
        # Remove duplicates
        seen = set()
        unique_apps = []
        for app in apps:
            key = (app['process_name'], app['window_title'])
            if key not in seen:
                seen.add(key)
                unique_apps.append(app)
        
        return unique_apps
    
    def _get_windows_running_apps(self) -> list:
        """Get running apps on Windows"""
        apps = []
        try:
            def enum_windows_callback(hwnd, apps_list):
                if win32gui.IsWindowVisible(hwnd):
                    window_title = win32gui.GetWindowText(hwnd)
                    if window_title:
                        try:
                            _, pid = win32process.GetWindowThreadProcessId(hwnd)
                            process = psutil.Process(pid)
                            process_name = process.name()
                            apps_list.append({
                                'process_name': process_name,
                                'window_title': window_title
                            })
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                return True
            
            win32gui.EnumWindows(enum_windows_callback, apps)
        except Exception as e:
            print(f"Error getting Windows running apps: {e}")
        
        return apps
    
    def _get_macos_running_apps(self) -> list:
        """Get running apps on macOS"""
        apps = []
        try:
            workspace = NSWorkspace.sharedWorkspace()
            running_apps = workspace.runningApplications()
            
            for app in running_apps:
                process_name = app.localizedName() or 'unknown'
                apps.append({
                    'process_name': process_name,
                    'window_title': process_name  # macOS doesn't easily provide window titles
                })
        except Exception as e:
            print(f"Error getting macOS running apps: {e}")
        
        return apps

