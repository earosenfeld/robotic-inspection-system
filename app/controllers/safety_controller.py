from typing import List, Dict, Optional
from app.models.safety_system import SafetySystem
import time

class SafetyController:
    """Controller for the safety system."""
    
    def __init__(self, safety_system: SafetySystem):
        """
        Initialize the safety controller.
        
        Args:
            safety_system: SafetySystem instance to control
        """
        self.safety_system = safety_system
        self.safety_events = []
        
    def check_safety_status(self) -> bool:
        """
        Check if all safety conditions are met.
        
        Returns:
            bool: True if all safety conditions are met
        """
        return (
            self.check_light_curtain() and
            self.check_door_status() and
            not self.is_emergency_stop_active()
        )
        
    def check_light_curtain(self) -> bool:
        """
        Check if the light curtain is intact.
        
        Returns:
            bool: True if light curtain is intact
        """
        return self.safety_system.check_light_curtain()
        
    def check_door_status(self) -> bool:
        """
        Check if the safety door is closed.
        
        Returns:
            bool: True if door is closed
        """
        return self.safety_system.check_door_status()
        
    def is_emergency_stop_active(self) -> bool:
        """
        Check if emergency stop is active.
        
        Returns:
            bool: True if emergency stop is active
        """
        return self.safety_system.is_emergency_stop_active()
        
    def trigger_emergency_stop(self):
        """Trigger the emergency stop."""
        self.safety_system.trigger_emergency_stop()
        self.safety_events.append({
            'type': 'emergency_stop',
            'timestamp': time.time()
        })
        
    def reset_emergency_stop(self):
        """Reset emergency stop state."""
        self.safety_system.reset_emergency_stop()
        self.safety_events.append({
            'type': 'emergency_stop_reset',
            'timestamp': time.time()
        })
        
    def set_light_curtain_state(self, is_clear: bool):
        """
        Set light curtain state.
        
        Args:
            is_clear: True if light curtain is clear
        """
        if is_clear:
            self.safety_system.reset_light_curtain()
        else:
            self.safety_system.trigger_light_curtain_break()
        self.safety_events.append({
            'type': 'light_curtain',
            'state': is_clear,
            'timestamp': time.time()
        })
        
    def set_door_state(self, is_closed: bool):
        """
        Set door state.
        
        Args:
            is_closed: True if door is closed
        """
        if is_closed:
            self.safety_system.reset_door()
        else:
            self.safety_system.trigger_door_open()
        self.safety_events.append({
            'type': 'door',
            'state': is_closed,
            'timestamp': time.time()
        })
        
    def get_safety_events(self) -> List[Dict]:
        """
        Get list of safety events.
        
        Returns:
            List of safety event dictionaries
        """
        return self.safety_events.copy()
        
    def get_safety_status(self) -> Dict:
        """
        Get current safety system status.
        
        Returns:
            dict: Safety system status information
        """
        return {
            'is_safe': self.safety_system.is_safe(),
            'emergency_stop_active': self.safety_system.is_emergency_stop_active(),
            'light_curtain_clear': self.safety_system.is_light_curtain_clear(),
            'door_closed': self.safety_system.is_door_closed(),
            'last_event_time': self.safety_system.get_last_event_time()
        }
        
    def reset(self):
        """Reset safety system to default state."""
        self.safety_system = SafetySystem()
        self.safety_events = []
        
    def reset_safety_system(self) -> bool:
        """
        Reset the safety system.
        
        Returns:
            bool: True if reset was successful
        """
        return self.safety_system.reset() 