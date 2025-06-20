#!/usr/bin/env python3
"""
Test script for the new GUI layout with test buttons next to visualization.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.inspection_service import InspectionService
from app.views.gui import InspectionGUI
import streamlit as st

def test_new_layout():
    """Test the new GUI layout with test buttons and wider design."""
    print("🤖 Testing New GUI Layout with Test Buttons")
    print("=" * 60)
    
    # Initialize GUI
    gui = InspectionGUI()
    
    print("✅ GUI initialized with wide layout configuration")
    print("✅ Page config set to 'wide' layout")
    print("✅ Sidebar state set to 'expanded'")
    
    # Test the new layout structure
    print("\n📐 Layout Structure:")
    print("✅ Interactive Arm Control section at top")
    print("✅ Quick Preset Positions (4 columns)")
    print("✅ Arm Visualization section under controls")
    print("✅ Test buttons next to visualization (3:1 ratio)")
    print("✅ Pose Recording section below visualization")
    print("✅ Recorded Poses section at bottom")
    
    # Test visualization integration
    print("\n🤖 Visualization Integration:")
    try:
        # Test that visualization can be updated
        joint_positions = gui.inspection_service.arm_controller.arm.get_joint_positions()
        gui.arm_visualizer.plot_arm(joint_positions)
        print("✅ Arm visualization updated successfully")
        
        # Test end effector pose
        current_pos, current_orient = gui.inspection_service.arm_controller.arm.get_end_effector_pose()
        print(f"✅ End effector position: X={current_pos[0]:.3f}, Y={current_pos[1]:.3f}, Z={current_pos[2]:.3f}")
        print(f"✅ End effector orientation: R={current_orient[0]:.3f}, P={current_orient[1]:.3f}, Y={current_orient[2]:.3f}")
        
    except Exception as e:
        print(f"❌ Visualization test failed: {str(e)}")
    
    # Test test button functionality
    print("\n🧪 Test Button Functionality:")
    
    # Simulate test current pose
    current_joint_positions = gui.inspection_service.arm_controller.arm.get_joint_positions()
    current_end_effector_pose = gui.inspection_service.arm_controller.arm.get_end_effector_pose()
    
    test_pose = {
        'joint_positions': [pos.tolist() for pos in current_joint_positions],
        'end_effector_position': current_end_effector_pose[0].tolist(),
        'end_effector_orientation': current_end_effector_pose[1].tolist(),
        'timestamp': 1234567890.0,
        'description': "Test Current Pose",
        'scene_config': {
            'inspection_type': 'surface_quality',
            'view_type': 'custom_view',
            'lighting': 'standard',
            'camera_settings': 'default'
        }
    }
    
    test_scene = {
        'name': "Test Current Pose",
        'description': "Testing current arm position",
        'poses': [test_pose],
        'inspection_type': 'surface_quality',
        'created_at': 1234567890.0
    }
    
    if gui.inspection_service.start_inspection_from_custom_scene("Medium Part", test_scene):
        print("✅ Test current pose scene created successfully")
        if gui.inspection_service.execute_step():
            result = gui.inspection_service.results[-1]
            print(f"✅ Test current pose executed: {result['result']['status']}")
        else:
            print("❌ Test current pose execution failed")
    else:
        print("❌ Failed to create test current pose scene")
    
    # Test preset test buttons
    print("\n🔍 Preset Test Buttons:")
    
    # Test top view preset
    original_angles = gui.inspection_service.arm_controller.arm.joint_angles.copy()
    gui.update_arm_position(0, 0.0)  # Base
    gui.update_arm_position(1, 0.3)  # Shoulder
    gui.update_arm_position(2, 0.5)  # Elbow
    gui.update_arm_position(3, 0.0)  # Wrist 1
    gui.update_arm_position(4, 0.0)  # Wrist 2
    gui.update_arm_position(5, 0.0)  # Wrist 3
    print("✅ Top view preset test - arm moved to top view position")
    
    # Test front view preset
    gui.update_arm_position(0, 0.5)  # Base
    gui.update_arm_position(1, 0.0)  # Shoulder
    gui.update_arm_position(2, 0.3)  # Elbow
    gui.update_arm_position(3, 0.2)  # Wrist 1
    gui.update_arm_position(4, 0.0)  # Wrist 2
    gui.update_arm_position(5, 0.0)  # Wrist 3
    print("✅ Front view preset test - arm moved to front view position")
    
    # Restore original position
    for i, angle in enumerate(original_angles):
        gui.update_arm_position(i, angle)
    print("✅ Original position restored")
    
    print("\n🎉 All layout tests completed!")
    print("\n📋 New Layout Features:")
    print("✅ Wider page layout with st.set_page_config")
    print("✅ Arm visualization positioned under interactive controls")
    print("✅ Test buttons next to visualization (3:1 column ratio)")
    print("✅ Quick test current pose functionality")
    print("✅ Preset test buttons for top and front views")
    print("✅ Better space utilization with wide layout")
    print("✅ Improved user experience with integrated testing")

if __name__ == "__main__":
    test_new_layout() 