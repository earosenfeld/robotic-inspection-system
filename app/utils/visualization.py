import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import List, Dict, Any, Optional

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
        Plot the robotic arm configuration.
        
        Args:
            arm: RoboticArm instance or array of joint positions
        """
        self.ax.clear()
        self.setup_plot()
        
        # Get joint positions
        if hasattr(arm, 'get_joint_positions'):
            joint_positions = arm.get_joint_positions()
        else:
            joint_positions = arm
            
        # Extract coordinates
        x = [pos[0] for pos in joint_positions]
        y = [pos[1] for pos in joint_positions]
        z = [pos[2] for pos in joint_positions]
        
        # Plot joints
        self.ax.scatter(x, y, z, c='red', marker='o', s=100)
        
        # Plot links
        for i in range(len(joint_positions) - 1):
            self.ax.plot(
                [x[i], x[i+1]],
                [y[i], y[i+1]],
                [z[i], z[i+1]],
                'b-',
                linewidth=2
            )
            
        # Add base
        self.ax.plot([0, 0], [0, 0], [0, 0.1], 'k-', linewidth=4)
        
        plt.draw()
    
    def plot_arm_with_tooltip(self, joint_positions: List[List[float]], scene_info: Optional[Dict[str, Any]] = None) -> go.Figure:
        """
        Create a Plotly 3D visualization of the robotic arm with interactive tooltips.
        
        Args:
            joint_positions: List of joint positions
            scene_info: Optional scene information for tooltips
            
        Returns:
            Plotly figure object
        """
        # Extract coordinates
        x = [pos[0] for pos in joint_positions]
        y = [pos[1] for pos in joint_positions]
        z = [pos[2] for pos in joint_positions]
        
        # Create figure
        fig = go.Figure()
        
        # Add ground plane
        ground_x = [-0.5, 0.5, 0.5, -0.5, -0.5]
        ground_y = [-0.5, -0.5, 0.5, 0.5, -0.5]
        ground_z = [0, 0, 0, 0, 0]
        
        fig.add_trace(go.Scatter3d(
            x=ground_x, y=ground_y, z=ground_z,
            mode='lines',
            line=dict(color='gray', width=2),
            name='Ground Plane',
            showlegend=False,
            hovertemplate='Ground Plane<extra></extra>'
        ))
        
        # Add workspace boundary (cylinder)
        theta = np.linspace(0, 2*np.pi, 50)
        r = 0.5  # Workspace radius
        workspace_x = r * np.cos(theta)
        workspace_y = r * np.sin(theta)
        workspace_z_top = [0.8] * len(theta)
        workspace_z_bottom = [0] * len(theta)
        
        # Workspace cylinder
        fig.add_trace(go.Surface(
            x=np.array([workspace_x, workspace_x]),
            y=np.array([workspace_y, workspace_y]),
            z=np.array([workspace_z_bottom, workspace_z_top]),
            colorscale=[[0, 'rgba(0,0,255,0.1)'], [1, 'rgba(0,0,255,0.1)']],
            showscale=False,
            name='Workspace',
            hovertemplate='Workspace Boundary<extra></extra>'
        ))
        
        # Add joints
        joint_text = [f"Joint {i+1}<br>Position: ({pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f})" 
                     for i, pos in enumerate(joint_positions)]
        
        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z,
            mode='markers',
            marker=dict(size=8, color='red'),
            name='Joints',
            text=joint_text,
            hovertemplate='%{text}<extra></extra>'
        ))
        
        # Add links
        for i in range(len(joint_positions) - 1):
            fig.add_trace(go.Scatter3d(
                x=[x[i], x[i+1]],
                y=[y[i], y[i+1]],
                z=[z[i], z[i+1]],
                mode='lines',
                line=dict(color='blue', width=4),
                name=f'Link {i+1}',
                showlegend=False,
                hovertemplate=f'Link {i+1}<br>From Joint {i+1} to Joint {i+2}<extra></extra>'
            ))
        
        # Add base
        fig.add_trace(go.Scatter3d(
            x=[0, 0], y=[0, 0], z=[0, 0.1],
            mode='lines',
            line=dict(color='black', width=6),
            name='Base',
            showlegend=False,
            hovertemplate='Base<extra></extra>'
        ))
        
        # Add scene information if available
        if scene_info:
            title_text = f"Robotic Arm - {scene_info.get('scene_name', 'Current Position')}"
            if 'defect_type' in scene_info:
                title_text += f"<br><sub>Inspecting: {scene_info['defect_type']}</sub>"
        else:
            title_text = "Robotic Arm Visualization"
        
        # Update layout with realistic bounds
        fig.update_layout(
            title=title_text,
            scene=dict(
                xaxis_title='X (m)',
                yaxis_title='Y (m)',
                zaxis_title='Z (m)',
                xaxis=dict(range=[-0.6, 0.6]),
                yaxis=dict(range=[-0.6, 0.6]),
                zaxis=dict(range=[0, 0.8]),
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5)
                )
            ),
            height=500,
            margin=dict(l=0, r=0, t=50, b=0)
        )
        
        return fig
        
    def get_figure(self):
        """Get the current figure."""
        return self.fig
        
    def clear(self):
        """Clear the plot."""
        self.ax.clear()
        self.setup_plot()
        plt.draw()


class ResultsVisualizer:
    """Visualization utility for inspection results."""
    
    def __init__(self):
        """Initialize the results visualizer."""
        pass
    
    def create_results_table(self, results: List[Dict[str, Any]]) -> go.Figure:
        """
        Create a Plotly table visualization of inspection results.
        
        Args:
            results: List of inspection result dictionaries
            
        Returns:
            Plotly figure object
        """
        if not results:
            # Create empty table
            fig = go.Figure(data=[go.Table(
                header=dict(
                    values=['Scene', 'Pose', 'Defect Type', 'Result', 'FOV'],
                    fill_color='lightblue',
                    align='left',
                    font=dict(size=12)
                ),
                cells=dict(
                    values=[[], [], [], [], []],
                    align='left',
                    font=dict(size=11)
                )
            )])
        else:
            # Prepare data for table
            scene_numbers = [r['scene_number'] for r in results]
            pose_descriptions = [r['pose_description'] for r in results]
            defect_types = [r['defect_type'] for r in results]
            results_values = [r['result'] for r in results]
            fov_values = [f"{r['fov']}mm" for r in results]
            
            # Color coding for results
            colors = ['lightgreen' if r == 'PASS' else 'lightcoral' for r in results_values]
            
            fig = go.Figure(data=[go.Table(
                header=dict(
                    values=['Scene', 'Pose', 'Defect Type', 'Result', 'FOV'],
                    fill_color='lightblue',
                    align='left',
                    font=dict(size=12, color='black')
                ),
                cells=dict(
                    values=[scene_numbers, pose_descriptions, defect_types, results_values, fov_values],
                    fill_color=[['white'] * len(results), ['white'] * len(results), 
                               ['white'] * len(results), colors, ['white'] * len(results)],
                    align='left',
                    font=dict(size=11, color='black')
                )
            )])
        
        fig.update_layout(
            title="Inspection Results",
            height=400,
            margin=dict(l=0, r=0, t=50, b=0)
        )
        
        return fig
    
    def create_results_summary(self, results: List[Dict[str, Any]]) -> go.Figure:
        """
        Create a summary visualization of inspection results.
        
        Args:
            results: List of inspection result dictionaries
            
        Returns:
            Plotly figure object
        """
        if not results:
            return go.Figure()
        
        # Calculate statistics
        total_scenes = len(results)
        pass_count = sum(1 for r in results if r['result'] == 'PASS')
        fail_count = total_scenes - pass_count
        pass_rate = (pass_count / total_scenes * 100) if total_scenes > 0 else 0
        
        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=['PASS', 'FAIL'],
            values=[pass_count, fail_count],
            hole=0.4,
            marker_colors=['lightgreen', 'lightcoral']
        )])
        
        fig.update_layout(
            title=f"Inspection Summary<br><sub>Pass Rate: {pass_rate:.1f}% ({pass_count}/{total_scenes})</sub>",
            height=300,
            margin=dict(l=0, r=0, t=50, b=0)
        )
        
        return fig 