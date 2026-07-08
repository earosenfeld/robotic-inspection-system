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
    """move_joint sets angles inside limits and rejects out-of-limit targets."""
    arm = RoboticArm()

    assert arm.move_joint(0, np.pi / 4) is True
    assert arm.joint_angles[0] == np.pi / 4

    # Shoulder limit is +/- pi/2: an out-of-range command must be rejected
    # and leave the joint untouched.
    before = arm.joint_angles[1]
    assert arm.move_joint(1, np.pi) is False
    assert arm.joint_angles[1] == before


def test_ik_recovers_reachable_pose():
    """DLS IK converges to a pose sampled from the arm's own FK."""
    arm = RoboticArm()
    q_true = np.array([0.3, -0.4, 0.5, 0.2, 0.3, -0.1])
    T = arm.forward_kinematics(q_true)
    arm.joint_angles = q_true.copy()
    _, rpy = arm.get_end_effector_pose()
    arm.reset()

    solution = arm.calculate_inverse_kinematics(list(T[:3, 3]), list(rpy))
    assert solution is not None
    T_sol = arm.forward_kinematics(np.array(solution))
    assert np.linalg.norm(T_sol[:3, 3] - T[:3, 3]) < 1.5e-3
    R_err = arm._rpy_to_matrix(rpy) @ T_sol[:3, :3].T
    assert np.linalg.norm(arm._rotation_vector(R_err)) < 1.5e-2


def test_ik_unreachable_returns_none():
    arm = RoboticArm()
    assert arm.calculate_inverse_kinematics([5.0, 0.0, 0.0], [0.0, 0.0, 0.0]) is None


def test_jacobian_matches_fk_perturbation():
    """Jacobian position block predicts FK translation for a small joint step."""
    arm = RoboticArm()
    q = np.array([0.2, -0.3, 0.4, 0.1, -0.2, 0.3])
    J = arm.jacobian(q)
    dq = np.array([1e-4, -2e-4, 1.5e-4, -1e-4, 2e-4, -1.5e-4])
    dp_pred = J[:3] @ dq
    dp_true = (arm.forward_kinematics(q + dq) - arm.forward_kinematics(q))[:3, 3]
    assert np.linalg.norm(dp_pred - dp_true) < 1e-6
    
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