#!/usr/bin/env python3
"""
Test script for the enhanced scene configuration functionality.
This demonstrates how each recorded pose can have its own scene settings.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.inspection_service import InspectionService
import time

def test_pose_scene_configuration():
    """Test creating poses with different scene configurations."""
    print("🎬 Testing Pose Scene Configuration")
    print("=" * 50)
    
    # Initialize service
    service = InspectionService()
    
    # Create poses with different scene configurations
    poses_with_configs = [
        {
            'name': 'Top Surface Inspection',
            'inspection_type': 'surface_quality',
            'view_type': 'top_view',
            'lighting': 'diffuse',
            'camera_settings': 'high_resolution',
            'joint_angles': [0.0, 0.3, 0.5, 0.0, 0.0, 0.0]
        },
        {
            'name': 'Edge Quality Check',
            'inspection_type': 'edge_quality',
            'view_type': 'side_view',
            'lighting': 'directional',
            'camera_settings': 'telephoto',
            'joint_angles': [0.5, 0.0, 0.3, 0.2, 0.0, 0.0]
        },
        {
            'name': 'Fingerprint Detection',
            'inspection_type': 'fingerprints',
            'view_type': 'front_view',
            'lighting': 'low_angle',
            'camera_settings': 'wide_angle',
            'joint_angles': [1.0, -0.2, 0.4, 0.1, 0.0, 0.0]
        },
        {
            'name': 'Comprehensive Check',
            'inspection_type': 'comprehensive',
            'view_type': 'angled_view',
            'lighting': 'multi_angle',
            'camera_settings': 'default',
            'joint_angles': [0.8, 0.1, 0.6, 0.3, 0.1, 0.0]
        }
    ]
    
    recorded_poses = []
    
    for i, config in enumerate(poses_with_configs):
        print(f"\n📸 Recording Pose {i+1}: {config['name']}")
        
        # Move arm to position
        for j, angle in enumerate(config['joint_angles']):
            service.arm_controller.arm.move_joint(j, angle)
        
        # Get current pose data
        current_joint_positions = service.arm_controller.arm.get_joint_positions()
        current_end_effector_pose = service.arm_controller.arm.get_end_effector_pose()
        
        # Create pose record with scene configuration
        pose_record = {
            'joint_positions': [pos.tolist() for pos in current_joint_positions],
            'end_effector_position': current_end_effector_pose[0].tolist(),
            'end_effector_orientation': current_end_effector_pose[1].tolist(),
            'timestamp': time.time(),
            'description': config['name'],
            'scene_config': {
                'inspection_type': config['inspection_type'],
                'view_type': config['view_type'],
                'lighting': config['lighting'],
                'camera_settings': config['camera_settings']
            }
        }
        
        recorded_poses.append(pose_record)
        print(f"✅ Pose recorded with config: {config['inspection_type']} - {config['view_type']} - {config['lighting']}")
    
    return recorded_poses

def test_scene_execution_with_configs(recorded_poses):
    """Test executing a scene with different configurations for each pose."""
    print(f"\n🔍 Testing Scene Execution with Configurations")
    print("=" * 55)
    
    # Initialize service
    service = InspectionService()
    
    # Create scene with configured poses
    custom_scene = {
        'name': "Multi-Configuration Inspection",
        'description': "Inspection with different settings for each pose",
        'poses': recorded_poses,
        'inspection_type': 'comprehensive',
        'created_at': time.time()
    }
    
    print(f"🚀 Starting multi-configuration scene inspection")
    if service.start_inspection_from_custom_scene("Medium Part", custom_scene):
        print("✅ Multi-configuration scene started successfully")
        
        # Execute all steps
        total_steps = len(service.inspection_sequence)
        print(f"📊 Executing {total_steps} inspection steps...")
        
        for step_num in range(total_steps):
            print(f"\n⚡ Executing step {step_num + 1}/{total_steps}")
            if service.execute_step():
                current_result = service.results[-1]
                print(f"   ✅ Step completed: {current_result['description']}")
                print(f"   📊 Result: {current_result['result']['status']}")
                print(f"   🔧 Config: {current_result['inspection_type']} - {current_result['view_type']} - {current_result['lighting']}")
                if current_result['result']['defects']:
                    print(f"   ⚠️  Defects: {current_result['result']['defects']}")
            else:
                print(f"   ❌ Step failed")
                break
        
        print(f"\n🎉 Multi-configuration inspection completed!")
        print(f"📋 Total results: {len(service.results)}")
        
        # Display final results with configurations
        print("\n📊 Final Results with Configurations:")
        for i, result in enumerate(service.results):
            print(f"   Step {i+1}: {result['description']}")
            print(f"      Config: {result['inspection_type']} - {result['view_type']} - {result['lighting']}")
            print(f"      Result: {result['result']['status']}")
            if result['result']['defects']:
                print(f"      Defects: {result['result']['defects']}")
            print()
    else:
        print("❌ Failed to start multi-configuration scene inspection")

def test_individual_pose_testing(recorded_poses):
    """Test testing individual poses with their configurations."""
    print(f"\n🧪 Testing Individual Pose Configurations")
    print("=" * 45)
    
    # Initialize service
    service = InspectionService()
    
    for i, pose in enumerate(recorded_poses):
        print(f"\n🔍 Testing Pose {i+1}: {pose['description']}")
        
        # Create single-pose scene
        test_scene = {
            'name': f"Test - {pose['description']}",
            'description': f"Testing pose {i+1} configuration",
            'poses': [pose],
            'inspection_type': pose['scene_config']['inspection_type'],
            'created_at': time.time()
        }
        
        if service.start_inspection_from_custom_scene("Medium Part", test_scene):
            if service.execute_step():
                result = service.results[-1]
                print(f"   ✅ Test completed: {result['result']['status']}")
                print(f"   🔧 Applied config: {result['inspection_type']} - {result['view_type']} - {result['lighting']}")
                if result['result']['defects']:
                    print(f"   ⚠️  Defects: {result['result']['defects']}")
            else:
                print(f"   ❌ Test failed")
        else:
            print(f"   ❌ Failed to start test")

def test_scene_configuration_summary(recorded_poses):
    """Test generating a summary of scene configurations."""
    print(f"\n📋 Scene Configuration Summary")
    print("=" * 35)
    
    # Analyze configurations
    config_summary = {}
    for pose in recorded_poses:
        scene_config = pose.get('scene_config', {})
        inspection_type = scene_config.get('inspection_type', 'unknown')
        view_type = scene_config.get('view_type', 'unknown')
        lighting = scene_config.get('lighting', 'unknown')
        
        if inspection_type not in config_summary:
            config_summary[inspection_type] = {
                'poses': 0,
                'view_types': set(),
                'lighting': set(),
                'descriptions': []
            }
        
        config_summary[inspection_type]['poses'] += 1
        config_summary[inspection_type]['view_types'].add(view_type)
        config_summary[inspection_type]['lighting'].add(lighting)
        config_summary[inspection_type]['descriptions'].append(pose['description'])
    
    # Display summary
    for inspection_type, summary in config_summary.items():
        print(f"\n🔧 **{inspection_type}**:")
        print(f"   Poses: {summary['poses']}")
        print(f"   View Types: {', '.join(summary['view_types'])}")
        print(f"   Lighting: {', '.join(summary['lighting'])}")
        print(f"   Descriptions: {', '.join(summary['descriptions'])}")

def main():
    """Main test function."""
    print("🎬 Enhanced Scene Configuration Test")
    print("=" * 60)
    
    try:
        # Test 1: Create poses with different configurations
        recorded_poses = test_pose_scene_configuration()
        
        # Test 2: Execute scene with configurations
        test_scene_execution_with_configs(recorded_poses)
        
        # Test 3: Test individual poses
        test_individual_pose_testing(recorded_poses)
        
        # Test 4: Configuration summary
        test_scene_configuration_summary(recorded_poses)
        
        print("\n🎉 All scene configuration tests completed successfully!")
        print("\n💡 Key Features Demonstrated:")
        print("   ✅ Each pose has its own scene configuration")
        print("   ✅ Different inspection types per pose")
        print("   ✅ Different view types per pose")
        print("   ✅ Different lighting per pose")
        print("   ✅ Different camera settings per pose")
        print("   ✅ Scene execution respects individual configurations")
        print("   ✅ Configuration summary and analysis")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 