#!/usr/bin/env python3
"""
Simplified Robotic Inspection System Architecture
Clean, interview-ready diagram without overlapping text
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

class SimpleArchitectureDiagram:
    """Generate a clean, simple system architecture diagram."""
    
    def __init__(self):
        """Initialize the diagram generator."""
        self.fig, self.ax = plt.subplots(1, 1, figsize=(14, 10))
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 10)
        self.ax.axis('off')
        
        # Simple color scheme
        self.colors = {
            'ui': '#E3F2FD',        # Light blue
            'app': '#FFF3E0',       # Light orange
            'control': '#E8F5E8',   # Light green
            'model': '#F3E5F5',     # Light purple
            'data': '#FFEBEE',      # Light red
            'border': '#1976D2'     # Dark blue
        }
    
    def create_box(self, x, y, width, height, color, title, subtitle=""):
        """Create a simple box with title and subtitle."""
        box = FancyBboxPatch(
            (x, y), width, height,
            boxstyle="round,pad=0.1",
            facecolor=color,
            edgecolor=self.colors['border'],
            linewidth=2
        )
        self.ax.add_patch(box)
        
        # Title
        self.ax.text(x + width/2, y + height - 0.3, title, 
                    ha='center', va='center', fontsize=12, fontweight='bold')
        
        # Subtitle
        if subtitle:
            self.ax.text(x + width/2, y + height/2, subtitle, 
                        ha='center', va='center', fontsize=10)
    
    def create_arrow(self, start, end, label=""):
        """Create a simple arrow."""
        arrow = ConnectionPatch(
            start, end, "data", "data",
            arrowstyle="->", shrinkA=5, shrinkB=5,
            mutation_scale=20, fc='black', ec='black', linewidth=2
        )
        self.ax.add_patch(arrow)
        
        if label:
            mid_x = (start[0] + end[0]) / 2
            mid_y = (start[1] + end[1]) / 2
            self.ax.text(mid_x, mid_y, label, ha='center', va='center', 
                        fontsize=9, bbox=dict(boxstyle="round,pad=0.2", 
                        facecolor='white', alpha=0.9))
    
    def create_diagram(self):
        """Create the simplified architecture diagram."""
        
        # Title
        self.ax.text(5, 9.5, "Robotic Inspection System Architecture", 
                    ha='center', va='center', fontsize=16, fontweight='bold')
        
        # Layer 1: User Interface
        self.create_box(1, 7.5, 8, 1.5, self.colors['ui'], 
                       "User Interface Layer", "Streamlit Web App")
        
        # UI Components
        self.create_box(1.5, 7.7, 2, 1, self.colors['ui'], "Control Panel")
        self.create_box(4, 7.7, 2, 1, self.colors['ui'], "3D Visualization")
        self.create_box(6.5, 7.7, 2, 1, self.colors['ui'], "Camera View")
        
        # Layer 2: Application
        self.create_box(1, 5.5, 8, 1.5, self.colors['app'], 
                       "Application Layer", "Inspection Orchestrator")
        
        # App Components
        self.create_box(1.5, 5.7, 2, 1, self.colors['app'], "Orchestrator")
        self.create_box(4, 5.7, 2, 1, self.colors['app'], "Config Manager")
        self.create_box(6.5, 5.7, 2, 1, self.colors['app'], "Results Processor")
        
        # Layer 3: Control
        self.create_box(1, 3.5, 8, 1.5, self.colors['control'], 
                       "Control Layer", "Robot & Camera Controllers")
        
        # Control Components
        self.create_box(1.5, 3.7, 2, 1, self.colors['control'], "Arm Controller")
        self.create_box(4, 3.7, 2, 1, self.colors['control'], "Camera Controller")
        self.create_box(6.5, 3.7, 2, 1, self.colors['control'], "Safety Controller")
        
        # Layer 4: Model
        self.create_box(1, 1.5, 8, 1.5, self.colors['model'], 
                       "Model Layer", "Simulated Hardware")
        
        # Model Components
        self.create_box(1.5, 1.7, 2, 1, self.colors['model'], "Arm Model")
        self.create_box(4, 1.7, 2, 1, self.colors['model'], "Camera Model")
        self.create_box(6.5, 1.7, 2, 1, self.colors['model'], "Safety Model")
        
        # Safety System (side panel)
        self.create_box(8.5, 1.5, 1.5, 7, self.colors['data'], 
                       "Safety System", "Emergency Stop\nMonitoring")
        
        # Data Layer (bottom)
        self.create_box(1, 0.2, 8, 1, self.colors['data'], 
                       "Data Layer", "Configuration & Results")
        
        # Add arrows
        self._add_arrows()
        
        # Add key metrics
        self._add_metrics()
    
    def _add_arrows(self):
        """Add simple arrows showing data flow."""
        
        # Vertical flow
        self.create_arrow((5, 7.5), (5, 7), "User Commands")
        self.create_arrow((5, 5.5), (5, 5), "Inspection Commands")
        self.create_arrow((5, 3.5), (5, 3), "Hardware Commands")
        self.create_arrow((5, 1.5), (5, 1), "Sensor Data")
        
        # Safety feedback
        self.create_arrow((9, 3.5), (9, 5.5), "Safety Status")
        self.create_arrow((9, 5.5), (9, 7.5), "System Status")
        
        # Horizontal flow
        self.create_arrow((3.5, 5.7), (4, 5.7), "Config")
        self.create_arrow((6, 5.7), (6.5, 5.7), "Results")
        self.create_arrow((3.5, 3.7), (4, 3.7), "Commands")
        self.create_arrow((6, 3.7), (6.5, 3.7), "Safety")
    
    def _add_metrics(self):
        """Add key system metrics."""
        
        metrics = """
Key Metrics:
• Control Loop: 10Hz
• Latency: <100ms
• Safety Response: <50ms
• Memory: <512MB
• CPU: <30%
        """
        
        self.ax.text(0.2, 0.5, metrics, fontsize=9, 
                    bbox=dict(boxstyle="round,pad=0.3", 
                    facecolor='lightblue', alpha=0.8),
                    verticalalignment='top')
    
    def save_diagram(self, filename="simple_architecture.png", dpi=300):
        """Save the diagram."""
        plt.tight_layout()
        plt.savefig(filename, dpi=dpi, bbox_inches='tight')
        print(f"Simple diagram saved as {filename}")

def main():
    """Generate the simplified architecture diagram."""
    
    print("Generating Simplified System Architecture Diagram...")
    
    diagram = SimpleArchitectureDiagram()
    diagram.create_diagram()
    diagram.save_diagram()
    
    print("\nSimple diagram created successfully!")
    print("This version is much cleaner and easier to present in interviews.")

if __name__ == "__main__":
    main() 