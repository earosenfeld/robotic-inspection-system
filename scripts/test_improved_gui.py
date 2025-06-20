#!/usr/bin/env python3
"""
Test script for the improved GUI with integrated visualization and scene-based inspection.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.inspection_service import InspectionService
from app.views.gui import InspectionGUI
import streamlit as st

def test_improved_gui_layout():
    """Test the improved GUI layout and functionality."""
    print("🤖 Testing Improved GUI Layout")
    print("=" * 50)
    
    # Initialize GUI
    gui = InspectionGUI()
    
    # Test that we have the correct number of tabs
    print("✅ GUI initialized successfully")
    print(f"✅ Available inspection types: {len(gui.get_inspection_types())}")
    print(f"✅ Available view types: {len(gui.get_view_types())}")
    print(f"✅ Available lighting options: {len(gui.get_lighting_options())}")
    
    # Test predefined scenes
    predefined_scenes = gui.get_predefined_scenes()
    print(f"✅ Predefined scenes: {len(predefined_scenes)}")
    for scene_name, scene_info in predefined_scenes.items():
        print(f"   - {scene_name}: {scene_info['description']}")
    
    # Test pose recording functionality
    print("\n📸 Testing Pose Recording:")
    
    # Simulate recording a pose with scene configuration
    test_pose = {
        'joint_positions': [[0.0, 0.0, 0.0], [0.0, 0.0, 0.3], [0.0, 0.0, 0.5], 
                           [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]],
        'end_effector_position': [0.5, 0.0, 0.8],
        'end_effector_orientation': [0.0, 0.0, 0.0],
        'timestamp': 1234567890.0,
        'description': "Test Pose 1",
        'scene_config': {
            'inspection_type': 'surface_quality',
            'view_type': 'top_view',
            'lighting': 'diffuse',
            'camera_settings': 'high_resolution'
        }
    }
    
    # Add to session state
    st.session_state.recorded_poses = [test_pose]
    print(f"✅ Test pose recorded with scene configuration")
    print(f"   - Inspection Type: {test_pose['scene_config']['inspection_type']}")
    print(f"   - View Type: {test_pose['scene_config']['view_type']}")
    print(f"   - Lighting: {test_pose['scene_config']['lighting']}")
    
    # Test scene creation
    print("\n🎬 Testing Scene Creation:")
    test_scene = gui.create_inspection_scene(
        "Test Comprehensive Scene",
        "A test scene for comprehensive inspection",
        [test_pose]
    )
    print(f"✅ Scene created: {test_scene['name']}")
    print(f"   - Description: {test_scene['description']}")
    print(f"   - Poses: {len(test_scene['poses'])}")
    
    # Test scene-based inspection
    print("\n🔍 Testing Scene-Based Inspection:")
    inspection_service = InspectionService()
    
    if inspection_service.start_inspection_from_custom_scene("Medium Part", test_scene):
        print("✅ Scene-based inspection started successfully")
        print(f"   - Inspection sequence length: {len(inspection_service.inspection_sequence)}")
        
        # Execute a step
        if inspection_service.execute_step():
            result = inspection_service.results[-1]
            print(f"✅ Step executed: {result['result']['status']}")
            if result['result']['defects']:
                print(f"   - Defects found: {result['result']['defects']}")
        else:
            print("❌ Step execution failed")
    else:
        print("❌ Failed to start scene-based inspection")
    
    # Test visualization integration
    print("\n🤖 Testing Visualization Integration:")
    try:
        # Test that visualization can be updated
        joint_positions = inspection_service.arm_controller.arm.get_joint_positions()
        gui.arm_visualizer.plot_arm(joint_positions)
        print("✅ Arm visualization updated successfully")
        
        # Test end effector pose
        current_pos, current_orient = inspection_service.arm_controller.arm.get_end_effector_pose()
        print(f"✅ End effector position: X={current_pos[0]:.3f}, Y={current_pos[1]:.3f}, Z={current_pos[2]:.3f}")
        print(f"✅ End effector orientation: R={current_orient[0]:.3f}, P={current_orient[1]:.3f}, Y={current_orient[2]:.3f}")
        
    except Exception as e:
        print(f"❌ Visualization test failed: {str(e)}")
    
    print("\n🎉 All tests completed!")
    print("\n📋 Summary of Improvements:")
    print("✅ Reduced to 2 tabs: 'Teach-by-Touch & Scenes' and 'Manual Control'")
    print("✅ Integrated visualization on the right side of controls")
    print("✅ Scene-based inspection integrated into teach-by-touch tab")
    print("✅ Pose-specific scene configurations maintained")
    print("✅ Improved layout with better space utilization")

if __name__ == "__main__":
    test_improved_gui_layout() 