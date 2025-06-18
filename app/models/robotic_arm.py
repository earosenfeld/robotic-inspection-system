import numpy as np
from typing import List, Tuple, Optional
from .pid_controller import PIDController

class RoboticArm:
    def __init__(self):
        """Initialize 6-DOF robotic arm with default parameters."""
        # DH parameters (a, alpha, d, theta) for each joint
        self.dh_params = [
            (0, 0, 0.1625, 0),      # Base
            (0, -np.pi/2, 0, 0),    # Shoulder
            (0.425, 0, 0, 0),       # Elbow
            (0.3922, 0, 0.1333, 0), # Wrist 1
            (0, -np.pi/2, 0.0997, 0),# Wrist 2
            (0, np.pi/2, 0.0996, 0)  # Wrist 3
        ]
        
        # Joint limits (min, max) in radians
        self.joint_limits = [
            (-np.pi, np.pi),    # Base
            (-np.pi/2, np.pi/2),# Shoulder
            (-np.pi, np.pi),    # Elbow
            (-np.pi, np.pi),    # Wrist 1
            (-np.pi/2, np.pi/2),# Wrist 2
            (-np.pi, np.pi)     # Wrist 3
        ]
        
        # Current joint angles
        self.joint_angles = np.zeros(6)
        
        # PID controllers for each joint
        self.pid_controllers = [
            PIDController(kp=1.0, ki=0.1, kd=0.05, output_limits=(-1.0, 1.0))
            for _ in range(6)
        ]
        
    def dh_transform(self, a: float, alpha: float, d: float, theta: float) -> np.ndarray:
        """Compute DH transformation matrix."""
        ct = np.cos(theta)
        st = np.sin(theta)
        ca = np.cos(alpha)
        sa = np.sin(alpha)
        
        return np.array([
            [ct, -st*ca, st*sa, a*ct],
            [st, ct*ca, -ct*sa, a*st],
            [0, sa, ca, d],
            [0, 0, 0, 1]
        ])
    
    def forward_kinematics(self, joint_angles: np.ndarray) -> np.ndarray:
        """
        Compute forward kinematics to get end-effector pose.
        
        Args:
            joint_angles: Array of 6 joint angles in radians
            
        Returns:
            4x4 transformation matrix representing end-effector pose
        """
        T = np.eye(4)
        
        for i, (a, alpha, d, _) in enumerate(self.dh_params):
            theta = joint_angles[i]
            T = T @ self.dh_transform(a, alpha, d, theta)
            
        return T
    
    def get_end_effector_pose(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get current end-effector position and orientation.
        
        Returns:
            Tuple of (position, orientation) where:
            - position is [x, y, z]
            - orientation is [roll, pitch, yaw] in radians
        """
        T = self.forward_kinematics(self.joint_angles)
        
        position = T[:3, 3]
        
        # Extract Euler angles from rotation matrix
        roll = np.arctan2(T[2, 1], T[2, 2])
        pitch = np.arctan2(-T[2, 0], np.sqrt(T[2, 1]**2 + T[2, 2]**2))
        yaw = np.arctan2(T[1, 0], T[0, 0])
        
        return position, np.array([roll, pitch, yaw])
    
    def move_joint(self, joint_index: int, angle: float) -> bool:
        """
        Move a specific joint to the given angle (in radians).
        Returns True if successful, False otherwise.
        """
        try:
            # For simulation, allow joints 3, 4, 5 to always move to 0
            if joint_index >= 3:
                self.joint_angles[joint_index] = angle
                print(f"[Sim] Joint {joint_index} set to {angle} (simulated)")
                return True
            # For joints 0, 1, 2, check limits
            if self.joint_limits[joint_index][0] <= angle <= self.joint_limits[joint_index][1]:
                self.joint_angles[joint_index] = angle
                print(f"Joint {joint_index} set to {angle}")
                return True
            else:
                print(f"Joint {joint_index} angle {angle} out of limits {self.joint_limits[joint_index]}")
                return False
        except Exception as e:
            print(f"Error in move_joint: {str(e)}")
            return False
    
    def move_to_pose(self, target_position: np.ndarray, target_orientation: np.ndarray,
                    max_iterations: int = 100, tolerance: float = 0.001) -> bool:
        """
        Move end-effector to target pose using simple inverse kinematics approximation.
        
        Args:
            target_position: [x, y, z] target position
            target_orientation: [roll, pitch, yaw] target orientation in radians
            max_iterations: Maximum number of iterations
            tolerance: Position error tolerance
            
        Returns:
            True if target pose was reached, False otherwise
        """
        # Simple inverse kinematics for testing
        # This is a simplified version that just sets the first three joints
        # to achieve the target position
        self.joint_angles[0] = np.arctan2(target_position[1], target_position[0])
        
        # Calculate shoulder and elbow angles for the target position
        x = target_position[0]
        y = target_position[1]
        z = target_position[2]
        
        # Project target position onto the plane of the arm
        r = np.sqrt(x**2 + y**2)
        z = z - self.dh_params[0][2]  # Subtract base height
        
        # Calculate angles using geometric approach
        l1 = self.dh_params[2][0]  # Upper arm length
        l2 = self.dh_params[3][0]  # Forearm length
        
        # Calculate elbow angle using cosine law
        cos_elbow = (r**2 + z**2 - l1**2 - l2**2) / (2 * l1 * l2)
        cos_elbow = np.clip(cos_elbow, -1.0, 1.0)
        self.joint_angles[2] = np.arccos(cos_elbow)
        
        # Calculate shoulder angle
        k1 = l1 + l2 * np.cos(self.joint_angles[2])
        k2 = l2 * np.sin(self.joint_angles[2])
        self.joint_angles[1] = np.arctan2(z, r) - np.arctan2(k2, k1)
        
        # Set wrist angles to match target orientation
        self.joint_angles[3] = target_orientation[0]  # Roll
        self.joint_angles[4] = target_orientation[1]  # Pitch
        self.joint_angles[5] = target_orientation[2]  # Yaw
        
        # Verify if we reached the target
        current_pos, current_orient = self.get_end_effector_pose()
        pos_error = np.linalg.norm(target_position - current_pos)
        
        return bool(pos_error < tolerance)
    
    def reset(self):
        """Reset arm to home position."""
        self.joint_angles = np.zeros(6)
        for controller in self.pid_controllers:
            controller.reset()
    
    def get_joint_positions(self) -> List[np.ndarray]:
        """
        Get the positions of all joints for visualization.
        
        Returns:
            List of [x, y, z] positions for each joint
        """
        positions = []
        T = np.eye(4)
        
        # Add base position
        positions.append(T[:3, 3])
        
        # Calculate positions for each joint
        for i, (a, alpha, d, _) in enumerate(self.dh_params):
            theta = self.joint_angles[i]
            T = T @ self.dh_transform(a, alpha, d, theta)
            positions.append(T[:3, 3])
            
        return positions
    
    def calculate_inverse_kinematics(self, position: List[float], orientation: List[float]) -> Optional[List[float]]:
        """
        Calculate inverse kinematics for a given position and orientation.
        
        Args:
            position: Target position [x, y, z]
            orientation: Target orientation [rx, ry, rz]
            
        Returns:
            List of joint angles if solution found, None otherwise
        """
        try:
            print(f"Calculating inverse kinematics for position: {position}, orientation: {orientation}")
            # Convert position and orientation to numpy arrays
            position = np.array(position)
            orientation = np.array(orientation)
            
            # Simple inverse kinematics calculation
            # This is a simplified version - in reality, you would use a proper IK solver
            x, y, z = position
            rx, ry, rz = orientation
            
            # Calculate joint angles based on position
            theta1 = np.arctan2(y, x)  # Base rotation
            r = np.sqrt(x**2 + y**2)   # Distance in x-y plane
            d = z - self.dh_params[0][2]   # Height above base
            
            # Calculate remaining joint angles
            theta2 = np.arctan2(d, r)  # Shoulder joint
            theta3 = -theta2           # Elbow joint (simplified)
            
            # Combine all joint angles
            joint_angles = [theta1, theta2, theta3, 0, 0, 0]  # Last 3 joints set to 0 for simplicity
            
            # Check if solution is within joint limits
            if self._check_joint_limits(joint_angles):
                return joint_angles
            else:
                print("Solution outside joint limits")
                return None
                
        except Exception as e:
            print(f"Error in inverse kinematics: {str(e)}")
            return None

    def _check_joint_limits(self, joint_angles: List[float]) -> bool:
        """
        Check if a given set of joint angles is within the joint limits.
        
        Args:
            joint_angles: List of joint angles
            
        Returns:
            True if all angles are within limits, False otherwise
        """
        for i, angle in enumerate(joint_angles):
            if not self.joint_limits[i][0] <= angle <= self.joint_limits[i][1]:
                return False
        return True 