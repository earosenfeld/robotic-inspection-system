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
        if not 0 <= joint_index < len(self.joint_angles):
            return False
        lo, hi = self.joint_limits[joint_index]
        if lo <= angle <= hi:
            self.joint_angles[joint_index] = angle
            return True
        return False
    
    def step_towards(self, target_angles: np.ndarray, dt: float = 0.01) -> float:
        """
        Advance the simulated joints one control step toward target_angles.

        Each joint's PID controller outputs a velocity command (rad/s,
        saturated by its output limits) which is integrated over dt, so
        motion unfolds over multiple steps like a real servo axis instead
        of teleporting.

        Args:
            target_angles: Array of 6 target joint angles in radians
            dt: Control timestep in seconds

        Returns:
            Maximum absolute joint error after the step (radians)
        """
        target_angles = np.asarray(target_angles, dtype=float)
        for i, controller in enumerate(self.pid_controllers):
            velocity = controller.compute(target_angles[i], self.joint_angles[i], dt=dt)
            new_angle = self.joint_angles[i] + velocity * dt
            lo, hi = self.joint_limits[i]
            self.joint_angles[i] = float(np.clip(new_angle, lo, hi))
        return float(np.max(np.abs(target_angles - self.joint_angles)))

    def move_to_pose(self, target_position: np.ndarray, target_orientation: np.ndarray,
                    max_iterations: int = 100, tolerance: float = 0.001) -> bool:
        """
        Move end-effector to a target pose via damped-least-squares inverse kinematics.
        
        Args:
            target_position: [x, y, z] target position
            target_orientation: [roll, pitch, yaw] target orientation in radians
            max_iterations: Maximum number of iterations
            tolerance: Position error tolerance
            
        Returns:
            True if target pose was reached, False otherwise
        """
        solution = self.calculate_inverse_kinematics(
            list(target_position), list(target_orientation),
            max_iterations=max_iterations, tolerance=tolerance)
        if solution is None:
            return False
        self.joint_angles = np.asarray(solution, dtype=float)
        current_pos, _ = self.get_end_effector_pose()
        pos_error = np.linalg.norm(np.asarray(target_position, dtype=float) - current_pos)
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
    
    @staticmethod
    def _rpy_to_matrix(rpy: np.ndarray) -> np.ndarray:
        """Rotation matrix from [roll, pitch, yaw] (Rz(yaw) @ Ry(pitch) @ Rx(roll)),
        matching the Euler extraction in get_end_effector_pose()."""
        r, p, y = rpy
        cr, sr = np.cos(r), np.sin(r)
        cp, sp = np.cos(p), np.sin(p)
        cy, sy = np.cos(y), np.sin(y)
        Rz = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]])
        Ry = np.array([[cp, 0, sp], [0, 1, 0], [-sp, 0, cp]])
        Rx = np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]])
        return Rz @ Ry @ Rx

    @staticmethod
    def _rotation_vector(R: np.ndarray) -> np.ndarray:
        """Axis-angle vector of a rotation matrix."""
        angle = np.arccos(np.clip((np.trace(R) - 1.0) / 2.0, -1.0, 1.0))
        if angle < 1e-9:
            return np.zeros(3)
        axis = np.array([
            R[2, 1] - R[1, 2],
            R[0, 2] - R[2, 0],
            R[1, 0] - R[0, 1],
        ]) / (2.0 * np.sin(angle))
        return angle * axis

    def jacobian(self, joint_angles: np.ndarray, eps: float = 1e-6) -> np.ndarray:
        """Numerical 6x6 geometric Jacobian (position + orientation) via
        central differences on the forward kinematics."""
        q = np.asarray(joint_angles, dtype=float)
        J = np.zeros((6, 6))
        for i in range(6):
            dq = np.zeros(6)
            dq[i] = eps
            T_plus = self.forward_kinematics(q + dq)
            T_minus = self.forward_kinematics(q - dq)
            J[:3, i] = (T_plus[:3, 3] - T_minus[:3, 3]) / (2.0 * eps)
            dR = T_plus[:3, :3] @ T_minus[:3, :3].T
            J[3:, i] = self._rotation_vector(dR) / (2.0 * eps)
        return J

    def calculate_inverse_kinematics(self, position: List[float], orientation: List[float],
                                     max_iterations: int = 200, tolerance: float = 1e-3,
                                     damping: float = 0.05) -> Optional[List[float]]:
        """
        Damped-least-squares (Levenberg-Marquardt) inverse kinematics.

        Iterates dq = J^T (J J^T + lambda^2 I)^-1 e over the 6D pose error
        (position + axis-angle orientation), clipping to joint limits each
        step. The damping term keeps steps bounded near singularities.

        Args:
            position: Target position [x, y, z]
            orientation: Target orientation [roll, pitch, yaw] (radians)
            max_iterations: Iteration budget
            tolerance: Convergence threshold on position error (m); the
                orientation error uses 10x this threshold in radians
            damping: DLS damping factor lambda

        Returns:
            List of joint angles if converged within limits, None otherwise
        """
        target_pos = np.asarray(position, dtype=float)
        R_target = self._rpy_to_matrix(np.asarray(orientation, dtype=float))
        lam_sq = damping ** 2
        lo = np.array([l for l, _ in self.joint_limits])
        hi = np.array([h for _, h in self.joint_limits])

        q = np.asarray(self.joint_angles, dtype=float).copy()
        for _ in range(max_iterations):
            T = self.forward_kinematics(q)
            pos_err = target_pos - T[:3, 3]
            ori_err = self._rotation_vector(R_target @ T[:3, :3].T)
            if np.linalg.norm(pos_err) < tolerance and np.linalg.norm(ori_err) < 10 * tolerance:
                return [float(a) for a in q]
            e = np.concatenate([pos_err, ori_err])
            J = self.jacobian(q)
            dq = J.T @ np.linalg.solve(J @ J.T + lam_sq * np.eye(6), e)
            # Bound the step so a bad linearization cannot fling the arm.
            step = np.linalg.norm(dq)
            if step > 0.5:
                dq *= 0.5 / step
            q = np.clip(q + dq, lo, hi)
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