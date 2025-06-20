import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import streamlit as st

class ArmVisualizer:
    """Visualization utility for the robotic arm."""
    
    def __init__(self):
        """Initialize the arm visualizer."""
        self.fig = plt.figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.setup_plot()
        
    def setup_plot(self):
        """Setup the 3D plot."""
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.ax.set_xlim([-1, 1])
        self.ax.set_ylim([-1, 1])
        self.ax.set_zlim([0, 1])
        self.ax.set_title('Robotic Arm Visualization')
        
    def plot_arm(self, arm):
        """
        Plot or update the robotic arm configuration.
        If the scatter/lines already exist, simply update their data for a smoother visual without flicker.
        Args:
            arm: RoboticArm instance or array of joint positions
        """
        # Get joint positions
        if hasattr(arm, 'get_joint_positions'):
            joint_positions = arm.get_joint_positions()
        else:
            joint_positions = arm

        # Extract coordinates
        x = [pos[0] for pos in joint_positions]
        y = [pos[1] for pos in joint_positions]
        z = [pos[2] for pos in joint_positions]

        # First time: create scatter & lines
        if not hasattr(self, '_scatter') or self._scatter is None:
            # Clear & set up plot once
            self.ax.clear()
            self.setup_plot()
            self._scatter = self.ax.scatter(x, y, z, c='red', marker='o', s=100)
            self._lines = []
            for i in range(len(joint_positions) - 1):
                line, = self.ax.plot([x[i], x[i+1]], [y[i], y[i+1]], [z[i], z[i+1]], 'b-', linewidth=2)
                self._lines.append(line)
            # Base
            self.ax.plot([0, 0], [0, 0], [0, 0.1], 'k-', linewidth=4)
        else:
            # Update scatter data
            self._scatter._offsets3d = (x, y, z)
            # Update line data
            for i, line in enumerate(self._lines):
                line.set_data_3d([x[i], x[i+1]], [y[i], y[i+1]], [z[i], z[i+1]])

        plt.draw()
        
    def get_figure(self):
        """Get the current figure."""
        return self.fig
        
    def clear(self):
        """Clear the plot."""
        self.ax.clear()
        self.setup_plot()
        plt.draw() 