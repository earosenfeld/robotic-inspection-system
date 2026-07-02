import time
import numpy as np

class PIDController:
    def __init__(self, kp: float, ki: float, kd: float, output_limits: tuple = (-float('inf'), float('inf'))):
        """
        Initialize PID controller.

        Args:
            kp: Proportional gain
            ki: Integral gain
            kd: Derivative gain
            output_limits: Tuple of (min, max) output limits
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_limits = output_limits

        self.previous_error = 0.0
        self.integral = 0.0
        self.last_time = None

    def compute(self, setpoint: float, process_variable: float, dt: float = None) -> float:
        """
        Compute PID output.

        Args:
            setpoint: Target value
            process_variable: Current value
            dt: Timestep in seconds. Pass explicitly in simulation for
                deterministic results; if omitted, falls back to wall-clock
                time between calls.

        Returns:
            Control output
        """
        if dt is None:
            current_time = time.time()
            if self.last_time is None:
                self.last_time = current_time
                return 0.0
            dt = current_time - self.last_time
            self.last_time = current_time

        if dt <= 0:
            return 0.0

        error = setpoint - process_variable
        self.integral += error * dt
        derivative = (error - self.previous_error) / dt

        # Anti-windup: clamp the integral term so it can never exceed the
        # output range on its own, preventing overshoot after saturation.
        if self.ki != 0:
            lo, hi = self.output_limits
            self.integral = float(np.clip(self.integral, lo / self.ki, hi / self.ki))

        output = (self.kp * error +
                 self.ki * self.integral +
                 self.kd * derivative)

        output = float(np.clip(output, self.output_limits[0], self.output_limits[1]))

        self.previous_error = error

        return output

    def reset(self):
        """Reset controller state."""
        self.previous_error = 0.0
        self.integral = 0.0
        self.last_time = None
