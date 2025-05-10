import json
import os
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

class Zone:
    """Represents a physical zone/room/area where bells can be played"""
    
    def __init__(self, name, id=None, description="", enabled=True, volume_modifier=100, 
                 bells_allowed=None, special_rules=None, color="#00a0ff"):
        self.name = name
        self.id = id or f"zone_{name.lower().replace(' ', '_')}"
        self.description = description
        self.enabled = enabled
        self.volume_modifier = volume_modifier  # Percentage modifier
        self.bells_allowed = bells_allowed or []  # Empty list means all bells
        self.special_rules = special_rules or {}
        self.color = color
        
    def to_dict(self):
        """Convert zone to dictionary for JSON storage"""
        return {
            "name": self.name,
            "id": self.id,
            "description": self.description,
            "enabled": self.enabled,
            "volume_modifier": self.volume_modifier,
            "bells_allowed": self.bells_allowed,
            "special_rules": self.special_rules,
            "color": self.color
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a Zone object from dictionary data"""
        return cls(
            name=data["name"],
            id=data.get("id"),
            description=data.get("description", ""),
            enabled=data.get("enabled", True),
            volume_modifier=data.get("volume_modifier", 100),
            bells_allowed=data.get("bells_allowed", []),
            special_rules=data.get("special_rules", {}),
            color=data.get("color", "#00a0ff")
        )
        
    def can_play_bell(self, bell):
        """Check if a bell is allowed to play in this zone"""
        # If no bells are specified, all bells are allowed
        if not self.bells_allowed:
            return True
            
        # Check if bell is in allowed list
        return bell.id in self.bells_allowed or bell.name in self.bells_allowed


class MultiZoneController(QObject):
    """Manages multiple zones for targeted bell playback"""
    
    # Signals
    zone_added = pyqtSignal(Zone)
    zone_updated = pyqtSignal(Zone)
    zone_removed = pyqtSignal(str)  # Zone ID
    zone_status_changed = pyqtSignal(str, bool)  # Zone ID, Enabled
    
    def __init__(self, zones_file="data/zones.json"):
        super().__init__()
        self.zones_file = zones_file
        self.zones = {}
        
        # Load zones from file
        self.load_zones()
        
        # If no zones, create default
        if not self.zones:
            self.create_default_zones()
            
    def load_zones(self):
        """Load zones from JSON file"""
        if not os.path.exists(self.zones_file):
            return
            
        try:
            with open(self.zones_file, 'r') as f:
                zones_data = json.load(f)
                
            for zone_data in zones_data:
                zone = Zone.from_dict(zone_data)
                self.zones[zone.id] = zone
                
            print(f"Loaded {len(self.zones)} zones")
        except Exception as e:
            print(f"Error loading zones: {e}")
            
    def save_zones(self):
        """Save zones to JSON file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.zones_file), exist_ok=True)
            
            zones_data = [zone.to_dict() for zone in self.zones.values()]
            
            with open(self.zones_file, 'w') as f:
                json.dump(zones_data, f, indent=4)
                
        except Exception as e:
            print(f"Error saving zones: {e}")
            
    def create_default_zones(self):
        """Create default zones if none exist"""
        default_zones = [
            Zone(
                name="Main Building",
                description="Primary school building including all classrooms",
                color="#00a0ff"
            ),
            Zone(
                name="Cafeteria",
                description="Dining and lunch area",
                color="#00ff99"
            ),
            Zone(
                name="Gym",
                description="Sports and physical education area",
                color="#ff5500"
            ),
            Zone(
                name="Playground",
                description="Outdoor play area",
                color="#ffaa00"
            ),
            Zone(
                name="Administration",
                description="Admin offices and staff rooms",
                color="#aa00ff"
            )
        ]
        
        for zone in default_zones:
            self.zones[zone.id] = zone
            
        self.save_zones()
        
    def add_zone(self, zone):
        """Add a new zone"""
        if zone.id in self.zones:
            # Update existing zone
            self.zones[zone.id] = zone
            self.zone_updated.emit(zone)
        else:
            # Add new zone
            self.zones[zone.id] = zone
            self.zone_added.emit(zone)
            
        self.save_zones()
        
    def update_zone(self, zone_id, updated_zone):
        """Update an existing zone"""
        if zone_id in self.zones:
            self.zones[zone_id] = updated_zone
            self.zone_updated.emit(updated_zone)
            self.save_zones()
            
    def remove_zone(self, zone_id):
        """Remove a zone"""
        if zone_id in self.zones:
            del self.zones[zone_id]
            self.zone_removed.emit(zone_id)
            self.save_zones()
            
    def enable_zone(self, zone_id, enabled=True):
        """Enable or disable a zone"""
        if zone_id in self.zones:
            self.zones[zone_id].enabled = enabled
            self.zone_status_changed.emit(zone_id, enabled)
            self.save_zones()
            
    def get_zones_for_bell(self, bell):
        """Get list of zones where a bell should play"""
        return [zone for zone in self.zones.values() 
                if zone.enabled and zone.can_play_bell(bell)]
                
    def get_zone_volume(self, zone_id, base_volume=100):
        """Get actual volume for a zone based on its modifier"""
        if zone_id in self.zones:
            return (base_volume * self.zones[zone_id].volume_modifier) / 100
        return base_volume
        
    def get_enabled_zones(self):
        """Get list of all enabled zones"""
        return [zone for zone in self.zones.values() if zone.enabled]
        
    def get_all_zones(self):
        """Get list of all zones"""
        return list(self.zones.values())


class ZoneScheduleRule:
    """Special rule for zone-specific scheduling"""
    
    def __init__(self, zone_id, bell_id, enabled=True, volume_override=None, 
                 alternate_sound=None, days=None, exclusion_dates=None):
        self.zone_id = zone_id
        self.bell_id = bell_id
        self.enabled = enabled
        self.volume_override = volume_override
        self.alternate_sound = alternate_sound
        self.days = days or []
        self.exclusion_dates = exclusion_dates or []
        
    def to_dict(self):
        """Convert rule to dictionary for JSON storage"""
        return {
            "zone_id": self.zone_id,
            "bell_id": self.bell_id,
            "enabled": self.enabled,
            "volume_override": self.volume_override,
            "alternate_sound": self.alternate_sound,
            "days": self.days,
            "exclusion_dates": self.exclusion_dates
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a ZoneScheduleRule object from dictionary data"""
        return cls(
            zone_id=data["zone_id"],
            bell_id=data["bell_id"],
            enabled=data.get("enabled", True),
            volume_override=data.get("volume_override"),
            alternate_sound=data.get("alternate_sound"),
            days=data.get("days", []),
            exclusion_dates=data.get("exclusion_dates", [])
        )