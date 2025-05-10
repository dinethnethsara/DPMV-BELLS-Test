import json
import os
import datetime
from PyQt5.QtCore import QObject, QTimer, pyqtSignal, QDateTime, QTime, QDate

class Bell:
    def __init__(self, name, time, sound="default.mp3", days=None, category="Default", 
                 color="#00a0ff", volume=100, enabled=True, icon=None, tts_message=None,
                 repeat=False, urgent=False, silent=False):
        self.name = name
        self.time = time  # QTime object
        self.sound = sound
        self.days = days if days else ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        self.category = category
        self.color = color
        self.volume = volume
        self.enabled = enabled
        self.icon = icon
        self.tts_message = tts_message
        self.repeat = repeat
        self.urgent = urgent
        self.silent = silent
        self.id = f"{name}-{time.toString('hh:mm')}"
        
    def to_dict(self):
        """Convert bell to dictionary for JSON storage"""
        return {
            "name": self.name,
            "time": self.time.toString("hh:mm"),
            "sound": self.sound,
            "days": self.days,
            "category": self.category,
            "color": self.color,
            "volume": self.volume,
            "enabled": self.enabled,
            "icon": self.icon,
            "tts_message": self.tts_message,
            "repeat": self.repeat,
            "urgent": self.urgent,
            "silent": self.silent,
            "id": self.id
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a Bell object from dictionary data"""
        time = QTime.fromString(data["time"], "hh:mm")
        return cls(
            name=data["name"],
            time=time,
            sound=data.get("sound", "default.mp3"),
            days=data.get("days", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]),
            category=data.get("category", "Default"),
            color=data.get("color", "#00a0ff"),
            volume=data.get("volume", 100),
            enabled=data.get("enabled", True),
            icon=data.get("icon", None),
            tts_message=data.get("tts_message", None),
            repeat=data.get("repeat", False),
            urgent=data.get("urgent", False),
            silent=data.get("silent", False)
        )

class BellScheduler(QObject):
    """Manages scheduling and triggering of bells"""
    
    # Signals
    bell_triggered = pyqtSignal(Bell)
    bell_updated = pyqtSignal()
    next_bell_changed = pyqtSignal(Bell, int)  # Bell, seconds until ring
    
    def __init__(self, bells_file="data/bells.json"):
        super().__init__()
        self.bells_file = bells_file
        self.bells = []
        self.next_bell = None
        self.seconds_to_next = 0
        
        # Create timer for checking bells (every second)
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_bells)
        self.check_timer.start(1000)
        
        # Load bells from file
        self.load_bells()
        
    def load_bells(self):
        """Load bells from JSON file"""
        if not os.path.exists(self.bells_file):
            self.create_default_bells()
        else:
            try:
                with open(self.bells_file, 'r') as f:
                    bells_data = json.load(f)
                
                self.bells = [Bell.from_dict(bell_data) for bell_data in bells_data]
                print(f"Loaded {len(self.bells)} bells")
            except Exception as e:
                print(f"Error loading bells: {e}")
                self.create_default_bells()
        
        # Update next bell
        self.update_next_bell()
        
    def create_default_bells(self):
        """Create default bells if no file exists"""
        self.bells = [
            Bell("School Start", QTime(9, 0)),
            Bell("Period 1", QTime(10, 30)),
            Bell("Break", QTime(11, 20)),
            Bell("Period 2", QTime(11, 35)),
            Bell("Lunch", QTime(12, 25)),
            Bell("Period 3", QTime(13, 10)),
            Bell("End of Day", QTime(14, 0))
        ]
        self.save_bells()
        
    def save_bells(self):
        """Save bells to JSON file"""
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.bells_file), exist_ok=True)
        
        bells_data = [bell.to_dict() for bell in self.bells]
        
        with open(self.bells_file, 'w') as f:
            json.dump(bells_data, f, indent=4)
        
    def check_bells(self):
        """Check if any bells need to be triggered"""
        current_time = QTime.currentTime()
        current_day = QDate.currentDate().toString("dddd")
        
        for bell in self.bells:
            # Skip if bell is disabled
            if not bell.enabled:
                continue
                
            # Skip if bell is not scheduled for today
            if current_day not in bell.days:
                continue
                
            # Check if bell time matches current time (ignoring seconds)
            if bell.time.hour() == current_time.hour() and bell.time.minute() == current_time.minute() and current_time.second() == 0:
                self.bell_triggered.emit(bell)
                print(f"Bell triggered: {bell.name}")
        
        # Update next bell info
        self.update_next_bell()
        
    def update_next_bell(self):
        """Update the next bell to ring"""
        current_time = QTime.currentTime()
        current_day = QDate.currentDate().toString("dddd")
        
        # Filter bells that are enabled and scheduled for today
        active_bells = [bell for bell in self.bells if bell.enabled and current_day in bell.days]
        
        # Find the next bell to ring
        next_bell = None
        min_seconds = float('inf')
        
        for bell in active_bells:
            # Calculate seconds until this bell
            seconds_until = self.seconds_until_time(current_time, bell.time)
            
            # If this bell is earlier than current next bell, update
            if seconds_until > 0 and seconds_until < min_seconds:
                next_bell = bell
                min_seconds = seconds_until
        
        # If next bell has changed, emit signal
        if next_bell != self.next_bell or min_seconds != self.seconds_to_next:
            self.next_bell = next_bell
            self.seconds_to_next = min_seconds
            
            if next_bell:
                self.next_bell_changed.emit(next_bell, min_seconds)
    
    def seconds_until_time(self, current, target):
        """Calculate seconds until target time from current time"""
        # Convert both times to seconds since midnight
        current_secs = current.hour() * 3600 + current.minute() * 60 + current.second()
        target_secs = target.hour() * 3600 + target.minute() * 60
        
        # Calculate difference
        diff = target_secs - current_secs
        
        # If target is earlier today, it must be for tomorrow
        if diff < 0:
            diff += 24 * 3600  # Add a day
            
        return diff
    
    def add_bell(self, bell):
        """Add a new bell to the schedule"""
        self.bells.append(bell)
        self.save_bells()
        self.update_next_bell()
        self.bell_updated.emit()
        
    def update_bell(self, bell_id, updated_bell):
        """Update an existing bell"""
        for i, bell in enumerate(self.bells):
            if bell.id == bell_id:
                self.bells[i] = updated_bell
                break
                
        self.save_bells()
        self.update_next_bell()
        self.bell_updated.emit()
        
    def remove_bell(self, bell_id):
        """Remove a bell from the schedule"""
        self.bells = [bell for bell in self.bells if bell.id != bell_id]
        self.save_bells()
        self.update_next_bell()
        self.bell_updated.emit()
        
    def get_bells_for_day(self, day=None):
        """Get bells scheduled for a specific day"""
        if day is None:
            day = QDate.currentDate().toString("dddd")
            
        return [bell for bell in self.bells if day in bell.days]