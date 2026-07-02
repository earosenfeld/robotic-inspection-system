import numpy as np
import pytest

from app.models.pid_controller import PIDController
from app.models.robotic_arm import RoboticArm


def test_step_response_converges():
    """A P-dominant controller driving a first-order plant reaches the setpoint."""
    pid = PIDController(kp=2.0, ki=0.5, kd=0.0, output_limits=(-5.0, 5.0))
    dt = 0.01
    position = 0.0
    setpoint = 1.0
    for _ in range(2000):
        velocity = pid.compute(setpoint, position, dt=dt)
        position += velocity * dt
    assert position == pytest.approx(setpoint, abs=1e-3)


def test_explicit_dt_is_deterministic():
    """Two controllers fed identical inputs with explicit dt produce identical outputs."""
    a = PIDController(kp=1.0, ki=0.2, kd=0.05, output_limits=(-1.0, 1.0))
    b = PIDController(kp=1.0, ki=0.2, kd=0.05, output_limits=(-1.0, 1.0))
    outputs_a = [a.compute(1.0, 0.1 * i, dt=0.01) for i in range(50)]
    outputs_b = [b.compute(1.0, 0.1 * i, dt=0.01) for i in range(50)]
    assert outputs_a == outputs_b


def test_anti_windup_bounds_integral():
    """With the output saturated for a long time, the integral term stays bounded."""
    pid = PIDController(kp=0.0, ki=1.0, kd=0.0, output_limits=(-1.0, 1.0))
    # Large persistent error saturates the output immediately.
    for _ in range(1000):
        out = pid.compute(100.0, 0.0, dt=0.01)
        assert out == 1.0
    # Integral must be clamped to what the output range allows (1.0 / ki).
    assert abs(pid.integral) <= 1.0 + 1e-9
    # After the error flips sign, the output must recover within a few steps
    # instead of staying pinned while a huge accumulated integral bleeds off.
    for step in range(5):
        out = pid.compute(-100.0, 0.0, dt=0.01)
        if out == -1.0:
            break
    assert out == -1.0


def test_output_limits_respected():
    pid = PIDController(kp=100.0, ki=0.0, kd=0.0, output_limits=(-2.0, 2.0))
    assert pid.compute(10.0, 0.0, dt=0.01) == 2.0
    assert pid.compute(-10.0, 0.0, dt=0.01) == -2.0


def test_arm_step_towards_converges():
    """The arm's PID-driven stepping reaches a joint target within limits."""
    arm = RoboticArm()
    target = np.array([0.5, 0.3, -0.4, 0.2, 0.1, -0.2])
    error = np.inf
    for _ in range(5000):
        error = arm.step_towards(target, dt=0.01)
        if error < 1e-3:
            break
    assert error < 1e-3
    np.testing.assert_allclose(arm.joint_angles, target, atol=1e-3)


def test_arm_step_towards_respects_joint_limits():
    """Stepping toward an out-of-range target saturates at the joint limit."""
    arm = RoboticArm()
    target = np.zeros(6)
    target[1] = np.pi  # shoulder limit is ±π/2
    for _ in range(5000):
        arm.step_towards(target, dt=0.01)
    assert arm.joint_angles[1] <= np.pi / 2 + 1e-9
