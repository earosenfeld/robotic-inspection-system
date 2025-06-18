from typing import List, Tuple, Optional
import numpy as np
from app.models.robotic_arm import RoboticArm

class RoboticArmController:
    """Controller for the robotic arm."""
    
    def __init__(self, arm: RoboticArm):
        """
        Initialize the robotic arm controller.
        
        Args:
            arm: RoboticArm instance to control
        """
        self.arm = arm
        self.is_moving = False
        self.current_sequence = None
        
    def move_to_pose(self, position: List[float], orientation: List[float]) -> bool:
        """
        Move the arm to a specific position and orientation.
        
        Args:
            position: Target position [x, y, z]
            orientation: Target orientation [rx, ry, rz]
            
        Returns:
            bool: True if movement was successful
        """
        try:
            print(f"Moving arm to position: {position}, orientation: {orientation}")
            # Calculate inverse kinematics
            joint_angles = self.arm.calculate_inverse_kinematics(position, orientation)
            
            if joint_angles is None:
                print("Failed to calculate inverse kinematics")
                return False
                
            # Move to calculated joint angles
            return self.move_to_joint_angles(joint_angles)
            
        except Exception as e:
            print(f"Error during arm movement: {str(e)}")
            return False
        
    def move_joint(self, joint_idx: int, target_angle: float) -> float:
        """
        Move a specific joint to a target angle.
        
        Args:
            joint_idx: Index of the joint to move
            target_angle: Target angle in radians
            
        Returns:
            float: Actual angle achieved
        """
        return self.arm.move_joint(joint_idx, target_angle)
        
    def get_current_pose(self) -> tuple:
        """
        Get the current end effector pose.
        
        Returns:
            tuple: (position, orientation) of the end effector
        """
        return self.arm.get_end_effector_pose()
        
    def get_joint_positions(self) -> np.ndarray:
        """
        Get the positions of all joints.
        
        Returns:
            np.ndarray: Array of joint positions
        """
        return self.arm.get_joint_positions()
        
    def reset(self):
        """Reset the arm to home position."""
        self.arm.reset()
        self.is_moving = False
        self.current_sequence = None
        
    def is_busy(self) -> bool:
        """
        Check if the arm is currently moving.
        
        Returns:
            bool: True if arm is moving
        """
        return self.is_moving 

    def check_safety_status(self) -> bool:
        """
        Check if the robotic arm is in a safe state to operate.
        
        Returns:
            bool: True if safe to operate, False otherwise
        """
        try:
            # Simulate safety checks
            # In a real system, this would check:
            # - Emergency stop status
            # - Collision detection
            # - Joint limits
            # - Power status
            # - Error states
            return True
        except Exception as e:
            print(f"Error checking safety status: {str(e)}")
            return False 

    def move_to_joint_angles(self, joint_angles: list) -> bool:
        """
        Move the robotic arm to the specified joint angles.
        Args:
            joint_angles: List of joint angles (in radians)
        Returns:
            bool: True if all joints moved successfully, False otherwise
        """
        try:
            for i, angle in enumerate(joint_angles):
                print(f"Moving joint {i} to angle {angle}")
                success = self.arm.move_joint(i, angle)
                if not success:
                    print(f"Failed to move joint {i}")
                    return False
            print("All joints moved successfully")
            return True
        except Exception as e:
            print(f"Error in move_to_joint_angles: {str(e)}")
            return False 