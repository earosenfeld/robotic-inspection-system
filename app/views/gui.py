import streamlit as st
import time
import numpy as np
import cv2
from typing import Dict, Any
from app.services.inspection_service import InspectionService
from app.utils.visualization import ArmVisualizer

class InspectionGUI:
    def __init__(self):
        """Initialize the GUI."""
        # Initialize services
        self.inspection_service = InspectionService()
        
        # Initialize visualizer
        self.arm_visualizer = ArmVisualizer()
        
        # Initialize session state
        if 'inspection_running' not in st.session_state:
            st.session_state.inspection_running = False
        if 'current_step' not in st.session_state:
            st.session_state.current_step = 0
        if 'inspection_sequence' not in st.session_state:
            st.session_state.inspection_sequence = None
        if 'results' not in st.session_state:
            st.session_state.results = []
            
    def main(self):
        """Main GUI loop."""
        st.title("Robotic Inspection System")
        
        # Controls at the top
        st.title("Robotic Inspection System")
        part_type = st.selectbox(
            "Select Part Type",
            self.inspection_service.get_available_parts(),
            key="part_type_select_main"
        )
        inspection_types = {
            "Small Part": ["scratches_small", "fingerprints"],
            "Medium Part": ["scratches_large", "fingerprints", "surface_quality"],
            "Large Part": ["scratches_large", "fingerprints", "surface_quality", "edge_quality"]
        }
        inspection_type = st.selectbox(
            "Select Inspection Type",
            inspection_types[part_type],
            key="inspection_type_select_main"
        )
        # Place Start Inspection and Execute Step buttons side by side
        button_col1, button_col2 = st.columns([1, 1])
        with button_col1:
            if st.button("Start Inspection"):
                st.session_state.inspection_type = inspection_type
                self.inspection_service.inspection_type = inspection_type
                if self.inspection_service.start_inspection(part_type, inspection_type):
                    st.session_state.inspection_running = True
                    st.session_state.current_step = 0
                    st.session_state.inspection_sequence = self.inspection_service.inspection_sequence
                    st.session_state.results = []
                    st.success("Inspection started successfully!")
                else:
                    st.error("Failed to start inspection")
        with button_col2:
            if st.button("Execute Step"):
                if hasattr(st.session_state, 'inspection_type'):
                    self.inspection_service.inspection_type = st.session_state.inspection_type
                # Debug info in a modal
                with st.expander("Debug Info"):
                    st.write(f"Session State - Inspection Running: {st.session_state.inspection_running}")
                    st.write(f"Session State - Current Step: {st.session_state.current_step}")
                    st.write(f"Session State - Inspection Sequence: {st.session_state.inspection_sequence is not None}")
                    if st.session_state.inspection_sequence and st.session_state.current_step < len(st.session_state.inspection_sequence):
                        st.write(f"Session State - Current Step Data: {st.session_state.inspection_sequence[st.session_state.current_step]}")
                    else:
                        st.write("Inspection completed!")
                        return
                if not st.session_state.inspection_running:
                    st.error("No inspection running - please start an inspection first")
                elif not st.session_state.inspection_sequence:
                    st.error("Inspection sequence lost - please restart the inspection")
                else:
                    # Update service with session state
                    st.write("Updating service with session state...")
                    self.inspection_service.inspection_sequence = st.session_state.inspection_sequence
                    self.inspection_service.current_step = st.session_state.current_step
                    self.inspection_service.results = st.session_state.results
                    st.write(f"Service updated - Current Step: {self.inspection_service.current_step}")
                    if self.inspection_service.execute_step():
                        st.success("Step executed successfully")
                        # Update session state
                        st.session_state.current_step = self.inspection_service.current_step
                        st.session_state.results = self.inspection_service.results
                        st.write(f"Updated Session State - Current Step: {st.session_state.current_step}")
                        if st.session_state.current_step >= len(st.session_state.inspection_sequence):
                            st.session_state.inspection_running = False
                            st.write("Inspection sequence completed - setting inspection_running to False")
                    else:
                        st.error("Failed to execute step - check console for detailed error messages")
        
        # Inspection view and results side by side
        col_view, col_results = st.columns([2, 1])
        with col_view:
            st.subheader("Inspection View")
            # Create a placeholder for the camera feed
            camera_placeholder = st.empty()
            
            # Create a placeholder for arm visualization
            arm_placeholder = st.empty()
            
            # Update arm visualization
            with arm_placeholder.container():
                self.arm_visualizer.plot_arm(self.inspection_service.arm_controller.arm.get_joint_positions())
                st.pyplot(self.arm_visualizer.fig)
            
            # Display inspection progress
            st.subheader("Inspection Progress")
            if st.session_state.inspection_sequence is not None:
                total_steps = len(st.session_state.inspection_sequence)
                current_step = st.session_state.current_step
                st.write(f"Step {current_step + 1} of {total_steps}")
                
                # Display current step information
                st.subheader("Current Step")
                if current_step < total_steps:
                    current_step_info = st.session_state.inspection_sequence[current_step]
                    st.write(f"Type: {current_step_info['type']}")
                    st.write(f"Position: {current_step_info['position']}")
                    st.write(f"Description: {current_step_info['description']}")
                    
                    # Display next step information
                    st.subheader("Next Step")
                    if current_step < total_steps - 1:
                        next_step = st.session_state.inspection_sequence[current_step + 1]
                        st.write(f"Type: {next_step['type']}")
                        st.write(f"Position: {next_step['position']}")
                        st.write(f"Description: {next_step['description']}")
                    else:
                        st.write("This is the final step")
                else:
                    st.success("Inspection completed!")
            else:
                st.warning("No inspection sequence is running. Please start an inspection.")
        
        with col_results:
            st.subheader("Inspection Results")
            if st.session_state.results:
                for result in st.session_state.results:
                    st.write(f"Step {result['step'] + 1}:")
                    st.write(f"Type: {result['type']}")
                    st.write(f"Result: {result['result']}")
            else:
                st.info("No results available")

def main():
    """Main entry point for the GUI."""
    gui = InspectionGUI()
    gui.main()
    
if __name__ == "__main__":
    main() 