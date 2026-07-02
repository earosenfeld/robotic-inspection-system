from enum import Enum
from typing import List, Dict, Any, Optional
import time

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
    """
    Latched safety-state model, mirroring how industrial safety relays behave:
    a fault forces the system out of NORMAL, clearing the fault leaves it in
    RESET_REQUIRED, and only an explicit system reset returns it to NORMAL.
    """

    def __init__(self):
        """Initialize the safety system."""
        self.state = SafetyState.NORMAL
        self.emergency_stop_pressed = False
        self.light_curtain_status = True   # True = clear/intact
        self.door_status = True            # True = closed
        self.events: List[SafetyEvent] = []

    # --- internal helpers -------------------------------------------------

    def _log_event(self, event_type: str, **details):
        self.events.append(SafetyEvent(event_type, time.time(), details))

    def _update_state_after_fault(self):
        """Set state to the highest-priority active fault."""
        if self.emergency_stop_pressed:
            self.state = SafetyState.EMERGENCY_STOP
        elif not self.light_curtain_status:
            self.state = SafetyState.LIGHT_CURTAIN_BREAK
        elif not self.door_status:
            self.state = SafetyState.DOOR_OPEN
        elif self.state != SafetyState.NORMAL:
            # All faults cleared, but a fault occurred since the last system
            # reset — operator must acknowledge before returning to NORMAL.
            self.state = SafetyState.RESET_REQUIRED

    # --- status checks ----------------------------------------------------

    def check_light_curtain(self) -> bool:
        """True if the light curtain is clear/intact."""
        return self.light_curtain_status

    def is_light_curtain_clear(self) -> bool:
        """True if the light curtain is clear/intact."""
        return self.light_curtain_status

    def check_door(self) -> bool:
        """True if the safety door is closed."""
        return self.door_status

    def check_door_status(self) -> bool:
        """True if the safety door is closed."""
        return self.door_status

    def is_door_closed(self) -> bool:
        """True if the safety door is closed."""
        return self.door_status

    def check_emergency_stop(self) -> bool:
        """True if the emergency stop is NOT pressed (circuit healthy)."""
        return not self.emergency_stop_pressed

    def is_emergency_stop_active(self) -> bool:
        """True if the emergency stop is pressed."""
        return self.emergency_stop_pressed

    def is_safe(self) -> bool:
        """True only when no fault is active and no reset is pending."""
        return self.state == SafetyState.NORMAL

    # --- fault triggers ---------------------------------------------------

    def trigger_emergency_stop(self):
        """Press the emergency stop."""
        self.emergency_stop_pressed = True
        self._log_event("emergency_stop")
        self._update_state_after_fault()

    def trigger_light_curtain_break(self):
        """Break the light curtain."""
        self.light_curtain_status = False
        self._log_event("light_curtain_break")
        self._update_state_after_fault()

    def trigger_door_open(self):
        """Open the safety door."""
        self.door_status = False
        self._log_event("door_open")
        self._update_state_after_fault()

    # --- fault resets -----------------------------------------------------

    def reset_emergency_stop(self):
        """Release the emergency stop (system stays in RESET_REQUIRED)."""
        self.emergency_stop_pressed = False
        self._log_event("emergency_stop_reset")
        self._update_state_after_fault()

    def reset_light_curtain(self):
        """Clear the light curtain (system stays in RESET_REQUIRED)."""
        self.light_curtain_status = True
        self._log_event("light_curtain_reset")
        self._update_state_after_fault()

    def reset_door(self):
        """Close the safety door (system stays in RESET_REQUIRED)."""
        self.door_status = True
        self._log_event("door_reset")
        self._update_state_after_fault()

    # --- system reset -----------------------------------------------------

    def reset_system(self) -> bool:
        """
        Acknowledge cleared faults and return to NORMAL.

        Returns False if there is nothing to reset (already NORMAL) or a
        fault is still active; True on success.
        """
        if self.state != SafetyState.RESET_REQUIRED:
            return False
        self.state = SafetyState.NORMAL
        self._log_event("system_reset")
        return True

    def reset(self) -> bool:
        """Alias for reset_system() kept for controller compatibility."""
        return self.reset_system()

    # --- event history ----------------------------------------------------

    def get_events(self, limit: Optional[int] = None) -> List[SafetyEvent]:
        """
        Get list of safety events.

        Args:
            limit: Optional limit on number of events to return

        Returns:
            List of safety events
        """
        if limit is not None:
            return self.events[-limit:]
        return self.events

    def get_last_event_time(self) -> Optional[float]:
        """Timestamp of the most recent safety event, or None."""
        if not self.events:
            return None
        return self.events[-1].timestamp
