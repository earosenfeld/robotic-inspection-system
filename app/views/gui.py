import streamlit as st
import time
import numpy as np
import cv2
import plotly.graph_objects as go
from typing import Dict, Any, Optional
import pandas as pd

from app.services.inspection_orchestrator import InspectionOrchestrator
from app.utils.visualization import ArmVisualizer, ResultsVisualizer
from app.utils.image_simulation import ImageSimulator

class EnhancedInspectionGUI:
    """Enhanced GUI for robotic inspection system with three-panel layout."""
    
    def __init__(self):
        """Initialize the enhanced GUI."""
        # Initialize services - use singleton pattern for orchestrator
        self.orchestrator = self._get_orchestrator()
        self.arm_visualizer = ArmVisualizer()
        self.results_visualizer = ResultsVisualizer()
        self.image_simulator = ImageSimulator()
        
        # Initialize session state
        self._initialize_session_state()
        
    def _get_orchestrator(self):
        """Get or create orchestrator instance using session state."""
        if 'orchestrator' not in st.session_state:
            st.session_state.orchestrator = InspectionOrchestrator()
            print("DEBUG: Created new orchestrator instance")
        else:
            print("DEBUG: Using existing orchestrator instance")
        return st.session_state.orchestrator
        
    def _initialize_session_state(self):
        """Initialize Streamlit session state variables."""
        if 'inspection_running' not in st.session_state:
            st.session_state.inspection_running = False
        if 'current_part' not in st.session_state:
            st.session_state.current_part = None
        if 'current_inspection_type' not in st.session_state:
            st.session_state.current_inspection_type = None
        if 'inspection_results' not in st.session_state:
            st.session_state.inspection_results = []
        if 'current_image' not in st.session_state:
            st.session_state.current_image = None
        if 'current_arm_positions' not in st.session_state:
            st.session_state.current_arm_positions = None
        if 'auto_run' not in st.session_state:
            st.session_state.auto_run = False
            
    def main(self):
        """Main GUI loop with three-panel layout."""
        st.set_page_config(
            page_title="Robotic Inspection System",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Main title
        st.title("🤖 Robotic Inspection System")
        st.markdown("---")
        
        # Control Panel at the top
        self._render_control_panel()
        
        # Three-panel layout
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            self._render_left_panel()
            
        with col2:
            self._render_center_panel()
            
        with col3:
            self._render_right_panel()
        
        # Results section at the bottom
        st.markdown("---")
        self._render_results_section()
        
    def _render_control_panel(self):
        """Render the control panel at the top."""
        st.subheader("🎮 Control Panel")
        
        # Part selection and controls in columns
        col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 1, 1, 1, 1])
        
        with col1:
            # Part selection
            available_parts = self.orchestrator.get_available_parts()
            selected_part = st.selectbox(
                "Select Part Type",
                available_parts,
                key="part_select"
            )
            
        with col2:
            # Inspection type selection
            if selected_part:
                inspection_types = self.orchestrator.get_part_inspection_types(selected_part)
                selected_inspection_type = st.selectbox(
                    "Select Inspection Type",
                    inspection_types,
                    key="inspection_type_select"
                )
            else:
                selected_inspection_type = None
                
        with col3:
            # Start inspection button
            if st.button("🚀 Run Full Inspection", type="primary"):
                if selected_part and selected_inspection_type:
                    self._start_inspection(selected_part, selected_inspection_type)
                    st.session_state.auto_run = True
                    
        with col4:
            # Next step button
            if st.button("⏭️ Next Step"):
                if st.session_state.inspection_running:
                    self._execute_next_step()
                else:
                    st.error("❌ No inspection running. Please start an inspection first.")
                    
        with col5:
            # Reset button
            if st.button("🔄 Reset"):
                self._reset_inspection()
                
        with col6:
            # Emergency stop button
            if st.button("🛑 EMERGENCY STOP", type="secondary", help="Immediately stop all operations"):
                self._emergency_stop()
                
        # Progress bar
        if st.session_state.inspection_running:
            status = self.orchestrator.get_inspection_status()
            current_scene = status.get('current_scene', 0)
            total_scenes = status.get('total_scenes', 0)
            
            if total_scenes > 0:
                progress = current_scene / total_scenes
                st.progress(progress, text=f"Scene {current_scene} of {total_scenes}")
            else:
                st.progress(0, text="Preparing inspection...")
                
    def _render_left_panel(self):
        """Render the left panel - Current Scene Information."""
        st.subheader("📋 Scene Information")
        
        if st.session_state.inspection_running:
            status = self.orchestrator.get_inspection_status()
            scene_info = self.orchestrator.get_current_scene_info()
            
            if scene_info:
                # Scene details
                st.info(f"**Current Scene:** {scene_info['scene_number']} of {scene_info['total_scenes']}")
                st.write(f"**Scene Name:** {scene_info['scene_name']}")
                st.write(f"**Defect Type:** {scene_info['defect_type']}")
                st.write(f"**Field of View:** {scene_info['fov']}mm")
                
                # Part information
                if st.session_state.current_part:
                    st.write(f"**Part:** {st.session_state.current_part}")
                if st.session_state.current_inspection_type:
                    st.write(f"**Inspection Type:** {st.session_state.current_inspection_type}")
                    
                # Status indicators
                st.markdown("### 🔍 Status")
                safety_status = status.get('safety_status', False)
                camera_status = status.get('camera_status', {}).get('ready', False)
                
                col1, col2 = st.columns(2)
                with col1:
                    if safety_status:
                        st.success("✅ Safety OK")
                    else:
                        st.error("❌ Safety Issue")
                        
                with col2:
                    if camera_status:
                        st.success("✅ Camera Ready")
                    else:
                        st.error("❌ Camera Issue")
                        
            else:
                st.warning("No active scene information")
        else:
            st.info("No inspection running. Select a part and start inspection.")
            
    def _render_center_panel(self):
        """Render the center panel - Robotic Arm Visualization."""
        st.subheader("🤖 Robotic Arm Orientation")
        
        if st.session_state.inspection_running:
            # Get current arm positions from session state or orchestrator
            if st.session_state.current_arm_positions is not None:
                arm_positions = st.session_state.current_arm_positions
            else:
                arm_positions = self.orchestrator.arm.get_joint_positions()
                
            scene_info = self.orchestrator.get_current_scene_info()
            
            # Create 3D visualization
            fig = self.arm_visualizer.plot_arm_with_tooltip(arm_positions, scene_info)
            
            # Display the plot
            st.plotly_chart(fig, use_container_width=True)
            
            # Joint information
            st.markdown("### 🔧 Joint Positions")
            for i, pos in enumerate(arm_positions):
                st.write(f"Joint {i+1}: ({pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f})")
                
        else:
            # Show default arm position
            default_positions = [[0, 0, 0], [0, 0, 0.1625], [0, 0, 0.5875], [0, 0, 0.7208], [0, 0, 0.8205], [0, 0, 0.9201]]
            fig = self.arm_visualizer.plot_arm_with_tooltip(default_positions)
            st.plotly_chart(fig, use_container_width=True)
            st.info("Arm in home position")
            
    def _render_right_panel(self):
        """Render the right panel - Simulated Camera View."""
        st.subheader("📷 Simulated Camera View")
        
        if st.session_state.inspection_running:
            # Display current image if available
            if st.session_state.current_image is not None:
                st.image(st.session_state.current_image, channels="BGR", use_container_width=True)
                st.caption("📹 Simulated FHV7 Output")
                
                # Image metadata
                if st.session_state.current_part and st.session_state.current_inspection_type:
                    st.write(f"**Part:** {st.session_state.current_part}")
                    st.write(f"**Inspection:** {st.session_state.current_inspection_type}")
                    
            else:
                # Generate a placeholder image
                if st.session_state.current_part and st.session_state.current_inspection_type:
                    scene_info = self.orchestrator.get_current_scene_info()
                    if scene_info:
                        image = self.image_simulator.generate_inspection_image(
                            st.session_state.current_part,
                            scene_info['defect_type'],
                            defect_probability=0.2
                        )
                        st.image(image, channels="BGR", use_container_width=True)
                        st.caption("📹 Simulated FHV7 Output")
                        
        else:
            # Show placeholder image
            placeholder_image = self.image_simulator.generate_base_image("generic")
            st.image(placeholder_image, channels="BGR", use_container_width=True)
            st.caption("📹 Simulated FHV7 Output - No Inspection Running")
            
    def _render_results_section(self):
        """Render the results section at the bottom."""
        st.subheader("📊 Inspection Results")
        
        if st.session_state.inspection_results:
            # Create results table
            results_df = pd.DataFrame(st.session_state.inspection_results)
            
            # Display table
            st.dataframe(
                results_df[['scene_number', 'pose_description', 'defect_type', 'result', 'fov']],
                use_container_width=True
            )
            
            # Create Plotly results table
            fig = self.results_visualizer.create_results_table(st.session_state.inspection_results)
            st.plotly_chart(fig, use_container_width=True)
            
            # Summary statistics
            col1, col2, col3, col4 = st.columns(4)
            
            total_scenes = len(st.session_state.inspection_results)
            pass_count = sum(1 for r in st.session_state.inspection_results if r['result'] == 'PASS')
            fail_count = total_scenes - pass_count
            
            with col1:
                st.metric("Total Scenes", total_scenes)
            with col2:
                st.metric("Passed", pass_count)
            with col3:
                st.metric("Failed", fail_count)
            with col4:
                pass_rate = (pass_count / total_scenes * 100) if total_scenes > 0 else 0
                st.metric("Pass Rate", f"{pass_rate:.1f}%")
                
        else:
            st.info("No inspection results available. Run an inspection to see results.")
            
    def _start_inspection(self, part_name: str, inspection_type: str):
        """Start a new inspection."""
        try:
            print(f"DEBUG: GUI starting inspection for {part_name} - {inspection_type}")
            
            if self.orchestrator.start_inspection(part_name, inspection_type):
                st.session_state.inspection_running = True
                st.session_state.current_part = part_name
                st.session_state.current_inspection_type = inspection_type
                st.session_state.inspection_results = []
                st.session_state.current_image = None
                st.session_state.current_arm_positions = None
                
                print(f"DEBUG: GUI set inspection_running=True")
                st.success(f"✅ Inspection started for {part_name} - {inspection_type}")
                
                # Auto-execute first step
                if st.session_state.auto_run:
                    self._execute_next_step()
                    
            else:
                st.error("❌ Failed to start inspection")
                
        except Exception as e:
            st.error(f"❌ Error starting inspection: {str(e)}")
            
    def _execute_next_step(self):
        """Execute the next step in the inspection."""
        try:
            print(f"DEBUG: GUI execute_next_step called, session_state.inspection_running={st.session_state.inspection_running}")
            
            # Double-check that inspection is running
            if not st.session_state.inspection_running:
                st.error("❌ Inspection state lost. Please restart the inspection.")
                return
                
            result = self.orchestrator.execute_next_step()
            
            if result["success"]:
                # Update session state
                st.session_state.inspection_results.append(result["result"])
                st.session_state.current_image = result["image"]
                
                # Update arm positions from the result
                if "arm_positions" in result:
                    st.session_state.current_arm_positions = result["arm_positions"]
                
                # Check if inspection is complete
                status = self.orchestrator.get_inspection_status()
                if not status.get('is_running', False):
                    st.session_state.inspection_running = False
                    st.session_state.auto_run = False
                    st.success("🎉 Inspection completed!")
                    
                # Auto-execute next step if auto-run is enabled
                elif st.session_state.auto_run:
                    time.sleep(1)  # Small delay for visualization
                    st.rerun()
                    
            else:
                st.error(f"❌ Step execution failed: {result['message']}")
                
        except Exception as e:
            st.error(f"❌ Error executing step: {str(e)}")
            # Reset state on error
            st.session_state.inspection_running = False
            
    def _reset_inspection(self):
        """Reset the inspection to initial state."""
        print("DEBUG: GUI resetting inspection")
        self.orchestrator.reset_inspection()
        
        # Reset session state
        st.session_state.inspection_running = False
        st.session_state.current_part = None
        st.session_state.current_inspection_type = None
        st.session_state.inspection_results = []
        st.session_state.current_image = None
        st.session_state.current_arm_positions = None
        st.session_state.auto_run = False
        
        print("DEBUG: GUI reset complete")
        st.info("🔄 Inspection reset to initial state")

    def _emergency_stop(self):
        """Immediately stop all operations."""
        print("DEBUG: GUI emergency stop called")
        self.orchestrator.emergency_stop()
        
        # Reset session state
        st.session_state.inspection_running = False
        st.session_state.current_part = None
        st.session_state.current_inspection_type = None
        st.session_state.inspection_results = []
        st.session_state.current_image = None
        st.session_state.current_arm_positions = None
        st.session_state.auto_run = False
        
        print("DEBUG: GUI emergency stop complete")
        st.info("🛑 Emergency stop complete")

def main():
    """Main entry point for the enhanced GUI."""
    gui = EnhancedInspectionGUI()
    gui.main()
    
if __name__ == "__main__":
    main() 