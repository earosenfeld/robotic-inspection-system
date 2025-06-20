import streamlit as st
import time
import numpy as np
import cv2
from typing import Dict, Any, List
from app.services.inspection_service import InspectionService
from app.utils.plotly_visualization import PlotlyArmVisualizer
from streamlit_plotly_events import plotly_events
from app.utils.inverse_kinematics import solve_ik

# Set page configuration for wider layout
st.set_page_config(
    page_title="Robotic Inspection System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

class InspectionGUI:
    def __init__(self):
        """Initialize the GUI."""
        # Initialize services
        self.inspection_service = InspectionService()
        
        # Initialize Plotly visualizer
        self.arm_visualizer = PlotlyArmVisualizer()
        
        # Initialize session state
        if 'inspection_running' not in st.session_state:
            st.session_state.inspection_running = False
        if 'manual_inspection_running' not in st.session_state:
            st.session_state.manual_inspection_running = False
        if 'current_step' not in st.session_state:
            st.session_state.current_step = 0
        if 'inspection_sequence' not in st.session_state:
            st.session_state.inspection_sequence = None
        if 'results' not in st.session_state:
            st.session_state.results = []
        if 'recorded_poses' not in st.session_state:
            st.session_state.recorded_poses = []
        if 'current_scene' not in st.session_state:
            st.session_state.current_scene = None
        if 'scene_poses' not in st.session_state:
            st.session_state.scene_poses = []
        if 'joint_angles' not in st.session_state:
            st.session_state.joint_angles = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        if 'animation_running' not in st.session_state:
            st.session_state.animation_running = False
        if 'animation_step' not in st.session_state:
            st.session_state.animation_step = 0
        if 'animation_poses' not in st.session_state:
            st.session_state.animation_poses = []
        if 'animation_total' not in st.session_state:
            st.session_state.animation_total = 0
        if 'animation_speed' not in st.session_state:
            st.session_state.animation_speed = 0.1
        if 'auto_play' not in st.session_state:
            st.session_state.auto_play = False
        if 'auto_play_start_step' not in st.session_state:
            st.session_state.auto_play_start_step = 0
            
    def record_current_pose(self):
        """Record the current pose of the robotic arm."""
        try:
            # Get current joint positions
            current_joint_positions = self.inspection_service.arm_controller.arm.get_joint_positions()
            current_end_effector_pose = self.inspection_service.arm_controller.arm.get_end_effector_pose()
            
            # Create pose record
            pose_record = {
                'joint_positions': [pos.tolist() for pos in current_joint_positions],
                'end_effector_position': current_end_effector_pose[0].tolist(),
                'end_effector_orientation': current_end_effector_pose[1].tolist(),
                'timestamp': time.time(),
                'description': f"Pose {len(st.session_state.recorded_poses) + 1}",
                'scene_config': {
                    'inspection_type': 'surface_quality',
                    'view_type': 'custom_view',
                    'lighting': 'standard',
                    'camera_settings': 'default'
                }
            }
            
            st.session_state.recorded_poses.append(pose_record)
            st.success(f"Pose recorded! Total poses: {len(st.session_state.recorded_poses)}")
            
        except Exception as e:
            st.error(f"Failed to record pose: {str(e)}")
    
    def create_inspection_scene(self, scene_name: str, description: str, poses: List[Dict]) -> Dict:
        """Create an inspection scene from recorded poses."""
        return {
            'name': scene_name,
            'description': description,
            'poses': poses,
            'inspection_type': 'custom_scene',
            'created_at': time.time()
        }
    
    def interpolate_poses(self, pose1: Dict, pose2: Dict, num_steps: int = 10) -> List[Dict]:
        """Create smooth interpolation between two poses using IK."""
        interpolated_poses = []
        
        # Get start and end positions
        start_pos = pose1['end_effector_position']
        end_pos = pose2['end_effector_position']
        start_orient = pose1['end_effector_orientation']
        end_orient = pose2['end_effector_orientation']
        
        for i in range(num_steps + 1):
            # Linear interpolation factor
            t = i / num_steps
            
            # Interpolate position
            interp_pos = [
                start_pos[0] + t * (end_pos[0] - start_pos[0]),
                start_pos[1] + t * (end_pos[1] - start_pos[1]),
                start_pos[2] + t * (end_pos[2] - start_pos[2])
            ]
            
            # Interpolate orientation (simple linear interpolation for now)
            interp_orient = [
                start_orient[0] + t * (end_orient[0] - start_orient[0]),
                start_orient[1] + t * (end_orient[1] - start_orient[1]),
                start_orient[2] + t * (end_orient[2] - start_orient[2])
            ]
            
            # Use IK to find joint angles for interpolated position
            if solve_ik(self.inspection_service.arm_controller.arm, interp_pos, interp_orient):
                # Get the resulting joint angles
                joint_angles = self.inspection_service.arm_controller.arm.joint_angles.copy()
                
                # Create interpolated pose
                interp_pose = {
                    'joint_angles': joint_angles.tolist(),
                    'end_effector_position': interp_pos,
                    'end_effector_orientation': interp_orient,
                    'description': f"Interpolated {i}/{num_steps}",
                    'scene_config': pose1.get('scene_config', {}),
                    'timestamp': time.time()
                }
                interpolated_poses.append(interp_pose)
            else:
                # If IK fails, use direct joint interpolation as fallback
                start_angles = pose1.get('joint_angles', [0, 0, 0, 0, 0, 0])
                end_angles = pose2.get('joint_angles', [0, 0, 0, 0, 0, 0])
                
                interp_angles = []
                for j in range(6):
                    interp_angle = start_angles[j] + t * (end_angles[j] - start_angles[j])
                    interp_angles.append(interp_angle)
                
                interp_pose = {
                    'joint_angles': interp_angles,
                    'end_effector_position': interp_pos,
                    'end_effector_orientation': interp_orient,
                    'description': f"Interpolated {i}/{num_steps} (fallback)",
                    'scene_config': pose1.get('scene_config', {}),
                    'timestamp': time.time()
                }
                interpolated_poses.append(interp_pose)
        
        return interpolated_poses
    
    def get_predefined_scenes(self) -> Dict[str, Dict]:
        """Get predefined inspection scenes."""
        return {
            "Top Surface Inspection": {
                "description": "Inspect the top surface of a part for scratches and surface quality",
                "inspection_type": "surface_quality",
                "camera_angles": ["top_view"],
                "lighting": "diffuse"
            },
            "Edge Quality Check": {
                "description": "Check edges for burrs, chips, and finish quality",
                "inspection_type": "edge_quality", 
                "camera_angles": ["front_view", "back_view", "side_view"],
                "lighting": "directional"
            },
            "Fingerprint Detection": {
                "description": "Detect fingerprints and smudges on surfaces",
                "inspection_type": "fingerprints",
                "camera_angles": ["front_view", "back_view"],
                "lighting": "low_angle"
            },
            "Comprehensive Inspection": {
                "description": "Full inspection covering all surfaces and features",
                "inspection_type": "comprehensive",
                "camera_angles": ["top_view", "front_view", "back_view", "side_view"],
                "lighting": "multi_angle"
            }
        }
    
    def get_inspection_types(self) -> List[str]:
        """Get available inspection types."""
        return [
            "surface_quality",
            "scratches_small", 
            "scratches_large",
            "fingerprints",
            "edge_quality",
            "comprehensive",
            "custom_scene"
        ]
    
    def get_view_types(self) -> List[str]:
        """Get available view types."""
        return [
            "top_view",
            "front_view", 
            "back_view",
            "side_view",
            "custom_view",
            "angled_view"
        ]
    
    def get_lighting_options(self) -> List[str]:
        """Get available lighting options."""
        return [
            "standard",
            "diffuse",
            "directional", 
            "low_angle",
            "multi_angle",
            "backlight"
        ]
    
    def main(self):
        """Main GUI loop."""
        st.title("🤖 Robotic Inspection System")
        
        # Create tabs for different modes - only 2 tabs now
        tab1, tab2 = st.tabs(["🎯 Teach-by-Touch & Scenes", "⚙️ Manual Control"])
        
        with tab1:
            self.teach_by_touch_tab()
            
        with tab2:
            self.manual_control_tab()
    
    def teach_by_touch_tab(self):
        """Teach-by-touch pose recording interface with integrated scene-based inspection."""
        st.header("🎯 Teach-by-Touch & Scene-Based Inspection")
        st.markdown("""
        **How it works:**
        1. Move the robot to desired positions manually (gravity-compensated mode)
        2. Record poses by clicking "Record Current Pose"
        3. Create inspection scenes from recorded poses
        4. Save and reuse scenes for different parts
        5. Run scene-based inspections with pose-specific configurations
        """)
        
        # Interactive Arm Control
        st.subheader("🎮 Interactive Arm Control")
        st.markdown("**Drag the sliders to move the robotic arm:**")
        
        # Get current joint angles from the arm
        current_angles = self.inspection_service.arm_controller.arm.joint_angles.copy()
        
        # Initialize session state for joint angles if not exists
        if 'current_joint_angles' not in st.session_state:
            st.session_state.current_joint_angles = current_angles.copy()
        
        # Create sliders for each joint
        col1, col2 = st.columns(2)
        
        with col1:
            # Joint 0 - Base (Yaw)
            joint0_angle = st.slider(
                "Joint 0 (Base) - Yaw", 
                min_value=-3.14, 
                max_value=3.14, 
                value=st.session_state.current_joint_angles[0], 
                step=0.1,
                key="joint0_slider"
            )
            if joint0_angle != st.session_state.current_joint_angles[0]:
                self.update_arm_position(0, joint0_angle)
                st.session_state.current_joint_angles[0] = joint0_angle
            
            # Joint 1 - Shoulder (Pitch)
            joint1_angle = st.slider(
                "Joint 1 (Shoulder) - Pitch", 
                min_value=-1.57, 
                max_value=1.57, 
                value=st.session_state.current_joint_angles[1], 
                step=0.1,
                key="joint1_slider"
            )
            if joint1_angle != st.session_state.current_joint_angles[1]:
                self.update_arm_position(1, joint1_angle)
                st.session_state.current_joint_angles[1] = joint1_angle
            
            # Joint 2 - Elbow (Pitch)
            joint2_angle = st.slider(
                "Joint 2 (Elbow) - Pitch", 
                min_value=-3.14, 
                max_value=3.14, 
                value=st.session_state.current_joint_angles[2], 
                step=0.1,
                key="joint2_slider"
            )
            if joint2_angle != st.session_state.current_joint_angles[2]:
                self.update_arm_position(2, joint2_angle)
                st.session_state.current_joint_angles[2] = joint2_angle
        
        with col2:
            # Joint 3 - Wrist 1 (Roll)
            joint3_angle = st.slider(
                "Joint 3 (Wrist 1) - Roll", 
                min_value=-3.14, 
                max_value=3.14, 
                value=st.session_state.current_joint_angles[3], 
                step=0.1,
                key="joint3_slider"
            )
            if joint3_angle != st.session_state.current_joint_angles[3]:
                self.update_arm_position(3, joint3_angle)
                st.session_state.current_joint_angles[3] = joint3_angle
            
            # Joint 4 - Wrist 2 (Pitch)
            joint4_angle = st.slider(
                "Joint 4 (Wrist 2) - Pitch", 
                min_value=-1.57, 
                max_value=1.57, 
                value=st.session_state.current_joint_angles[4], 
                step=0.1,
                key="joint4_slider"
            )
            if joint4_angle != st.session_state.current_joint_angles[4]:
                self.update_arm_position(4, joint4_angle)
                st.session_state.current_joint_angles[4] = joint4_angle
            
            # Joint 5 - Wrist 3 (Yaw)
            joint5_angle = st.slider(
                "Joint 5 (Wrist 3) - Yaw", 
                min_value=-3.14, 
                max_value=3.14, 
                value=st.session_state.current_joint_angles[5], 
                step=0.1,
                key="joint5_slider"
            )
            if joint5_angle != st.session_state.current_joint_angles[5]:
                self.update_arm_position(5, joint5_angle)
                st.session_state.current_joint_angles[5] = joint5_angle
        
        # Quick preset positions
        st.subheader("⚡ Quick Preset Positions")
        preset_col1, preset_col2, preset_col3, preset_col4 = st.columns(4)
        
        with preset_col1:
            if st.button("🏠 Home Position"):
                # Define home position angles
                home_angles = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                for j, ang in enumerate(home_angles):
                    self.update_arm_position(j, ang)
                    st.session_state.current_joint_angles[j] = ang
                st.success("Arm moved to home position!")
        
        with preset_col2:
            if st.button("⬆️ Top View"):
                top_angles = [0.0, 0.3, 0.5, 0.0, 0.0, 0.0]
                for j, ang in enumerate(top_angles):
                    self.update_arm_position(j, ang)
                    st.session_state.current_joint_angles[j] = ang
                st.success("Arm moved to top view position!")
        
        with preset_col3:
            if st.button("➡️ Front View"):
                front_angles = [0.5, 0.0, 0.3, 0.2, 0.0, 0.0]
                for j, ang in enumerate(front_angles):
                    self.update_arm_position(j, ang)
                    st.session_state.current_joint_angles[j] = ang
                st.success("Arm moved to front view position!")
        
        with preset_col4:
            if st.button("↗️ Side View"):
                side_angles = [1.0, -0.2, 0.4, 0.1, 0.0, 0.0]
                for j, ang in enumerate(side_angles):
                    self.update_arm_position(j, ang)
                    st.session_state.current_joint_angles[j] = ang
                st.success("Arm moved to side view position!")
        
        # Arm Visualization and Pose Recording
        st.subheader("🤖 Arm Visualization & Pose Recording")
        
        # Create a three-column layout: visualization (left), buttons (middle), camera preview (right)
        viz_col, btn_col, cam_col = st.columns([2, 1, 1])
        
        with viz_col:
            # Function to (re)draw the visualization
            def redraw():
                fig_local = self.arm_visualizer.plot_arm(
                    self.inspection_service.arm_controller.arm.get_joint_positions()
                )
                return fig_local

            # Create the figure to display
            fig = redraw()
            
            # Use plotly_events to display the chart and capture clicks
            st.write("**🖱️ Click on the visualization end-effector sphere to move the arm:**")
            selected_points = plotly_events(
                fig,
                click_event=True,
                hover_event=False,
                select_event=False,
                key="arm_click_events_main",
                override_height=400,
                override_width="100%"
            )
            
            # Handle click event ➜ move arm via IK
            if selected_points and all(k in selected_points[0] for k in ("x", "y", "z")):
                pt = selected_points[0]
                target_pos = [pt['x'], pt['y'], pt['z']]
                _, current_orient = self.inspection_service.arm_controller.arm.get_end_effector_pose()
                
                if solve_ik(self.inspection_service.arm_controller.arm, target_pos, current_orient.tolist()):
                    # Update session state with new joint angles from IK
                    new_angles = self.inspection_service.arm_controller.arm.joint_angles.copy()
                    for j, angle in enumerate(new_angles):
                        st.session_state.current_joint_angles[j] = angle
                    st.success(f"Arm moved to clicked position (X={target_pos[0]:.2f}, Y={target_pos[1]:.2f}, Z={target_pos[2]:.2f})")
                    st.rerun() # Rerun to reflect the new position immediately
                else:
                    st.warning("Could not reach clicked position – try another location.")
            
            # Camera controls
            st.write("**📷 Camera Controls:**")
            cam_col1, cam_col2, cam_col3, cam_col4 = st.columns(4)
            
            with cam_col1:
                if st.button("👁️ Front View", key="cam_front"):
                    self.arm_visualizer.fig.update_scenes(
                        camera=dict(eye=dict(x=0, y=-2, z=0.5))
                    )
                    st.rerun()
            
            with cam_col2:
                if st.button("👁️ Side View", key="cam_side"):
                    self.arm_visualizer.fig.update_scenes(
                        camera=dict(eye=dict(x=2, y=0, z=0.5))
                    )
                    st.rerun()
            
            with cam_col3:
                if st.button("👁️ Top View", key="cam_top"):
                    self.arm_visualizer.fig.update_scenes(
                        camera=dict(eye=dict(x=0, y=0, z=2))
                    )
                    st.rerun()
            
            with cam_col4:
                if st.button("👁️ Isometric", key="cam_iso"):
                    self.arm_visualizer.fig.update_scenes(
                        camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
                    )
                    st.rerun()
            
            # Click instructions
            st.info("💡 **Tip:** Use the sliders above to move the arm, then click '📸 Record Current Pose' to save the position!")
            
            # Add refresh button for visualization
            if st.button("🔄 Refresh Visualization", key="refresh_viz_main"):
                st.rerun()
            
            # Coordinate-based positioning
            st.write("**🎯 Direct Position Control:**")
            pos_col1, pos_col2 = st.columns(2)
            
            with pos_col1:
                st.write("**End Effector Position:**")
                target_x = st.number_input("X Position:", value=0.0, step=0.1, key="target_x")
                target_y = st.number_input("Y Position:", value=0.0, step=0.1, key="target_y")
                target_z = st.number_input("Z Position:", value=0.5, step=0.1, key="target_z")
                
                if st.button("🎯 Move to Position", key="move_to_pos"):
                    target_pos = [target_x, target_y, target_z]
                    # Keep current orientation
                    _, current_orient = self.inspection_service.arm_controller.arm.get_end_effector_pose()
                    if solve_ik(self.inspection_service.arm_controller.arm, target_pos, current_orient.tolist()):
                        # Update session state with new joint angles
                        new_angles = self.inspection_service.arm_controller.arm.joint_angles.copy()
                        for j, angle in enumerate(new_angles):
                            st.session_state.current_joint_angles[j] = angle
                        st.success("Arm moved to target position!")
                    else:
                        st.error("Could not reach target position - try a different position.")
            
            with pos_col2:
                st.write("**Current Position:**")
                current_pos, current_orient = self.inspection_service.arm_controller.arm.get_end_effector_pose()
                st.write(f"X: {current_pos[0]:.3f}")
                st.write(f"Y: {current_pos[1]:.3f}")
                st.write(f"Z: {current_pos[2]:.3f}")
                st.write(f"Roll: {current_orient[0]:.3f}")
                st.write(f"Pitch: {current_orient[1]:.3f}")
                st.write(f"Yaw: {current_orient[2]:.3f}")
            
            # Display current arm status
            st.write("**📊 Arm Status:**")
            
            # Animation controls - moved here to be with the visualization
            if st.session_state.get('animation_running', False):
                st.subheader("🎬 Smooth Scene Animation in Progress")
                
                # Handle automatic smooth playback
                if st.session_state.get('auto_play', False):
                    # Auto-advance animation step for smooth playback
                    if st.session_state.animation_step < st.session_state.animation_total - 1:
                        st.session_state.animation_step += 1
                        st.rerun()
                    else:
                        # Animation complete
                        st.session_state.auto_play = False
                        st.session_state.animation_running = False
                        st.success("🎉 Automatic smooth animation completed!")
                        st.rerun()
                
                # Progress bar
                progress = st.session_state.animation_step / st.session_state.animation_total
                st.progress(progress)
                
                # Current pose info
                if st.session_state.animation_step < st.session_state.animation_total:
                    current_pose = st.session_state.animation_poses[st.session_state.animation_step]
                    
                    # Calculate which original pose we're closest to
                    original_pose_count = len(st.session_state.recorded_poses)
                    interpolated_steps_per_pose = 8
                    
                    # Calculate which original pose this step corresponds to
                    if st.session_state.animation_step == 0:
                        current_original_pose = 1
                        step_type = "Original Pose"
                    else:
                        # For interpolated steps, calculate which original pose we're between
                        step_in_sequence = st.session_state.animation_step
                        original_pose_index = step_in_sequence // (interpolated_steps_per_pose + 1)
                        current_original_pose = original_pose_index + 1
                        
                        # Determine if this is an original pose or interpolated step
                        if step_in_sequence % (interpolated_steps_per_pose + 1) == 0:
                            step_type = "Original Pose"
                        else:
                            step_type = "Interpolated Step"
                    
                    st.write(f"**Current Step:** {st.session_state.animation_step + 1}/{st.session_state.animation_total}")
                    st.write(f"**Step Type:** {step_type}")
                    st.write(f"**Original Pose:** {current_original_pose}/{original_pose_count}")
                    st.write(f"**Description:** {current_pose['description']}")
                    
                    # Move arm to current pose
                    for j, angle in enumerate(current_pose.get('joint_angles', [])):
                        self.inspection_service.arm_controller.arm.move_joint(j, angle)
                        st.session_state.current_joint_angles[j] = angle
                    
                    # Show current arm position
                    current_pos, current_orient = self.inspection_service.arm_controller.arm.get_end_effector_pose()
                    st.write(f"**🤖 Current Arm Position:** X={current_pos[0]:.3f}, Y={current_pos[1]:.3f}, Z={current_pos[2]:.3f}")
                    
                    # Show pose configuration
                    scene_config = current_pose.get('scene_config', {})
                    st.write(f"**Inspection Type:** {scene_config.get('inspection_type', 'unknown')}")
                    st.write(f"**View Type:** {scene_config.get('view_type', 'unknown')}")
                    st.write(f"**Lighting:** {scene_config.get('lighting', 'unknown')}")
                    
                    # Add a note about smooth motion
                    st.info("💡 **Smooth Motion:** The arm is moving through interpolated poses for fluid animation!")
                    
                    # Control buttons
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if st.button("⏭️ Next Step", key="next_pose"):
                            st.session_state.animation_step += 1
                            if st.session_state.animation_step >= st.session_state.animation_total:
                                st.session_state.animation_running = False
                                st.success("🎉 Smooth animation completed!")
                            st.rerun()
                    
                    with col2:
                        if st.button("⏸️ Pause Animation", key="pause_animation"):
                            st.session_state.animation_running = False
                            st.info("Animation paused")
                    
                    with col3:
                        if st.button("🔄 Restart Animation", key="restart_animation"):
                            st.session_state.animation_step = 0
                            st.rerun()
                    
                    with col4:
                        if st.button("▶️ Play All Smooth", key="play_all_smooth"):
                            # Start automatic smooth playback
                            st.session_state.auto_play = True
                            st.session_state.auto_play_start_step = st.session_state.animation_step
                            st.info("Starting automatic smooth playback...")
                            st.rerun()
                    
                    # Add refresh visualization button
                    if st.button("🔄 Refresh Visualization", key="refresh_viz"):
                        st.rerun()
                else:
                    st.success("🎉 Smooth animation completed!")
                    st.session_state.animation_running = False
                    # Show final summary
                    st.write("**📊 Smooth Animation Summary:**")
                    original_poses = st.session_state.recorded_poses
                    for i, pose in enumerate(original_poses):
                        scene_config = pose.get('scene_config', {})
                        st.write(f"✅ Original Pose {i+1}: {pose['description']} - {scene_config.get('inspection_type', 'unknown')}")
                    st.write(f"🎬 **Total interpolated steps:** {st.session_state.animation_total}")
                    st.write(f"🎯 **Smooth motion achieved with IK interpolation!**")
        
        with btn_col:
            # -----------------------
            # 📸 Pose Recording & Scene Testing
            # -----------------------
            st.subheader("📸 Pose Recording")
            
            # Scene configuration for the pose to be recorded
            st.markdown("**Configure scene settings:**")
            
            inspection_type = st.selectbox(
                "Inspection Type:",
                self.get_inspection_types(),
                key="pose_inspection_type"
            )
            
            view_type = st.selectbox(
                "View Type:",
                self.get_view_types(),
                key="pose_view_type"
            )
            
            lighting = st.selectbox(
                "Lighting:",
                self.get_lighting_options(),
                key="pose_lighting"
            )
            
            camera_settings = st.selectbox(
                "Camera Settings:",
                ["default", "high_resolution", "low_resolution", "wide_angle", "telephoto"],
                key="pose_camera_settings"
            )
            
            # Pose description
            pose_description = st.text_input(
                "Pose Description:",
                value=f"Pose {len(st.session_state.recorded_poses) + 1}",
                key="pose_description"
            )
            
            # Record pose button
            if st.button("📸 Record Current Pose", type="primary"):
                # Get current joint angles
                current_joint_angles = self.inspection_service.arm_controller.arm.joint_angles.copy()
                current_joint_positions = self.inspection_service.arm_controller.arm.get_joint_positions()
                current_end_effector_pose = self.inspection_service.arm_controller.arm.get_end_effector_pose()
                
                # Create pose record with scene configuration and joint angles
                pose_record = {
                    'joint_positions': [pos.tolist() for pos in current_joint_positions],
                    'joint_angles': current_joint_angles.tolist(),
                    'end_effector_position': current_end_effector_pose[0].tolist(),
                    'end_effector_orientation': current_end_effector_pose[1].tolist(),
                    'timestamp': time.time(),
                    'description': pose_description,
                    'scene_config': {
                        'inspection_type': inspection_type,
                        'view_type': view_type,
                        'lighting': lighting,
                        'camera_settings': camera_settings
                    }
                }
                
                st.session_state.recorded_poses.append(pose_record)
                st.success(f"Pose recorded! Total: {len(st.session_state.recorded_poses)}")
                st.rerun()
            
            st.write("---")
            st.write("**🧪 Scene Testing:**")
            if st.button("🧪 Test Complete Scene"):
                if len(st.session_state.recorded_poses) > 0:
                    # Create smooth interpolated animation sequence
                    smooth_poses = []
                    
                    # Add first pose
                    smooth_poses.append(st.session_state.recorded_poses[0])
                    
                    # Add interpolated poses between each recorded pose
                    for i in range(len(st.session_state.recorded_poses) - 1):
                        pose1 = st.session_state.recorded_poses[i]
                        pose2 = st.session_state.recorded_poses[i + 1]
                        
                        # Create 8 interpolated steps between poses for smooth motion
                        interpolated = self.interpolate_poses(pose1, pose2, num_steps=8)
                        smooth_poses.extend(interpolated[1:])  # Skip first to avoid duplicate
                    
                    # Start the smooth animation
                    st.session_state.animation_running = True
                    st.session_state.animation_step = 0
                    st.session_state.animation_poses = smooth_poses
                    st.session_state.animation_total = len(smooth_poses)
                    st.session_state.animation_speed = 0.1  # 100ms between steps
                    
                    # Calculate step information for display
                    original_pose_count = len(st.session_state.recorded_poses)
                    interpolated_steps_per_pose = 8
                    total_interpolated_steps = (original_pose_count - 1) * interpolated_steps_per_pose + original_pose_count
                    
                    st.info(f"🎬 **Animation Started:** {original_pose_count} original poses → {total_interpolated_steps} smooth steps")
                    st.rerun()
                else:
                    st.error("No poses recorded yet!")
            
            st.write("---")
            st.write("**Quick Actions:**")
            if st.button("🗑️ Clear All Poses"):
                st.session_state.recorded_poses = []
                st.success("All poses cleared!")
            
            if st.button("🔄 Reset Arm"):
                # Define a visible home pose (slightly raised)
                home_angles = [0.0, -0.4, 0.8, 0.0, 0.0, 0.0]
                for j, ang in enumerate(home_angles):
                    self.update_arm_position(j, ang)
                    st.session_state.current_joint_angles[j] = ang
                st.success("Arm moved to home position!")
        
        with cam_col:
            # -----------------------
            # 📷 Camera Preview (mock image)
            # -----------------------
            st.subheader("📷 Camera View")

            def get_camera_preview():
                cam_pos, cam_orient = self.inspection_service.arm_controller.arm.get_end_effector_pose()
                scene_desc = {'type': 'random'}
                img, _ = self.inspection_service.camera_controller.capture_image(cam_pos, cam_orient, scene_desc)
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                return img_rgb

            if 'preview_img' not in st.session_state:
                st.session_state.preview_img = get_camera_preview()

            st.image(st.session_state.preview_img, caption="Mock camera view", use_container_width=True)

            if st.button("🔄 Refresh Camera View", key="refresh_cam_view"):
                st.session_state.preview_img = get_camera_preview()
                st.rerun()

            # Display recorded poses
            st.subheader("📋 Recorded Poses")
            if st.session_state.recorded_poses:
                for i, pose in enumerate(st.session_state.recorded_poses):
                    with st.expander(f"Pose {i+1}: {pose['description']}"):
                        # Pose information
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**End Effector Position:**")
                            st.code(f"X: {pose['end_effector_position'][0]:.3f}")
                            st.code(f"Y: {pose['end_effector_position'][1]:.3f}")
                            st.code(f"Z: {pose['end_effector_position'][2]:.3f}")
                        with col2:
                            st.write("**End Effector Orientation:**")
                            st.code(f"Roll: {pose['end_effector_orientation'][0]:.3f}")
                            st.code(f"Pitch: {pose['end_effector_orientation'][1]:.3f}")
                            st.code(f"Yaw: {pose['end_effector_orientation'][2]:.3f}")
                        
                        # Scene configuration display and editing
                        st.write("**Scene Configuration:**")
                        scene_config = pose.get('scene_config', {})
                        
                        # Allow editing scene configuration
                        edit_col1, edit_col2 = st.columns(2)
                        
                        with edit_col1:
                            new_inspection_type = st.selectbox(
                                f"Inspection Type:",
                                self.get_inspection_types(),
                                index=self.get_inspection_types().index(scene_config.get('inspection_type', 'surface_quality')),
                                key=f"edit_inspection_{i}"
                            )
                            
                            new_view_type = st.selectbox(
                                f"View Type:",
                                self.get_view_types(),
                                index=self.get_view_types().index(scene_config.get('view_type', 'custom_view')),
                                key=f"edit_view_{i}"
                            )
                        
                        with edit_col2:
                            new_lighting = st.selectbox(
                                f"Lighting:",
                                self.get_lighting_options(),
                                index=self.get_lighting_options().index(scene_config.get('lighting', 'standard')),
                                key=f"edit_lighting_{i}"
                            )
                            
                            new_camera_settings = st.selectbox(
                                f"Camera Settings:",
                                ["default", "high_resolution", "low_resolution", "wide_angle", "telephoto"],
                                index=["default", "high_resolution", "low_resolution", "wide_angle", "telephoto"].index(scene_config.get('camera_settings', 'default')),
                                key=f"edit_camera_{i}"
                            )
                        
                        # Update scene configuration if changed
                        if (new_inspection_type != scene_config.get('inspection_type') or
                            new_view_type != scene_config.get('view_type') or
                            new_lighting != scene_config.get('lighting') or
                            new_camera_settings != scene_config.get('camera_settings')):
                            
                            pose['scene_config'] = {
                                'inspection_type': new_inspection_type,
                                'view_type': new_view_type,
                                'lighting': new_lighting,
                                'camera_settings': new_camera_settings
                            }
                            st.success("Scene configuration updated!")
                        
                        # Allow editing description
                        new_desc = st.text_input(f"Description for Pose {i+1}:", value=pose['description'], key=f"desc_{i}")
                        if new_desc != pose['description']:
                            pose['description'] = new_desc
                        
                        # Action buttons
                        action_col1, action_col2, action_col3 = st.columns(3)
                        
                        with action_col1:
                            if st.button(f"🎯 Move to Pose {i+1}", key=f"move_to_pose_{i}"):
                                # Move arm to recorded joint positions
                                for j, angle in enumerate(pose.get('joint_angles', [])):
                                    self.update_arm_position(j, angle)
                                    st.session_state.current_joint_angles[j] = angle
                                st.success(f"Arm moved to Pose {i+1}!")
                        
                        with action_col2:
                            if st.button(f"🔍 Test Scene {i+1}", key=f"test_scene_{i}"):
                                # Create a single-pose scene for testing
                                test_scene = {
                                    'name': f"Test Scene - {pose['description']}",
                                    'description': f"Test scene for pose {i+1}",
                                    'poses': [pose],
                                    'inspection_type': pose['scene_config']['inspection_type'],
                                    'created_at': time.time()
                                }
                                
                                # Start test inspection
                                if self.inspection_service.start_inspection_from_custom_scene("Medium Part", test_scene):
                                    if self.inspection_service.execute_step():
                                        result = self.inspection_service.results[-1]
                                        st.success(f"Scene test completed: {result['result']['status']}")
                                        if result['result']['defects']:
                                            st.warning(f"Defects found: {result['result']['defects']}")
                                    else:
                                        st.error("Scene test failed")
                                else:
                                    st.error("Failed to start scene test")
                        
                        with action_col3:
                            if st.button(f"🗑️ Delete Pose {i+1}", key=f"delete_pose_{i}"):
                                st.session_state.recorded_poses.pop(i)
                                st.success(f"Pose {i+1} deleted!")
                                st.rerun()
            else:
                st.info("No poses recorded yet. Move the arm, configure scene settings, and click 'Record Current Pose' to get started!")
            
            # Scene creation from recorded poses
            if len(st.session_state.recorded_poses) >= 1:
                st.subheader("🎬 Create Inspection Scene")
                
                # Scene configuration summary
                st.markdown("**Scene Configuration Summary:**")
                scene_summary = {}
                for i, pose in enumerate(st.session_state.recorded_poses):
                    scene_config = pose.get('scene_config', {})
                    inspection_type = scene_config.get('inspection_type', 'surface_quality')
                    view_type = scene_config.get('view_type', 'custom_view')
                    lighting = scene_config.get('lighting', 'standard')
                    
                    if inspection_type not in scene_summary:
                        scene_summary[inspection_type] = {'poses': 0, 'view_types': set(), 'lighting': set()}
                    
                    scene_summary[inspection_type]['poses'] += 1
                    scene_summary[inspection_type]['view_types'].add(view_type)
                    scene_summary[inspection_type]['lighting'].add(lighting)
                
                # Display summary
                for inspection_type, summary in scene_summary.items():
                    st.write(f"**{inspection_type}**: {summary['poses']} poses, "
                            f"Views: {', '.join(summary['view_types'])}, "
                            f"Lighting: {', '.join(summary['lighting'])}")
                
                # Scene creation options
                scene_name = st.text_input("Scene Name:", placeholder="e.g., Comprehensive Part Inspection")
                scene_description = st.text_area("Scene Description:", placeholder="Describe what this scene inspects...")
                
                # Scene type selection
                scene_type = st.selectbox(
                    "Scene Type:",
                    ["custom_scene", "surface_quality", "comprehensive", "edge_quality", "fingerprint_detection"],
                    help="Choose how the scene should be processed"
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🎬 Create Scene from Poses") and scene_name:
                        scene = self.create_inspection_scene(scene_name, scene_description, st.session_state.recorded_poses.copy())
                        scene['scene_type'] = scene_type
                        
                        if 'saved_scenes' not in st.session_state:
                            st.session_state.saved_scenes = []
                        st.session_state.saved_scenes.append(scene)
                        st.success(f"Scene '{scene_name}' created successfully!")
                
                with col2:
                    if st.button("📋 View Scene Summary"):
                        if len(st.session_state.recorded_poses) > 0:
                            st.write("**Scene Summary:**")
                            st.write(f"Total poses: {len(st.session_state.recorded_poses)}")
                            st.write(f"Scene type: {scene_type}")
                            st.write(f"Description: {scene_description}")
                            
                            # Show pose details
                            for i, pose in enumerate(st.session_state.recorded_poses):
                                scene_config = pose.get('scene_config', {})
                                st.write(f"  Pose {i+1}: {pose['description']} - "
                                        f"{scene_config.get('inspection_type', 'unknown')} - "
                                        f"{scene_config.get('view_type', 'unknown')}")
                        else:
                            st.error("No poses to summarize")
            
            # Display saved scenes
            if 'saved_scenes' in st.session_state and st.session_state.saved_scenes:
                st.subheader("💾 Saved Scenes")
                for i, scene in enumerate(st.session_state.saved_scenes):
                    with st.expander(f"Scene: {scene['name']}"):
                        st.write(f"**Description:** {scene['description']}")
                        st.write(f"**Poses:** {len(scene['poses'])}")
                        st.write(f"**Scene Type:** {scene.get('scene_type', 'custom_scene')}")
                        st.write(f"**Created:** {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(scene['created_at']))}")
                        
                        # Show pose details
                        st.write("**Pose Details:**")
                        for j, pose in enumerate(scene['poses']):
                            scene_config = pose.get('scene_config', {})
                            st.write(f"  Pose {j+1}: {pose['description']} - "
                                    f"{scene_config.get('inspection_type', 'unknown')} - "
                                    f"{scene_config.get('view_type', 'unknown')}")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if st.button(f"▶️ Use Scene", key=f"use_scene_{i}"):
                                st.session_state.current_scene = scene
                                st.session_state.scene_poses = scene['poses']
                                st.success(f"Scene '{scene['name']}' loaded!")
                        
                        with col2:
                            if st.button(f"🧪 Test Scene", key=f"test_saved_scene_{i}"):
                                if self.inspection_service.start_inspection_from_custom_scene("Medium Part", scene):
                                    st.success(f"Scene '{scene['name']}' test started!")
                                    # Execute first step as preview
                                    if self.inspection_service.execute_step():
                                        result = self.inspection_service.results[-1]
                                        st.success(f"Preview: {result['result']['status']}")
                                    else:
                                        st.error("Scene test failed")
                                else:
                                    st.error("Failed to start scene test")
                        
                        with col3:
                            if st.button(f"🗑️ Delete Scene", key=f"delete_scene_{i}"):
                                st.session_state.saved_scenes.pop(i)
                                st.success("Scene deleted!")
                                st.rerun()
            
            # Scene-based inspection execution
            if st.session_state.current_scene:
                st.subheader("🔍 Scene-Based Inspection")
                st.write(f"**Current Scene:** {st.session_state.current_scene['name']}")
                st.write(f"**Description:** {st.session_state.current_scene['description']}")
                st.write(f"**Poses:** {len(st.session_state.scene_poses)}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("▶️ Start Scene Inspection"):
                        part_type = st.selectbox("Select Part Type:", self.inspection_service.get_available_parts(), key="scene_part")
                        if self.inspection_service.start_inspection_from_custom_scene(part_type, st.session_state.current_scene):
                            st.session_state.inspection_running = True
                            st.session_state.current_step = 0
                            st.session_state.inspection_sequence = self.inspection_service.inspection_sequence
                            st.session_state.results = []
                            st.success("Scene inspection started!")
                        else:
                            st.error("Failed to start scene inspection")
                
                with col2:
                    if st.button("🗑️ Clear Current Scene"):
                        st.session_state.current_scene = None
                        st.session_state.scene_poses = []
                        st.success("Current scene cleared!")
            
            # Inspection execution
            if st.session_state.inspection_running:
                st.subheader("⚡ Execute Inspection")
                if st.button("▶️ Execute Next Step"):
                    if self.inspection_service.execute_step():
                        st.success("Step executed successfully")
                        st.session_state.current_step = self.inspection_service.current_step
                        st.session_state.results = self.inspection_service.results
                        if st.session_state.current_step >= len(st.session_state.inspection_sequence):
                            st.session_state.inspection_running = False
                            st.success("Inspection completed!")
                    else:
                        st.error("Failed to execute step")
            
            # Display current inspection status
            if st.session_state.inspection_running and st.session_state.inspection_sequence:
                st.subheader("📊 Current Inspection Status")
                total_steps = len(st.session_state.inspection_sequence)
                current_step = st.session_state.current_step
                st.write(f"Step {current_step + 1} of {total_steps}")
                
                if current_step < total_steps:
                    current_step_info = st.session_state.inspection_sequence[current_step]
                    st.write(f"**Current Step:** {current_step_info['type']}")
                    st.write(f"**Position:** {current_step_info['position']}")
                    st.write(f"**Description:** {current_step_info['description']}")
            
            # Display results
            if st.session_state.results:
                st.subheader("📋 Inspection Results")
                for result in st.session_state.results:
                    st.write(f"Step {result['step'] + 1}: {result.get('description', result['type'])} - {result['result']['status']}")
                    if result['result']['defects']:
                        st.write(f"   Defects: {result['result']['defects']}")

    def manual_control_tab(self):
        """Manual control interface (original functionality)."""
        st.header("⚙️ Manual Control")
        st.markdown("Traditional manual control interface for debugging and testing.")
        
        # Part and inspection type selection
        part_type = st.selectbox(
            "Select Part Type",
            self.inspection_service.get_available_parts(),
            key="part_type_select_manual"
        )
        
        inspection_types = {
            "Small Part": ["scratches_small", "fingerprints"],
            "Medium Part": ["scratches_large", "fingerprints", "surface_quality"],
            "Large Part": ["scratches_large", "fingerprints", "surface_quality", "edge_quality"]
        }
        
        inspection_type = st.selectbox(
            "Select Inspection Type",
            inspection_types[part_type],
            key="inspection_type_select_manual"
        )
        
        # Control buttons
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Start Manual Inspection"):
                # Use separate service instance for manual control
                manual_service = InspectionService()
                if manual_service.start_inspection(part_type, inspection_type):
                    st.session_state.manual_inspection_running = True
                    st.session_state.manual_current_step = 0
                    st.session_state.manual_inspection_sequence = manual_service.inspection_sequence
                    st.session_state.manual_results = []
                    st.session_state.manual_service = manual_service
                    st.success("Manual inspection started successfully!")
                else:
                    st.error("Failed to start manual inspection")
        
        with col2:
            if st.button("Execute Manual Step"):
                if st.session_state.manual_inspection_running and hasattr(st.session_state, 'manual_service'):
                    manual_service = st.session_state.manual_service
                    if manual_service.execute_step():
                        st.success("Manual step executed successfully")
                        st.session_state.manual_current_step = manual_service.current_step
                        st.session_state.manual_results = manual_service.results
                        if st.session_state.manual_current_step >= len(manual_service.inspection_sequence):
                            st.session_state.manual_inspection_running = False
                            st.success("Manual inspection completed!")
                    else:
                        st.error("Failed to execute manual step")
                else:
                    st.error("No manual inspection running - please start an inspection first")
        
        # Display inspection progress and results
        if st.session_state.manual_inspection_running and hasattr(st.session_state, 'manual_service'):
            st.subheader("📊 Manual Inspection Progress")
            manual_service = st.session_state.manual_service
            total_steps = len(manual_service.inspection_sequence)
            current_step = manual_service.current_step
            st.write(f"Step {current_step + 1} of {total_steps}")
            
            if current_step < total_steps:
                current_step_info = manual_service.inspection_sequence[current_step]
                st.write(f"**Current Step:** {current_step_info['type']}")
                st.write(f"**Position:** {current_step_info['position']}")
                st.write(f"**Description:** {current_step_info['description']}")
        
        # Display results
        if hasattr(st.session_state, 'manual_results') and st.session_state.manual_results:
            st.subheader("📋 Manual Inspection Results")
            for result in st.session_state.manual_results:
                st.write(f"Step {result['step'] + 1}: {result['type']} - {result['result']}")
        
        # Manual arm control for testing
        st.subheader("🎮 Manual Arm Control")
        st.markdown("**Direct joint control for testing:**")
        
        # Get current joint angles
        current_angles = self.inspection_service.arm_controller.arm.joint_angles.copy()
        
        # Manual joint sliders
        col1, col2 = st.columns(2)
        
        with col1:
            manual_joint0 = st.slider(
                "Manual Joint 0", 
                min_value=-3.14, 
                max_value=3.14, 
                value=current_angles[0], 
                step=0.1,
                key="manual_joint0"
            )
            if manual_joint0 != current_angles[0]:
                self.update_arm_position(0, manual_joint0)
            
            manual_joint1 = st.slider(
                "Manual Joint 1", 
                min_value=-1.57, 
                max_value=1.57, 
                value=current_angles[1], 
                step=0.1,
                key="manual_joint1"
            )
            if manual_joint1 != current_angles[1]:
                self.update_arm_position(1, manual_joint1)
            
            manual_joint2 = st.slider(
                "Manual Joint 2", 
                min_value=-3.14, 
                max_value=3.14, 
                value=current_angles[2], 
                step=0.1,
                key="manual_joint2"
            )
            if manual_joint2 != current_angles[2]:
                self.update_arm_position(2, manual_joint2)
        
        with col2:
            manual_joint3 = st.slider(
                "Manual Joint 3", 
                min_value=-3.14, 
                max_value=3.14, 
                value=current_angles[3], 
                step=0.1,
                key="manual_joint3"
            )
            if manual_joint3 != current_angles[3]:
                self.update_arm_position(3, manual_joint3)
            
            manual_joint4 = st.slider(
                "Manual Joint 4", 
                min_value=-1.57, 
                max_value=1.57, 
                value=current_angles[4], 
                step=0.1,
                key="manual_joint4"
            )
            if manual_joint4 != current_angles[4]:
                self.update_arm_position(4, manual_joint4)
            
            manual_joint5 = st.slider(
                "Manual Joint 5", 
                min_value=-3.14, 
                max_value=3.14, 
                value=current_angles[5], 
                step=0.1,
                key="manual_joint5"
            )
            if manual_joint5 != current_angles[5]:
                self.update_arm_position(5, manual_joint5)
    
    def update_arm_position(self, joint_index: int, angle: float):
        """Update the arm position by moving a specific joint."""
        try:
            if self.inspection_service.arm_controller.arm.move_joint(joint_index, angle):
                st.session_state.current_joint_angles[joint_index] = angle
                return True
            else:
                st.error(f"Failed to move joint {joint_index} to angle {angle}")
                return False
        except Exception as e:
            st.error(f"Error updating arm position: {str(e)}")
            return False

def main():
    """Main entry point for the GUI."""
    gui = InspectionGUI()
    gui.main()
    
if __name__ == "__main__":
    main() 