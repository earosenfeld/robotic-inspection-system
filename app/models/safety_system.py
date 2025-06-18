from enum import Enum
from typing import List, Dict, Any, Optional
import time
from datetime import datetime

class SafetyState(Enum):
    """Enumeration of possible safety system states."""
    NORMAL = "normal"
    EMERGENCY_STOP = "emergency_stop"
    LIGHT_CURTAIN_BREAK = "light_curtain_break"
    DOOR_OPEN = "door_open"
    RESET_REQUIRED = "reset_required"

class SafetyEvent:
    """Class representing a safety event."""
    def __init__(self, event_type: str, timestamp: float, details: Dict[str, Any]):
        self.event_type = event_type
        self.timestamp = timestamp
        self.details = details

class SafetySystem:
    """Model for the safety system."""
    
    def __init__(self):
        """Initialize the safety system."""
        self.emergency_stop_active = False
        self.light_curtain_intact = True
        self.door_closed = True
        self.safety_events = []
        
    def check_light_curtain(self) -> bool:
        """
        Check if the light curtain is intact.
        
        Returns:
            bool: True if light curtain is intact
        """
        return self.light_curtain_intact
        
    def check_door_status(self) -> bool:
        """
        Check if the safety door is closed.
        
        Returns:
            bool: True if door is closed
        """
        return self.door_closed
        
    def is_emergency_stop_active(self) -> bool:
        """
        Check if emergency stop is active.
        
        Returns:
            bool: True if emergency stop is active
        """
        return self.emergency_stop_active
        
    def trigger_emergency_stop(self):
        """Trigger the emergency stop."""
        self.emergency_stop_active = True
        self.safety_events.append({
            'type': 'emergency_stop',
            'timestamp': datetime.now().isoformat()
        })
        
    def trigger_light_curtain_break(self):
        """Trigger a light curtain break."""
        self.light_curtain_intact = False
        self.safety_events.append({
            'type': 'light_curtain_break',
            'timestamp': datetime.now().isoformat()
        })
        
    def trigger_door_open(self):
        """Trigger a door open event."""
        self.door_closed = False
        self.safety_events.append({
            'type': 'door_open',
            'timestamp': datetime.now().isoformat()
        })
        
    def reset(self) -> bool:
        """
        Reset the safety system.
        
        Returns:
            bool: True if reset was successful
        """
        if not self.emergency_stop_active:
            self.light_curtain_intact = True
            self.door_closed = True
            self.safety_events.append({
                'type': 'system_reset',
                'timestamp': datetime.now().isoformat()
            })
            return True
        return False

    def get_state(self) -> SafetyState:
        """Get current safety system state."""
        if self.emergency_stop_active:
            return SafetyState.EMERGENCY_STOP
        elif not self.light_curtain_intact:
            return SafetyState.LIGHT_CURTAIN_BREAK
        elif not self.door_closed:
            return SafetyState.DOOR_OPEN
        else:
            return SafetyState.RESET_REQUIRED

    def get_events(self, limit: Optional[int] = None) -> List[SafetyEvent]:
        """
        Get list of safety events.
        
        Args:
            limit: Optional limit on number of events to return
            
        Returns:
            List of safety events
        """
        if limit is not None:
            return self.safety_events[-limit:]
        return self.safety_events

    def is_safe(self) -> bool:
        """Check if all safety conditions are met."""
        return (not self.emergency_stop_active and
                self.light_curtain_intact and
                self.door_closed) 