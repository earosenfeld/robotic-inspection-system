#!/usr/bin/env python3
"""
Test script for the new teach-by-touch and scene-based inspection functionality.
This demonstrates how the Productive Robotics-style interface works.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.inspection_service import InspectionService
from app.models.robotic_arm import RoboticArm
import numpy as np
import time

def test_teach_by_touch_recording():
    """Test the teach-by-touch pose recording functionality."""
    print("🤖 Testing Teach-by-Touch Pose Recording")
    print("=" * 50)
    
    # Initialize service
    service = InspectionService()
    
    # Simulate moving the arm to different positions and recording poses
    recorded_poses = []
    
    # Pose 1: Top view position
    print("\n📸 Recording Pose 1: Top View")
    service.arm_controller.arm.move_joint(0, 0.0)  # Base
    service.arm_controller.arm.move_joint(1, 0.3)  # Shoulder
    service.arm_controller.arm.move_joint(2, 0.5)  # Elbow
    service.arm_controller.arm.move_joint(3, 0.0)  # Wrist 1
    service.arm_controller.arm.move_joint(4, 0.0)  # Wrist 2
    service.arm_controller.arm.move_joint(5, 0.0)  # Wrist 3
    
    # Record pose
    current_joint_positions = service.arm_controller.arm.get_joint_positions()
    current_end_effector_pose = service.arm_controller.arm.get_end_effector_pose()
    
    pose1 = {
        'joint_positions': [pos.tolist() for pos in current_joint_positions],
        'end_effector_position': current_end_effector_pose[0].tolist(),
        'end_effector_orientation': current_end_effector_pose[1].tolist(),
        'timestamp': time.time(),
        'description': "Top View Position"
    }
    recorded_poses.append(pose1)
    print(f"✅ Pose 1 recorded: {pose1['description']}")
    
    # Pose 2: Front view position
    print("\n📸 Recording Pose 2: Front View")
    service.arm_controller.arm.move_joint(0, 0.5)  # Base
    service.arm_controller.arm.move_joint(1, 0.0)  # Shoulder
    service.arm_controller.arm.move_joint(2, 0.3)  # Elbow
    service.arm_controller.arm.move_joint(3, 0.2)  # Wrist 1
    service.arm_controller.arm.move_joint(4, 0.0)  # Wrist 2
    service.arm_controller.arm.move_joint(5, 0.0)  # Wrist 3
    
    # Record pose
    current_joint_positions = service.arm_controller.arm.get_joint_positions()
    current_end_effector_pose = service.arm_controller.arm.get_end_effector_pose()
    
    pose2 = {
        'joint_positions': [pos.tolist() for pos in current_joint_positions],
        'end_effector_position': current_end_effector_pose[0].tolist(),
        'end_effector_orientation': current_end_effector_pose[1].tolist(),
        'timestamp': time.time(),
        'description': "Front View Position"
    }
    recorded_poses.append(pose2)
    print(f"✅ Pose 2 recorded: {pose2['description']}")
    
    # Pose 3: Side view position
    print("\n📸 Recording Pose 3: Side View")
    service.arm_controller.arm.move_joint(0, 1.0)  # Base
    service.arm_controller.arm.move_joint(1, -0.2)  # Shoulder
    service.arm_controller.arm.move_joint(2, 0.4)  # Elbow
    service.arm_controller.arm.move_joint(3, 0.1)  # Wrist 1
    service.arm_controller.arm.move_joint(4, 0.0)  # Wrist 2
    service.arm_controller.arm.move_joint(5, 0.0)  # Wrist 3
    
    # Record pose
    current_joint_positions = service.arm_controller.arm.get_joint_positions()
    current_end_effector_pose = service.arm_controller.arm.get_end_effector_pose()
    
    pose3 = {
        'joint_positions': [pos.tolist() for pos in current_joint_positions],
        'end_effector_position': current_end_effector_pose[0].tolist(),
        'end_effector_orientation': current_end_effector_pose[1].tolist(),
        'timestamp': time.time(),
        'description': "Side View Position"
    }
    recorded_poses.append(pose3)
    print(f"✅ Pose 3 recorded: {pose3['description']}")
    
    print(f"\n📋 Total poses recorded: {len(recorded_poses)}")
    return recorded_poses

def test_scene_creation(recorded_poses):
    """Test creating an inspection scene from recorded poses."""
    print("\n🎬 Testing Scene Creation")
    print("=" * 30)
    
    # Create a custom scene
    custom_scene = {
        'name': "Comprehensive Part Inspection",
        'description': "Inspect all surfaces of a medium-sized part using recorded poses",
        'poses': recorded_poses,
        'inspection_type': 'custom_scene',
        'created_at': time.time()
    }
    
    print(f"✅ Scene created: {custom_scene['name']}")
    print(f"   Description: {custom_scene['description']}")
    print(f"   Poses: {len(custom_scene['poses'])}")
    
    return custom_scene

def test_scene_based_inspection(custom_scene):
    """Test scene-based inspection execution."""
    print("\n🔍 Testing Scene-Based Inspection")
    print("=" * 35)
    
    # Initialize service
    service = InspectionService()
    
    # Start inspection using custom scene
    print(f"🚀 Starting inspection with scene: {custom_scene['name']}")
    if service.start_inspection_from_custom_scene("Medium Part", custom_scene):
        print("✅ Custom scene inspection started successfully")
        
        # Execute all steps
        total_steps = len(service.inspection_sequence)
        print(f"📊 Executing {total_steps} inspection steps...")
        
        for step_num in range(total_steps):
            print(f"\n⚡ Executing step {step_num + 1}/{total_steps}")
            if service.execute_step():
                current_result = service.results[-1]
                print(f"   ✅ Step completed: {current_result['description']}")
                print(f"   📊 Result: {current_result['result']['status']}")
                if current_result['result']['defects']:
                    print(f"   ⚠️  Defects: {current_result['result']['defects']}")
            else:
                print(f"   ❌ Step failed")
                break
        
        print(f"\n🎉 Inspection completed!")
        print(f"📋 Total results: {len(service.results)}")
        
        # Display final results
        print("\n📊 Final Results:")
        for i, result in enumerate(service.results):
            print(f"   Step {i+1}: {result['description']} - {result['result']['status']}")
            if result['result']['defects']:
                print(f"      Defects: {result['result']['defects']}")
    else:
        print("❌ Failed to start custom scene inspection")

def test_predefined_scenes():
    """Test predefined scene functionality."""
    print("\n📚 Testing Predefined Scenes")
    print("=" * 30)
    
    # Initialize service
    service = InspectionService()
    
    # Test predefined scenes
    predefined_scenes = {
        "Top Surface Inspection": {
            "description": "Inspect the top surface of a part for scratches and surface quality",
            "inspection_type": "surface_quality",
            "camera_angles": ["top_view"],
            "lighting": "diffuse"
        },
        "Edge Quality Check": {
            "description": "Check edges for burrs, chips, and finish quality",
            "inspection_type": "edge_quality", 
            "camera_angles": ["front_view", "back_view", "side_view"],
            "lighting": "directional"
        }
    }
    
    for scene_name, scene_info in predefined_scenes.items():
        print(f"\n🎯 Testing scene: {scene_name}")
        if service.start_inspection_from_scene("Medium Part", scene_info):
            print(f"   ✅ Scene started successfully")
            print(f"   📊 Steps in sequence: {len(service.inspection_sequence)}")
            
            # Execute first step as example
            if service.execute_step():
                result = service.results[-1]
                print(f"   ✅ Example step completed: {result['result']['status']}")
            else:
                print(f"   ❌ Example step failed")
        else:
            print(f"   ❌ Failed to start scene")

def main():
    """Main test function."""
    print("🤖 Productive Robotics-Style Inspection System Test")
    print("=" * 60)
    
    try:
        # Test 1: Teach-by-touch pose recording
        recorded_poses = test_teach_by_touch_recording()
        
        # Test 2: Scene creation
        custom_scene = test_scene_creation(recorded_poses)
        
        # Test 3: Scene-based inspection
        test_scene_based_inspection(custom_scene)
        
        # Test 4: Predefined scenes
        test_predefined_scenes()
        
        print("\n🎉 All tests completed successfully!")
        print("\n💡 Key Features Demonstrated:")
        print("   ✅ Teach-by-touch pose recording")
        print("   ✅ Scene creation from recorded poses")
        print("   ✅ Custom scene-based inspection")
        print("   ✅ Predefined scene templates")
        print("   ✅ Natural, physical robot programming")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 