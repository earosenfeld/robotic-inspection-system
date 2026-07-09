#!/usr/bin/env python3
"""
Test script to show exactly what commands the orchestrator sends
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.inspection_orchestrator import InspectionOrchestrator

def test_orchestrator_commands():
    """Test and show the commands sent by the orchestrator."""
    
    print("🤖 ROBOTIC INSPECTION SYSTEM - COMMAND EXAMPLES")
    print("=" * 60)
    
    # Create orchestrator
    orchestrator = InspectionOrchestrator()
    
    # Show available parts
    parts = orchestrator.get_available_parts()
    print(f"\n📋 Available Parts: {parts}")
    
    # Show inspection types for Small Part
    inspection_types = orchestrator.get_part_inspection_types("Small Part")
    print(f"🔍 Inspection Types for Small Part: {inspection_types}")
    
    # Start an inspection
    print(f"\n🚀 Starting inspection for Small Part - scratches_small")
    success = orchestrator.start_inspection("Small Part", "scratches_small")
    print(f"Start success: {success}")
    
    # Show current scene info
    scene_info = orchestrator.get_current_scene_info()
    print(f"\n📸 Current Scene Info:")
    print(f"   Scene: {scene_info['scene_name']}")
    print(f"   Position: {scene_info['position']}")
    print(f"   Defect Type: {scene_info['defect_type']}")
    print(f"   FOV: {scene_info['fov']} degrees")
    
    # Execute a step to see the commands
    print(f"\n⚡ EXECUTING INSPECTION STEP")
    print("-" * 40)
    
    result = orchestrator.execute_next_step()
    
    print(f"\n📊 Step Result:")
    print(f"   Success: {result['success']}")
    if result['success']:
        print(f"   Scene: {result['result']['scene_name']}")
        print(f"   Position: {result['result']['pose_description']}")
        print(f"   Inspection Result: {result['result']['result']}")
        print(f"   Arm Positions: {len(result['arm_positions'])} joint positions")
    
    # Show inspection status
    status = orchestrator.get_inspection_status()
    print(f"\n📈 Inspection Status:")
    print(f"   Running: {status['is_running']}")
    print(f"   Current Scene: {status['current_scene']}")
    print(f"   Total Scenes: {status['total_scenes']}")
    print(f"   Safety Status: {status['safety_status']}")
    print(f"   Results Count: {status['results_count']}")
    
    print(f"\n✅ Test completed!")

if __name__ == "__main__":
    test_orchestrator_commands() 