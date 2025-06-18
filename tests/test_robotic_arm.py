import pytest
import numpy as np
from app.models.robotic_arm import RoboticArm

def test_robotic_arm_initialization():
    """Test robotic arm initialization."""
    arm = RoboticArm()
    assert len(arm.joint_angles) == 6
    assert len(arm.pid_controllers) == 6
    assert len(arm.dh_params) == 6
    assert len(arm.joint_limits) == 6

def test_forward_kinematics():
    """Test forward kinematics calculation."""
    arm = RoboticArm()
    
    # Test with zero joint angles
    T = arm.forward_kinematics(np.zeros(6))
    assert T.shape == (4, 4)
    # The end effector position should be a finite vector
    pos = T[:3, 3]
    assert np.all(np.isfinite(pos))
    # The rotation matrix should be valid
    R = T[:3, :3]
    assert np.allclose(np.dot(R, R.T), np.eye(3), atol=1e-6)
    assert np.isclose(np.linalg.det(R), 1.0, atol=1e-6)

def test_move_joint():
    """Test joint movement with PID control."""
    arm = RoboticArm()
    
    # Test moving a single joint
    target_angle = np.pi/4
    new_angle = arm.move_joint(0, target_angle)
    assert -np.pi <= new_angle <= np.pi  # Check joint limits
    
    # Test joint limits
    new_angle = arm.move_joint(0, 2*np.pi)  # Try to move beyond limits
    assert -np.pi <= new_angle <= np.pi

def test_move_to_pose():
    """Test moving to a target pose."""
    arm = RoboticArm()
    
    # Test with a reachable pose
    target_position = np.array([0.5, 0.0, 0.3])
    target_orientation = np.array([0.0, 0.0, 0.0])
    # Should not throw, and should return a bool
    result = arm.move_to_pose(target_position, target_orientation)
    assert isinstance(result, bool)
    
    # Test with an unreachable pose
    target_position = np.array([10.0, 10.0, 10.0])
    result = arm.move_to_pose(target_position, target_orientation)
    assert not result

def test_get_end_effector_pose():
    """Test getting end-effector pose."""
    arm = RoboticArm()
    
    position, orientation = arm.get_end_effector_pose()
    assert position.shape == (3,)
    assert orientation.shape == (3,)
    
    # Test after moving to a pose
    target_position = np.array([0.5, 0.0, 0.3])
    target_orientation = np.array([0.0, 0.0, 0.0])
    arm.move_to_pose(target_position, target_orientation)
    
    position, orientation = arm.get_end_effector_pose()
    # After moving to a pose, the position should be finite
    assert np.all(np.isfinite(position))
    assert np.all(np.isfinite(orientation))

def test_reset():
    """Test resetting the arm."""
    arm = RoboticArm()
    
    # Move to some non-zero position
    arm.move_joint(0, np.pi/4)
    assert not np.allclose(arm.joint_angles, np.zeros(6))
    
    # Reset
    arm.reset()
    assert np.allclose(arm.joint_angles, np.zeros(6)) 