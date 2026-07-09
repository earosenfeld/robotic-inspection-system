#!/usr/bin/env python3
"""
Test script to demonstrate PID control implementation in the robotic arm
"""

import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.models.robotic_arm import RoboticArm

def test_pid_control():
    """Test the PID control implementation."""
    
    print("🤖 TESTING PID CONTROL IMPLEMENTATION")
    print("=" * 50)
    
    # Create robotic arm
    arm = RoboticArm()
    
    # Test 1: Direct movement (no PID)
    print("\n📋 Test 1: Direct Movement (No PID)")
    print("-" * 30)
    arm.set_pid_control(False)
    
    start_time = time.time()
    success = arm.move_joint(0, 0.5)  # Move base joint to 0.5 radians
    end_time = time.time()
    
    print(f"Direct movement result: {success}")
    print(f"Time taken: {end_time - start_time:.4f} seconds")
    print(f"Final joint angle: {arm.joint_angles[0]:.4f} radians")
    
    # Test 2: PID movement
    print("\n📋 Test 2: PID Movement")
    print("-" * 30)
    arm.set_pid_control(True)
    
    # Reset joint to 0
    arm.joint_angles[0] = 0.0
    
    start_time = time.time()
    success = arm.move_joint(0, 0.5)  # Move base joint to 0.5 radians with PID
    end_time = time.time()
    
    print(f"PID movement result: {success}")
    print(f"Time taken: {end_time - start_time:.4f} seconds")
    print(f"Final joint angle: {arm.joint_angles[0]:.4f} radians")
    
    # Test 3: Multiple joints with PID
    print("\n📋 Test 3: Multiple Joints with PID")
    print("-" * 30)
    
    # Reset all joints
    arm.reset()
    
    # Move multiple joints
    target_angles = [0.3, 0.2, -0.1, 0.0, 0.0, 0.0]
    
    start_time = time.time()
    for i, target_angle in enumerate(target_angles):
        print(f"\nMoving joint {i} to {target_angle} radians...")
        success = arm.move_joint(i, target_angle)
        if success:
            print(f"Joint {i} reached target: {arm.joint_angles[i]:.4f}")
        else:
            print(f"Joint {i} failed to reach target")
    
    end_time = time.time()
    print(f"\nTotal time for all joints: {end_time - start_time:.4f} seconds")
    
    # Test 4: PID parameter tuning
    print("\n📋 Test 4: PID Parameter Tuning")
    print("-" * 30)
    
    # Set different PID parameters for joint 1
    arm.set_pid_parameters(1, kp=2.0, ki=0.2, kd=0.1)
    
    # Reset joint 1
    arm.joint_angles[1] = 0.0
    
    print("Moving joint 1 with tuned PID parameters...")
    start_time = time.time()
    success = arm.move_joint(1, 0.4)
    end_time = time.time()
    
    print(f"Tuned PID movement result: {success}")
    print(f"Time taken: {end_time - start_time:.4f} seconds")
    print(f"Final joint angle: {arm.joint_angles[1]:.4f} radians")
    
    # Test 5: PID status
    print("\n📋 Test 5: PID Status")
    print("-" * 30)
    
    for i in range(3):  # Check first 3 joints
        status = arm.get_pid_status(i)
        if status:
            print(f"Joint {i} PID status:")
            print(f"  kp: {status['kp']}")
            print(f"  ki: {status['ki']}")
            print(f"  kd: {status['kd']}")
            print(f"  integral: {status['integral']:.4f}")
            print(f"  previous_error: {status['previous_error']:.4f}")
    
    print("\n✅ PID Control Test Completed!")

def test_inspection_with_pid():
    """Test a complete inspection with PID control."""
    
    print("\n🔍 TESTING INSPECTION WITH PID CONTROL")
    print("=" * 50)
    
    # Create robotic arm
    arm = RoboticArm()
    arm.set_pid_control(True)
    
    # Simulate inspection sequence
    inspection_positions = [
        [0.2, 0.0, 0.3],  # Front inspection
        [0.0, 0.2, 0.3],  # Right side
        [0.2, 0.0, 0.4]   # Top inspection
    ]
    
    for i, position in enumerate(inspection_positions):
        print(f"\n📸 Inspection Position {i+1}: {position}")
        print("-" * 40)
        
        # Calculate inverse kinematics
        joint_angles = arm.calculate_inverse_kinematics(position, [0, 0, 0])
        
        if joint_angles:
            print(f"Target joint angles: {[f'{angle:.3f}' for angle in joint_angles]}")
            
            # Move to position using PID control
            start_time = time.time()
            success = True
            
            for j, target_angle in enumerate(joint_angles):
                if not arm.move_joint(j, target_angle):
                    success = False
                    break
            
            end_time = time.time()
            
            if success:
                print(f"✅ Reached inspection position {i+1}")
                print(f"⏱️  Time taken: {end_time - start_time:.2f} seconds")
                
                # Get final pose
                final_pos, final_orient = arm.get_end_effector_pose()
                print(f"📍 Final position: [{final_pos[0]:.3f}, {final_pos[1]:.3f}, {final_pos[2]:.3f}]")
            else:
                print(f"❌ Failed to reach inspection position {i+1}")
        else:
            print(f"❌ No valid joint solution for position {i+1}")
    
    print("\n✅ Inspection Test Completed!")

if __name__ == "__main__":
    # Run basic PID tests
    test_pid_control()
    
    # Run inspection test
    test_inspection_with_pid() 