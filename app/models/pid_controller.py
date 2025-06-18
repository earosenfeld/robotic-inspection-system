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
        self.last_time = time.time()
        
    def compute(self, setpoint: float, process_variable: float) -> float:
        """
        Compute PID output.
        
        Args:
            setpoint: Target value
            process_variable: Current value
            
        Returns:
            Control output
        """
        current_time = time.time()
        dt = current_time - self.last_time
        
        if dt <= 0:
            return 0.0
            
        error = setpoint - process_variable
        self.integral += error * dt
        derivative = (error - self.previous_error) / dt
        
        # Compute PID output
        output = (self.kp * error + 
                 self.ki * self.integral + 
                 self.kd * derivative)
        
        # Apply output limits
        output = np.clip(output, self.output_limits[0], self.output_limits[1])
        
        # Update state
        self.previous_error = error
        self.last_time = current_time
        
        return output
    
    def reset(self):
        """Reset controller state."""
        self.previous_error = 0.0
        self.integral = 0.0
        self.last_time = time.time() 