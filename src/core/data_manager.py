"""
Data management for Simple Text Expander
Handles loading, saving, and import/export of expansion data
"""
import json
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional

from src.config import DATA_DIR, DATA_FILE, DEFAULT_DATA


class DataManager:
    """Manages expansion data storage and retrieval"""
    
    def __init__(self):
        self.data: Dict[str, Any] = DEFAULT_DATA.copy()
        self._ensure_data_dir()
        self.load()
    
    def _ensure_data_dir(self):
        """Ensure the data directory exists"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    def load(self) -> Dict[str, Any]:
        """Load data from JSON file"""
        if DATA_FILE.exists():
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                # Ensure all required keys exist
                if "settings" not in self.data:
                    self.data["settings"] = DEFAULT_DATA["settings"]
                if "groups" not in self.data:
                    self.data["groups"] = []
                if "version" not in self.data:
                    self.data["version"] = DEFAULT_DATA["version"]
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading data: {e}")
                self.data = DEFAULT_DATA.copy()
                self.save()
        else:
            # Create default data file
            self.data = DEFAULT_DATA.copy()
            self.save()
        return self.data
    
    def save(self) -> bool:
        """Save data to JSON file"""
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving data: {e}")
            return False
    
    def get_settings(self) -> Dict[str, Any]:
        """Get current settings"""
        return self.data.get("settings", {})
    
    def update_settings(self, settings: Dict[str, Any]) -> bool:
        """Update settings"""
        self.data["settings"].update(settings)
        return self.save()
    
    def get_groups(self) -> List[Dict[str, Any]]:
        """Get all groups"""
        return self.data.get("groups", [])
    
    def add_group(self, name: str) -> str:
        """Add a new group and return its ID"""
        group_id = str(uuid.uuid4())
        group = {
            "id": group_id,
            "name": name,
            "expansions": []
        }
        self.data["groups"].append(group)
        self.save()
        return group_id
    
    def update_group(self, group_id: str, name: str) -> bool:
        """Update a group's name"""
        for group in self.data["groups"]:
            if group["id"] == group_id:
                group["name"] = name
                return self.save()
        return False
    
    def delete_group(self, group_id: str) -> bool:
        """Delete a group"""
        self.data["groups"] = [
            g for g in self.data["groups"] if g["id"] != group_id
        ]
        return self.save()
    
    def get_group(self, group_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific group by ID"""
        for group in self.data["groups"]:
            if group["id"] == group_id:
                return group
        return None
    
    def add_expansion(self, group_id: str, prefix: str, text: str, 
                     description: str = "", trigger_immediate: bool = True,
                     trigger_delay_ms: int = 0) -> str:
        """Add an expansion to a group and return its ID"""
        expansion_id = str(uuid.uuid4())
        expansion = {
            "id": expansion_id,
            "prefix": prefix,
            "text": text,
            "description": description,
            "trigger_immediate": trigger_immediate,
            "trigger_delay_ms": trigger_delay_ms
        }
        
        for group in self.data["groups"]:
            if group["id"] == group_id:
                group["expansions"].append(expansion)
                self.save()
                return expansion_id
        return ""
    
    def update_expansion(self, group_id: str, expansion_id: str, 
                        prefix: str, text: str, description: str = "",
                        trigger_immediate: bool = True,
                        trigger_delay_ms: int = 0) -> bool:
        """Update an expansion"""
        for group in self.data["groups"]:
            if group["id"] == group_id:
                for expansion in group["expansions"]:
                    if expansion["id"] == expansion_id:
                        expansion["prefix"] = prefix
                        expansion["text"] = text
                        expansion["description"] = description
                        expansion["trigger_immediate"] = trigger_immediate
                        expansion["trigger_delay_ms"] = trigger_delay_ms
                        return self.save()
        return False
    
    def delete_expansion(self, group_id: str, expansion_id: str) -> bool:
        """Delete an expansion"""
        for group in self.data["groups"]:
            if group["id"] == group_id:
                group["expansions"] = [
                    e for e in group["expansions"] if e["id"] != expansion_id
                ]
                return self.save()
        return False
    
    def get_all_expansions(self) -> List[Dict[str, Any]]:
        """Get all expansions from all groups"""
        expansions = []
        for group in self.data["groups"]:
            for expansion in group["expansions"]:
                expansions.append({
                    **expansion,
                    "group_id": group["id"],
                    "group_name": group["name"]
                })
        return expansions
    
    def export_json(self, file_path: Path) -> bool:
        """Export all data to a JSON file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error exporting data: {e}")
            return False
    
    def import_json(self, file_path: Path, merge: bool = False) -> bool:
        """Import data from a JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)
            
            if merge:
                # Merge groups (skip duplicates by name)
                existing_names = {g["name"] for g in self.data["groups"]}
                for group in imported_data.get("groups", []):
                    if group["name"] not in existing_names:
                        # Generate new IDs to avoid conflicts
                        old_group_id = group["id"]
                        group["id"] = str(uuid.uuid4())
                        for expansion in group["expansions"]:
                            expansion["id"] = str(uuid.uuid4())
                        self.data["groups"].append(group)
            else:
                # Replace all data
                self.data = imported_data
                # Ensure required keys
                if "settings" not in self.data:
                    self.data["settings"] = DEFAULT_DATA["settings"]
                if "groups" not in self.data:
                    self.data["groups"] = []
            
            return self.save()
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error importing data: {e}")
            return False
    
    def is_prefix_unique(self, prefix: str, exclude_group_id: Optional[str] = None,
                        exclude_expansion_id: Optional[str] = None) -> bool:
        """Check if a prefix is unique across all expansions"""
        for group in self.data["groups"]:
            if exclude_group_id and group["id"] == exclude_group_id:
                continue
            for expansion in group["expansions"]:
                if expansion["prefix"] == prefix:
                    if exclude_expansion_id and expansion["id"] == exclude_expansion_id:
                        continue
                    return False
        return True

