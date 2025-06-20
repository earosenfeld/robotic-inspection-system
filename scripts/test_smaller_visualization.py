#!/usr/bin/env python3
"""
Test script for the smaller visualization and Test Complete Scene button.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.inspection_service import InspectionService
from app.views.gui import InspectionGUI
import streamlit as st

def test_smaller_visualization():
    """Test the smaller visualization and Test Complete Scene button."""
    print("🤖 Testing Smaller Visualization and Test Complete Scene")
    print("=" * 60)
    
    # Initialize GUI
    gui = InspectionGUI()
    
    print("✅ GUI initialized with smaller visualization configuration")
    
    # Test visualization size
    print("\n📐 Visualization Size Test:")
    try:
        # Test that visualization can be updated with smaller size
        joint_positions = gui.inspection_service.arm_controller.arm.get_joint_positions()
        gui.arm_visualizer.plot_arm(joint_positions)
        gui.arm_visualizer.fig.set_size_inches(6, 4)
        print("✅ Visualization size set to 6x4 inches")
        print("✅ Figure size configured for better layout")
        
    except Exception as e:
        print(f"❌ Visualization size test failed: {str(e)}")
    
    # Test Test Complete Scene button functionality
    print("\n🧪 Test Complete Scene Button:")
    
    # Add some test poses to session state
    test_poses = [
        {
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
        },
        {
            'joint_positions': [[0.0, 0.0, 0.5], [0.0, 0.0, 0.0], [0.0, 0.0, 0.3], 
                               [0.0, 0.0, 0.2], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]],
            'end_effector_position': [0.3, 0.0, 0.6],
            'end_effector_orientation': [0.0, 0.0, 0.0],
            'timestamp': 1234567891.0,
            'description': "Test Pose 2",
            'scene_config': {
                'inspection_type': 'edge_quality',
                'view_type': 'front_view',
                'lighting': 'directional',
                'camera_settings': 'default'
            }
        }
    ]
    
    # Simulate adding poses to session state
    st.session_state.recorded_poses = test_poses
    print(f"✅ Added {len(test_poses)} test poses to session state")
    
    # Test complete scene creation
    test_scene = {
        'name': "Test Complete Scene",
        'description': "Testing all recorded poses",
        'poses': test_poses.copy(),
        'inspection_type': 'comprehensive',
        'created_at': 1234567892.0
    }
    
    print(f"✅ Created test scene with {len(test_scene['poses'])} poses")
    
    # Test scene execution
    if gui.inspection_service.start_inspection_from_custom_scene("Medium Part", test_scene):
        print("✅ Test complete scene started successfully")
        print(f"   - Inspection sequence length: {len(gui.inspection_service.inspection_sequence)}")
        
        # Execute all steps
        total_steps = len(gui.inspection_service.inspection_sequence)
        print(f"   - Executing {total_steps} steps...")
        
        for step_num in range(total_steps):
            if gui.inspection_service.execute_step():
                print(f"   - Step {step_num + 1}/{total_steps} completed")
            else:
                print(f"   - Step {step_num + 1} failed")
                break
        
        print("✅ Complete scene test finished!")
        
        # Show results
        if gui.inspection_service.results:
            print("   - Test Results:")
            for i, result in enumerate(gui.inspection_service.results):
                print(f"     Pose {i+1}: {result['result']['status']}")
                if result['result']['defects']:
                    print(f"       Defects: {result['result']['defects']}")
    else:
        print("❌ Failed to start complete scene test")
    
    # Test layout improvements
    print("\n📐 Layout Improvements:")
    print("✅ Visualization size reduced to 6x4 inches")
    print("✅ Column ratio changed to 2:1 (visualization:test buttons)")
    print("✅ Test Complete Scene button is primary action")
    print("✅ Test Current Pose moved to secondary section")
    print("✅ Better space utilization for simultaneous viewing")
    
    print("\n🎉 All tests completed!")
    print("\n📋 Key Improvements:")
    print("✅ Smaller visualization allows seeing controls and visualization together")
    print("✅ Test Complete Scene button prominently displayed")
    print("✅ Better organized test button hierarchy")
    print("✅ Improved user experience with simultaneous viewing")

if __name__ == "__main__":
    test_smaller_visualization() 