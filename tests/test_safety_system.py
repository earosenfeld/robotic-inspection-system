import pytest
from app.models.safety_system import SafetySystem, SafetyState

def test_safety_system_initialization():
    """Test safety system initialization."""
    safety = SafetySystem()
    assert safety.state == SafetyState.NORMAL
    assert safety.light_curtain_status
    assert safety.door_status
    assert not safety.emergency_stop_pressed
    assert len(safety.events) == 0

def test_light_curtain():
    """Test light curtain functionality."""
    safety = SafetySystem()
    
    # Test initial state
    assert safety.check_light_curtain()
    
    # Test break
    safety.trigger_light_curtain_break()
    assert not safety.check_light_curtain()
    assert safety.state == SafetyState.LIGHT_CURTAIN_BREAK
    assert len(safety.events) == 1
    assert safety.events[0].event_type == "light_curtain_break"
    
    # Test reset
    safety.reset_light_curtain()
    assert safety.check_light_curtain()
    assert len(safety.events) == 2
    assert safety.events[1].event_type == "light_curtain_reset"

def test_door():
    """Test door functionality."""
    safety = SafetySystem()
    
    # Test initial state
    assert safety.check_door()
    
    # Test open
    safety.trigger_door_open()
    assert not safety.check_door()
    assert safety.state == SafetyState.DOOR_OPEN
    assert len(safety.events) == 1
    assert safety.events[0].event_type == "door_open"
    
    # Test reset
    safety.reset_door()
    assert safety.check_door()
    assert len(safety.events) == 2
    assert safety.events[1].event_type == "door_reset"

def test_emergency_stop():
    """Test emergency stop functionality."""
    safety = SafetySystem()
    
    # Test initial state
    assert safety.check_emergency_stop()
    
    # Test trigger
    safety.trigger_emergency_stop()
    assert not safety.check_emergency_stop()
    assert safety.state == SafetyState.EMERGENCY_STOP
    assert len(safety.events) == 1
    assert safety.events[0].event_type == "emergency_stop"
    
    # Test reset
    safety.reset_emergency_stop()
    assert safety.check_emergency_stop()
    assert len(safety.events) == 2
    assert safety.events[1].event_type == "emergency_stop_reset"

def test_system_reset():
    """Test system reset functionality."""
    safety = SafetySystem()
    
    # Test reset in normal state
    assert not safety.reset_system()  # Should fail in normal state
    
    # Trigger a safety event
    safety.trigger_light_curtain_break()
    assert safety.state == SafetyState.LIGHT_CURTAIN_BREAK
    
    # Try reset while safety event is active
    assert not safety.reset_system()  # Should fail while event is active
    
    # Reset the safety event
    safety.reset_light_curtain()
    assert safety.state == SafetyState.RESET_REQUIRED
    
    # Now try system reset
    assert safety.reset_system()
    assert safety.state == SafetyState.NORMAL
    assert len(safety.events) == 3
    assert safety.events[2].event_type == "system_reset"

def test_event_history():
    """Test event history functionality."""
    safety = SafetySystem()
    
    # Add some events
    safety.trigger_light_curtain_break()
    safety.reset_light_curtain()
    safety.trigger_door_open()
    
    # Test getting all events
    events = safety.get_events()
    assert len(events) == 3
    
    # Test getting limited events
    recent_events = safety.get_events(limit=2)
    assert len(recent_events) == 2
    assert recent_events[0].event_type == "light_curtain_reset"
    assert recent_events[1].event_type == "door_open" 