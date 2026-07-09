#!/usr/bin/env python3
"""
Robotic Inspection System - System Architecture Diagram Generator
Suitable for ROS Software Engineer Interview Presentation

This script generates a comprehensive system architecture diagram showing:
- System layers and components
- Data flow and communication patterns
- Integration points and interfaces
- Real-time control loops
- Safety systems and error handling
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np
from typing import List, Tuple, Dict
import os

class SystemArchitectureDiagram:
    """Generate professional system architecture diagrams for robotic systems."""
    
    def __init__(self):
        """Initialize the diagram generator."""
        self.fig, self.ax = plt.subplots(1, 1, figsize=(16, 12))
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 12)
        self.ax.axis('off')
        
        # Color scheme for different system layers
        self.colors = {
            'user_interface': '#E8F4FD',      # Light blue
            'application': '#FFF2CC',         # Light yellow
            'control': '#E1D5E7',             # Light purple
            'hardware': '#D5E8D4',            # Light green
            'safety': '#F8CECC',              # Light red
            'data': '#FFE6CC',                # Light orange
            'communication': '#D4EDDA',       # Light mint
            'border': '#2E86AB'               # Dark blue
        }
        
    def create_rounded_box(self, x: float, y: float, width: float, height: float, 
                          color: str, label: str, alpha: float = 0.8) -> FancyBboxPatch:
        """Create a rounded rectangle box."""
        box = FancyBboxPatch(
            (x, y), width, height,
            boxstyle="round,pad=0.1",
            facecolor=color,
            edgecolor=self.colors['border'],
            linewidth=2,
            alpha=alpha
        )
        self.ax.add_patch(box)
        
        # Add label
        self.ax.text(x + width/2, y + height/2, label, 
                    ha='center', va='center', fontsize=10, fontweight='bold')
        return box
    
    def create_arrow(self, start: Tuple[float, float], end: Tuple[float, float], 
                    label: str = "", style: str = "->", color: str = "black"):
        """Create an arrow with optional label."""
        arrow = ConnectionPatch(
            start, end, "data", "data",
            arrowstyle=style, shrinkA=5, shrinkB=5,
            mutation_scale=20, fc=color, ec=color, linewidth=2
        )
        self.ax.add_patch(arrow)
        
        if label:
            mid_x = (start[0] + end[0]) / 2
            mid_y = (start[1] + end[1]) / 2
            self.ax.text(mid_x, mid_y, label, ha='center', va='center', 
                        fontsize=8, bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
    
    def create_data_flow_diagram(self):
        """Create the main system architecture diagram."""
        
        # Title
        self.ax.text(5, 11.5, "Robotic Inspection System - System Architecture", 
                    ha='center', va='center', fontsize=16, fontweight='bold')
        
        # Layer 1: User Interface Layer
        self.create_rounded_box(0.5, 9.5, 9, 1.5, self.colors['user_interface'], 
                               "User Interface Layer\n(Streamlit Web App)", 0.9)
        
        # UI Components
        self.create_rounded_box(1, 9.7, 2, 1, self.colors['user_interface'], 
                               "Control Panel\n(Part Selection, Start/Stop)", 0.7)
        self.create_rounded_box(3.5, 9.7, 2, 1, self.colors['user_interface'], 
                               "3D Visualization\n(Plotly Arm Display)", 0.7)
        self.create_rounded_box(6, 9.7, 2, 1, self.colors['user_interface'], 
                               "Camera View\n(Simulated FHV7 Output)", 0.7)
        
        # Layer 2: Application Layer
        self.create_rounded_box(0.5, 7.5, 9, 1.5, self.colors['application'], 
                               "Application Layer\n(Inspection Orchestrator)", 0.9)
        
        # Application Components
        self.create_rounded_box(1, 7.7, 2, 1, self.colors['application'], 
                               "Inspection Orchestrator\n(Workflow Management)", 0.7)
        self.create_rounded_box(3.5, 7.7, 2, 1, self.colors['application'], 
                               "Configuration Manager\n(JSON Config Parser)", 0.7)
        self.create_rounded_box(6, 7.7, 2, 1, self.colors['application'], 
                               "Results Processor\n(Data Aggregation)", 0.7)
        
        # Layer 3: Control Layer
        self.create_rounded_box(0.5, 5.5, 9, 1.5, self.colors['control'], 
                               "Control Layer\n(Robot & Camera Controllers)", 0.9)
        
        # Control Components
        self.create_rounded_box(1, 5.7, 2, 1, self.colors['control'], 
                               "Robotic Arm Controller\n(Inverse Kinematics)", 0.7)
        self.create_rounded_box(3.5, 5.7, 2, 1, self.colors['control'], 
                               "Camera Controller\n(Image Capture)", 0.7)
        self.create_rounded_box(6, 5.7, 2, 1, self.colors['control'], 
                               "Safety Controller\n(Monitoring)", 0.7)
        
        # Layer 4: Model Layer
        self.create_rounded_box(0.5, 3.5, 9, 1.5, self.colors['hardware'], 
                               "Model Layer\n(Simulated Hardware)", 0.9)
        
        # Model Components
        self.create_rounded_box(1, 3.7, 2, 1, self.colors['hardware'], 
                               "Robotic Arm Model\n(6-DOF DH Parameters)", 0.7)
        self.create_rounded_box(3.5, 3.7, 2, 1, self.colors['hardware'], 
                               "Camera Model\n(Image Simulation)", 0.7)
        self.create_rounded_box(6, 3.7, 2, 1, self.colors['hardware'], 
                               "Safety System Model\n(State Machine)", 0.7)
        
        # Layer 5: Data Layer
        self.create_rounded_box(0.5, 1.5, 9, 1.5, self.colors['data'], 
                               "Data Layer\n(Storage & Configuration)", 0.9)
        
        # Data Components
        self.create_rounded_box(1, 1.7, 2, 1, self.colors['data'], 
                               "Configuration Files\n(JSON Inspection Plans)", 0.7)
        self.create_rounded_box(3.5, 1.7, 2, 1, self.colors['data'], 
                               "Results Database\n(CSV Logging)", 0.7)
        self.create_rounded_box(6, 1.7, 2, 1, self.colors['data'], 
                               "Image Storage\n(Simulated Captures)", 0.7)
        
        # Safety System (Cross-cutting)
        self.create_rounded_box(8.5, 1.5, 1.5, 9, self.colors['safety'], 
                               "Safety System\n(Emergency Stop, Monitoring)", 0.8)
        
        # Communication Layer
        self.create_rounded_box(0.5, 0.2, 9, 1, self.colors['communication'], 
                               "Communication Layer\n(Inter-Process Communication)", 0.9)
        
        # Add arrows for data flow
        self._add_data_flow_arrows()
        
        # Add real-time control loop
        self._add_control_loop()
        
        # Add system metrics
        self._add_system_metrics()
        
    def _add_data_flow_arrows(self):
        """Add arrows showing data flow between components."""
        
        # User Interface to Application
        self.create_arrow((5, 9.5), (5, 9), "User Commands\n(Part/Inspection Selection)")
        
        # Application to Control
        self.create_arrow((5, 7.5), (5, 7), "Inspection Commands\n(Target Positions)")
        
        # Control to Model
        self.create_arrow((5, 5.5), (5, 5), "Hardware Commands\n(Joint Angles, Capture)")
        
        # Model to Data
        self.create_arrow((5, 3.5), (5, 3), "Sensor Data\n(Images, Joint States)")
        
        # Feedback loops
        self.create_arrow((9, 3.5), (9, 5.5), "Safety Status", "->", "red")
        self.create_arrow((9, 5.5), (9, 7.5), "Control Status", "->", "blue")
        self.create_arrow((9, 7.5), (9, 9.5), "System Status", "->", "green")
        
        # Horizontal communication
        self.create_arrow((3, 7.7), (3.5, 7.7), "Config Data")
        self.create_arrow((5.5, 7.7), (6, 7.7), "Results Data")
        
        self.create_arrow((3, 5.7), (3.5, 5.7), "Joint Commands")
        self.create_arrow((5.5, 5.7), (6, 5.7), "Safety Checks")
        
        self.create_arrow((3, 3.7), (3.5, 3.7), "Image Data")
        self.create_arrow((5.5, 3.7), (6, 3.7), "Safety States")
        
    def _add_control_loop(self):
        """Add real-time control loop visualization."""
        
        # Control loop box
        control_loop = FancyBboxPatch(
            (0.2, 2.5), 9.6, 0.8,
            boxstyle="round,pad=0.1",
            facecolor='none',
            edgecolor='red',
            linewidth=3,
            linestyle='--'
        )
        self.ax.add_patch(control_loop)
        
        self.ax.text(5, 2.9, "Real-Time Control Loop (10Hz)", 
                    ha='center', va='center', fontsize=12, fontweight='bold', color='red')
        
        # Control loop steps
        steps = [
            "1. Read Sensor Data",
            "2. Update State",
            "3. Calculate Control",
            "4. Send Commands"
        ]
        
        for i, step in enumerate(steps):
            x = 1.5 + i * 1.8
            self.ax.text(x, 2.7, step, ha='center', va='center', 
                        fontsize=8, bbox=dict(boxstyle="round,pad=0.2", 
                        facecolor='lightgray', alpha=0.8))
    
    def _add_system_metrics(self):
        """Add system performance metrics."""
        
        metrics_text = """
System Metrics:
• Latency: < 100ms (Control Loop)
• Throughput: 10 FPS (Visualization)
• Reliability: 99.9% (Simulated)
• Safety Response: < 50ms (Emergency Stop)
• Memory Usage: < 512MB
• CPU Usage: < 30%
        """
        
        self.ax.text(0.2, 0.5, metrics_text, fontsize=8, 
                    bbox=dict(boxstyle="round,pad=0.5", 
                    facecolor='lightblue', alpha=0.8),
                    verticalalignment='top')
    
    def create_ros_comparison_diagram(self):
        """Create a comparison diagram showing how this maps to ROS architecture."""
        
        self.fig, self.ax = plt.subplots(1, 1, figsize=(16, 10))
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 10)
        self.ax.axis('off')
        
        # Title
        self.ax.text(5, 9.5, "ROS vs Custom Implementation Comparison", 
                    ha='center', va='center', fontsize=16, fontweight='bold')
        
        # Left side - ROS Implementation
        self.ax.text(2.5, 8.5, "ROS Implementation", ha='center', va='center', 
                    fontsize=14, fontweight='bold', color='blue')
        
        # ROS Nodes
        ros_nodes = [
            "ros_inspection_orchestrator_node",
            "ros_arm_controller_node", 
            "ros_camera_node",
            "ros_safety_monitor_node",
            "ros_visualization_node"
        ]
        
        for i, node in enumerate(ros_nodes):
            y = 7.5 - i * 0.8
            self.create_rounded_box(0.5, y, 4, 0.6, '#E3F2FD', node, 0.8)
        
        # ROS Topics
        topics = [
            "/inspection_commands",
            "/joint_states", 
            "/camera_image",
            "/safety_status",
            "/inspection_results"
        ]
        
        for i, topic in enumerate(topics):
            y = 7.5 - i * 0.8
            self.ax.text(4.8, y + 0.3, topic, ha='center', va='center', 
                        fontsize=8, bbox=dict(boxstyle="round,pad=0.2", 
                        facecolor='lightgreen', alpha=0.8))
        
        # Right side - Custom Implementation
        self.ax.text(7.5, 8.5, "Custom Implementation", ha='center', va='center', 
                    fontsize=14, fontweight='bold', color='green')
        
        custom_components = [
            "InspectionOrchestrator (Class)",
            "RoboticArmController (Class)",
            "CameraController (Class)", 
            "SafetyController (Class)",
            "Streamlit GUI (Web App)"
        ]
        
        for i, component in enumerate(custom_components):
            y = 7.5 - i * 0.8
            self.create_rounded_box(5.5, y, 4, 0.6, '#E8F5E8', component, 0.8)
        
        # Communication comparison
        self.ax.text(5, 2.5, "Communication Pattern Comparison", 
                    ha='center', va='center', fontsize=12, fontweight='bold')
        
        # ROS Communication
        self.ax.text(2.5, 2, "ROS: Publisher/Subscriber Pattern", ha='center', va='center', 
                    fontsize=10, bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue'))
        
        # Custom Communication  
        self.ax.text(7.5, 2, "Custom: Direct Method Calls", ha='center', va='center',
                    fontsize=10, bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen'))
        
        # Advantages/Disadvantages
        advantages_text = """
ROS Advantages:
• Standardized communication
• Rich ecosystem
• Built-in tools (rviz, rqt)
• Multi-language support
• Production ready

Custom Advantages:
• Simpler architecture
• Faster development
• Easier debugging
• No ROS dependency
• Web-based UI
        """
        
        self.ax.text(0.2, 0.5, advantages_text, fontsize=8,
                    bbox=dict(boxstyle="round,pad=0.5", facecolor='lightyellow'),
                    verticalalignment='top')
    
    def save_diagram(self, filename: str = "system_architecture.png", dpi: int = 300):
        """Save the diagram to a file."""
        plt.tight_layout()
        plt.savefig(filename, dpi=dpi, bbox_inches='tight')
        print(f"Diagram saved as {filename}")
    
    def show_diagram(self):
        """Display the diagram."""
        plt.tight_layout()
        plt.show()

def main():
    """Generate and display the system architecture diagrams."""
    
    print("Generating Robotic Inspection System Architecture Diagrams...")
    
    # Create main system architecture diagram
    diagram = SystemArchitectureDiagram()
    diagram.create_data_flow_diagram()
    diagram.save_diagram("robotic_inspection_architecture.png")
    
    # Create ROS comparison diagram
    ros_diagram = SystemArchitectureDiagram()
    ros_diagram.create_ros_comparison_diagram()
    ros_diagram.save_diagram("ros_comparison_architecture.png")
    
    print("\nGenerated diagrams:")
    print("1. robotic_inspection_architecture.png - Main system architecture")
    print("2. ros_comparison_architecture.png - ROS vs Custom implementation")
    
    print("\nKey Interview Points:")
    print("• Demonstrates understanding of layered architecture")
    print("• Shows real-time control loop implementation")
    print("• Illustrates safety system integration")
    print("• Compares with industry standard (ROS)")
    print("• Shows data flow and communication patterns")
    print("• Demonstrates system metrics and performance considerations")

if __name__ == "__main__":
    main()
