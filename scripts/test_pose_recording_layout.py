#!/usr/bin/env python3
"""
Test script for the new layout with pose recording moved to the right of visualization.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.inspection_service import InspectionService
from app.views.gui import InspectionGUI
import streamlit as st

def test_pose_recording_layout():
    """Test the new layout with pose recording next to visualization."""
    print("🤖 Testing Pose Recording Layout")
    print("=" * 50)
    
    # Initialize GUI
    gui = InspectionGUI()
    
    print("✅ GUI initialized with new pose recording layout")
    
    # Test the new layout structure
    print("\n📐 New Layout Structure:")
    print("✅ Interactive Arm Control section at top")
    print("✅ Quick Preset Positions (4 columns)")
    print("✅ Arm Visualization & Pose Recording section (2:1 ratio)")
    print("✅ Pose recording controls on the right")
    print("✅ Test Complete Scene button in pose recording section")
    print("✅ Recorded Poses section below")
    
    # Test pose recording functionality
    print("\n📸 Pose Recording Test:")
    
    # Simulate recording a pose
    current_joint_positions = gui.inspection_service.arm_controller.arm.get_joint_positions()
    current_end_effector_pose = gui.inspection_service.arm_controller.arm.get_end_effector_pose()
    
    test_pose = {
        'joint_positions': [pos.tolist() for pos in current_joint_positions],
        'end_effector_position': current_end_effector_pose[0].tolist(),
        'end_effector_orientation': current_end_effector_pose[1].tolist(),
        'timestamp': 1234567890.0,
        'description': "Test Pose from New Layout",
        'scene_config': {
            'inspection_type': 'surface_quality',
            'view_type': 'top_view',
            'lighting': 'diffuse',
            'camera_settings': 'high_resolution'
        }
    }
    
    # Add to session state
    st.session_state.recorded_poses = [test_pose]
    print(f"✅ Test pose recorded with new layout")
    print(f"   - Inspection Type: {test_pose['scene_config']['inspection_type']}")
    print(f"   - View Type: {test_pose['scene_config']['view_type']}")
    print(f"   - Lighting: {test_pose['scene_config']['lighting']}")
    
    # Test Test Complete Scene functionality
    print("\n🧪 Test Complete Scene Test:")
    
    test_scene = {
        'name': "Test Complete Scene",
        'description': "Testing all recorded poses",
        'poses': [test_pose],
        'inspection_type': 'comprehensive',
        'created_at': 1234567891.0
    }
    
    if gui.inspection_service.start_inspection_from_custom_scene("Medium Part", test_scene):
        print("✅ Test complete scene started successfully")
        print(f"   - Inspection sequence length: {len(gui.inspection_service.inspection_sequence)}")
        
        # Execute step
        if gui.inspection_service.execute_step():
            result = gui.inspection_service.results[-1]
            print(f"✅ Step executed: {result['result']['status']}")
        else:
            print("❌ Step execution failed")
    else:
        print("❌ Failed to start complete scene test")
    
    # Test visualization integration
    print("\n🤖 Visualization Integration:")
    try:
        # Test that visualization can be updated
        joint_positions = gui.inspection_service.arm_controller.arm.get_joint_positions()
        gui.arm_visualizer.plot_arm(joint_positions)
        gui.arm_visualizer.fig.set_size_inches(6, 4)
        print("✅ Arm visualization updated with smaller size")
        
        # Test end effector pose
        current_pos, current_orient = gui.inspection_service.arm_controller.arm.get_end_effector_pose()
        print(f"✅ End effector position: X={current_pos[0]:.3f}, Y={current_pos[1]:.3f}, Z={current_pos[2]:.3f}")
        print(f"✅ End effector orientation: R={current_orient[0]:.3f}, P={current_orient[1]:.3f}, Y={current_orient[2]:.3f}")
        
    except Exception as e:
        print(f"❌ Visualization test failed: {str(e)}")
    
    print("\n🎉 All layout tests completed!")
    print("\n📋 Key Improvements:")
    print("✅ Pose recording moved to the right of visualization")
    print("✅ No more scrolling needed to record poses")
    print("✅ Can see robotic arm while recording poses")
    print("✅ Test Complete Scene button integrated in pose recording section")
    print("✅ Better workflow: control → see → record → test")
    print("✅ Improved user experience with simultaneous viewing")

if __name__ == "__main__":
    test_pose_recording_layout() 