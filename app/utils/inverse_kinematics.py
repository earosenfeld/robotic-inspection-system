from typing import List, Optional
import numpy as np

from app.models.robotic_arm import RoboticArm


def solve_ik(arm: RoboticArm, target_position: List[float], target_orientation: List[float]):
    """Try to compute IK for the given pose and update the arm in‐place.

    Args:
        arm: RoboticArm instance.
        target_position: [x, y, z]
        target_orientation: [roll, pitch, yaw]
    Returns:
        bool – True if a solution was applied.
    """
    sol: Optional[List[float]] = arm.calculate_inverse_kinematics(target_position, target_orientation)
    if sol is None:
        return False
    for j, ang in enumerate(sol):
        arm.move_joint(j, ang)
    return True 