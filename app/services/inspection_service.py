import json
import time
from typing import Dict, List, Any, Optional
import numpy as np
from pathlib import Path
import os
from datetime import datetime

from app.models.robotic_arm import RoboticArm
from app.models.camera import Camera
from app.models.safety_system import SafetySystem
from app.controllers.robotic_arm_controller import RoboticArmController
from app.controllers.camera_controller import CameraController
from app.controllers.safety_controller import SafetyController
from app.config.camera_config import calculate_inspection_grid, CAMERA_CONFIG

class InspectionService:
    """Service for coordinating inspection operations."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the inspection service.
        
        Args:
            config_path: Path to inspection configuration file
        """
        # Set default config path if none provided
        if config_path is None:
            self.config_path = Path("data/configs/parts_inspection_config.json")
        else:
            self.config_path = config_path
            
        # Initialize models
        self.arm = RoboticArm()
        self.camera = Camera()
        self.safety_system = SafetySystem()
        
        # Initialize controllers
        self.arm_controller = RoboticArmController(self.arm)
        self.camera_controller = CameraController(self.camera)
        self.safety_controller = SafetyController(self.safety_system)
        
        # Initialize inspection state
        self.inspection_sequence = None
        self.current_step = 0
        self.results = []
        
        # Load configuration
        self._load_config()
        
    def _load_config(self):
        """Load or create default configuration."""
        self.config = {
            "Small Part": {
                "dimensions": {
                    "length": 100,  # mm
                    "width": 100,   # mm
                    "height": 50    # mm
                },
                "inspection_types": ["scratches_small", "fingerprints"]
            },
            "Medium Part": {
                "dimensions": {
                    "length": 200,  # mm
                    "width": 200,   # mm
                    "height": 100   # mm
                },
                "inspection_types": ["scratches_large", "surface_quality"]
            },
            "Large Part": {
                "dimensions": {
                    "length": 500,  # mm
                    "width": 500,   # mm
                    "height": 200   # mm
                },
                "inspection_types": ["edge_quality", "surface_quality", "scratches_large"]
            }
        }
        
        try:
            # Create config directory if it doesn't exist
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save default config to file
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
                
        except Exception as e:
            print(f"Error saving config: {str(e)}")
            # Continue with in-memory config if file save fails
        
    def get_available_parts(self) -> List[str]:
        """Get list of available parts for inspection."""
        return list(self.config.keys())
    
    def get_part_scenes(self, part_id: str) -> List[Dict[str, Any]]:
        """Get list of inspection scenes for a part."""
        if part_id in self.config:
            return self.config[part_id]["inspection_points"]
        return []
    
    def start_inspection(self, part_type: str, inspection_type: str) -> bool:
        """
        Start a new inspection sequence.
        
        Args:
            part_type: Type of part to inspect
            inspection_type: Type of inspection to perform
            
        Returns:
            bool: True if inspection started successfully
        """
        try:
            # Check safety status
            if not self.arm_controller.check_safety_status():
                print("Safety check failed - cannot start inspection")
                return False
                
            # Validate part type and inspection type
            if part_type not in self.config:
                raise ValueError(f"Unknown part type: {part_type}")
                
            if inspection_type not in self.config[part_type]["inspection_types"]:
                raise ValueError(f"Invalid inspection type {inspection_type} for part {part_type}")
            
            # Get part dimensions
            part_dimensions = self.config[part_type]["dimensions"]
            
            # Calculate inspection points based on part dimensions and camera specs
            inspection_points = calculate_inspection_grid(part_dimensions, CAMERA_CONFIG)
            
            # Filter inspection points based on inspection type
            if inspection_type == "scratches_small":
                # For small scratches, we need high-resolution top views
                self.inspection_sequence = [p for p in inspection_points if p["type"] == "top_view"]
            elif inspection_type == "scratches_large":
                # For large scratches, we can use fewer points with wider spacing
                self.inspection_sequence = [p for p in inspection_points if p["type"] in ["top_view", "front_view", "back_view"]]
            elif inspection_type == "fingerprints":
                # For fingerprints, we need good lighting angles
                self.inspection_sequence = [p for p in inspection_points if p["type"] in ["front_view", "back_view"]]
            elif inspection_type == "surface_quality":
                # For surface quality, we need comprehensive coverage
                self.inspection_sequence = inspection_points
            elif inspection_type == "edge_quality":
                # For edge quality, we focus on the edges
                self.inspection_sequence = [p for p in inspection_points if p["type"] in ["front_view", "back_view"]]
            
            print(f"Starting inspection for part: {part_type}, type: {inspection_type}")
            print(f"Inspection sequence created with {len(self.inspection_sequence)} steps")
            print(f"Inspection sequence: {self.inspection_sequence}")
            
            self.current_step = 0
            self.results = []
            self.inspection_type = inspection_type  # Store for use in execute_step
            return True
            
        except Exception as e:
            print(f"Error starting inspection: {str(e)}")
            return False
        
    def execute_step(self) -> bool:
        """
        Execute the current inspection step.
        
        Returns:
            bool: True if step was executed successfully
        """
        try:
            print("\n=== Execute Step Debug Info ===")
            print(f"Current step index: {self.current_step}")
            print(f"Inspection sequence exists: {self.inspection_sequence is not None}")
            if self.inspection_sequence:
                print(f"Total steps in sequence: {len(self.inspection_sequence)}")
                print(f"Current step data: {self.inspection_sequence[self.current_step]}")
            
            # Check if we have an active inspection sequence
            if not self.inspection_sequence:
                print("No active inspection sequence")
                return False
                
            # Check if we've completed all steps
            if self.current_step >= len(self.inspection_sequence):
                print("Inspection sequence completed")
                return False
                
            # Check safety status
            if not self.arm_controller.check_safety_status():
                print("Safety check failed - cannot execute step")
                return False
                
            # Get current step data
            step = self.inspection_sequence[self.current_step]
            
            # Handle different step types
            if step["type"] == "custom_pose":
                # Handle custom pose from teach-by-touch
                print(f"Executing custom pose: {step['description']}")
                print(f"Scene config: {step['inspection_type']} - {step.get('view_type', 'unknown')} - {step.get('lighting', 'unknown')}")
                
                # Move arm to recorded joint positions
                if "joint_positions" in step:
                    joint_positions = step["joint_positions"]
                    for i, joint_pos in enumerate(joint_positions):
                        if i < len(self.arm.joint_angles):
                            self.arm.joint_angles[i] = joint_pos[2]  # Use Z coordinate as joint angle
                    print(f"Arm moved to recorded joint positions")
                else:
                    # Fallback to end effector pose
                    if not self.arm_controller.move_to_pose(step["position"], step["orientation"]):
                        print(f"Failed to move arm to custom pose for step {self.current_step}")
                        return False
                
                # Apply scene configuration (lighting, camera settings)
                lighting = step.get('lighting', 'standard')
                camera_settings = step.get('camera_settings', 'default')
                print(f"Applying lighting: {lighting}, camera: {camera_settings}")
                
                # Capture image at the recorded pose
                print("Capturing image at custom pose...")
                image = self.camera_controller.capture_image(
                    step["position"],
                    step["orientation"],
                    step["description"]
                )
                if image is None:
                    print("Failed to capture image at custom pose")
                    return False
                
                # Analyze image using pose-specific inspection type
                inspection_type = step.get("inspection_type", "custom_scene")
                print(f"Analyzing image with inspection type: {inspection_type}")
                result = self._analyze_image(image, inspection_type)
                
                # Store result with scene information
                self.results.append({
                    "step": self.current_step,
                    "type": step["type"],
                    "description": step["description"],
                    "scene_name": step.get("scene_name", "Custom Scene"),
                    "inspection_type": inspection_type,
                    "view_type": step.get("view_type", "custom_view"),
                    "lighting": lighting,
                    "camera_settings": camera_settings,
                    "result": result
                })
                
            else:
                # Handle standard inspection steps
                print(f"Moving arm to position: {step['position']}, orientation: {step['orientation']}")
                if not self.arm_controller.move_to_pose(step["position"], step["orientation"]):
                    print(f"Failed to move arm to position for step {self.current_step}")
                    return False
                    
                # Capture image
                print("Capturing image...")
                image = self.camera_controller.capture_image(
                    step["position"],
                    step["orientation"],
                    step["description"]
                )
                if image is None:
                    print("Failed to capture image")
                    return False
                    
                # Analyze image
                print("Analyzing image...")
                result = self._analyze_image(image, self.inspection_type)
                
                # Store result
                self.results.append({
                    "step": self.current_step,
                    "type": step["type"],
                    "result": result
                })
            
            # Move to next step
            self.current_step += 1
            print(f"Step {self.current_step-1} completed successfully")
            return True
            
        except Exception as e:
            print(f"Error executing step: {str(e)}")
            return False
        
    def get_inspection_status(self) -> Dict:
        """
        Get current inspection status.
        
        Returns:
            dict: Inspection status information
        """
        return {
            'is_running': self.inspection_sequence is not None,
            'current_step': self.current_step,
            'total_steps': len(self.inspection_sequence) if self.inspection_sequence else 0,
            'results': self.results.copy()
        }
        
    def stop_inspection(self):
        """Stop the current inspection sequence."""
        self.inspection_sequence = None
        self.current_step = 0
        
    def _analyze_image(self, image: np.ndarray, inspection_type: str) -> Dict:
        """
        Analyze an image for defects based on inspection type.
        
        Args:
            image: Captured image
            inspection_type: Type of inspection being performed
            
        Returns:
            Dictionary containing analysis results
        """
        # Simulate defect detection based on inspection type
        if inspection_type == "scratches_small":
            # Simulate small scratch detection (20% chance)
            has_defect = np.random.random() < 0.2
            return {
                "status": "pass" if not has_defect else "fail",
                "defects": ["small_scratch"] if has_defect else [],
                "description": "No small scratches detected" if not has_defect else "Small scratch detected"
            }
        elif inspection_type == "scratches_large":
            # Simulate large scratch detection (10% chance)
            has_defect = np.random.random() < 0.1
            return {
                "status": "pass" if not has_defect else "fail",
                "defects": ["large_scratch"] if has_defect else [],
                "description": "No large scratches detected" if not has_defect else "Large scratch detected"
            }
        elif inspection_type == "fingerprints":
            # Simulate fingerprint detection (15% chance)
            has_defect = np.random.random() < 0.15
            return {
                "status": "pass" if not has_defect else "fail",
                "defects": ["fingerprint"] if has_defect else [],
                "description": "No fingerprints detected" if not has_defect else "Fingerprint detected"
            }
        elif inspection_type == "surface_quality":
            # Simulate surface quality issues (5% chance)
            has_defect = np.random.random() < 0.05
            return {
                "status": "pass" if not has_defect else "fail",
                "defects": ["surface_imperfection"] if has_defect else [],
                "description": "Surface quality acceptable" if not has_defect else "Surface quality issues detected"
            }
        elif inspection_type == "edge_quality":
            # Simulate edge quality issues (8% chance)
            has_defect = np.random.random() < 0.08
            return {
                "status": "pass" if not has_defect else "fail",
                "defects": ["edge_imperfection"] if has_defect else [],
                "description": "Edge quality acceptable" if not has_defect else "Edge quality issues detected"
            }
        elif inspection_type == "comprehensive":
            # Simulate comprehensive inspection (multiple defect types)
            defects = []
            if np.random.random() < 0.1:  # 10% chance of scratches
                defects.append("scratch")
            if np.random.random() < 0.05:  # 5% chance of fingerprints
                defects.append("fingerprint")
            if np.random.random() < 0.03:  # 3% chance of surface issues
                defects.append("surface_imperfection")
            if np.random.random() < 0.02:  # 2% chance of edge issues
                defects.append("edge_imperfection")
            
            has_defects = len(defects) > 0
            return {
                "status": "pass" if not has_defects else "fail",
                "defects": defects,
                "description": "Comprehensive inspection passed" if not has_defects else f"Defects found: {', '.join(defects)}"
            }
        elif inspection_type == "custom_scene":
            # Simulate custom scene inspection (general purpose)
            has_defect = np.random.random() < 0.12  # 12% chance of any defect
            defect_type = np.random.choice(["scratch", "fingerprint", "surface_imperfection", "edge_imperfection"]) if has_defect else None
            return {
                "status": "pass" if not has_defect else "fail",
                "defects": [defect_type] if has_defect else [],
                "description": "Custom scene inspection passed" if not has_defect else f"Defect found: {defect_type}"
            }
        else:
            return {
                "status": "error",
                "defects": [],
                "description": f"Unknown inspection type: {inspection_type}"
            }
    
    def get_inspection_results(self) -> List[Dict[str, Any]]:
        """Get results of completed inspection."""
        return self.results
    
    def reset_safety_system(self) -> bool:
        """Reset safety system after an event."""
        return self.safety_controller.reset_system()
    
    def trigger_safety_event(self, event_type: str):
        """
        Trigger a safety event.
        
        Args:
            event_type: Type of safety event ("light_curtain", "door", "emergency_stop")
        """
        if event_type == "light_curtain":
            self.safety_controller.trigger_light_curtain_break()
        elif event_type == "door":
            self.safety_controller.trigger_door_open()
        elif event_type == "emergency_stop":
            self.safety_controller.trigger_emergency_stop()
            
        if self.inspection_sequence:
            self.stop_inspection()
    
    def get_safety_status(self) -> dict:
        """
        Get the current safety system status.
        
        Returns:
            dict: Safety status information
        """
        return {
            'light_curtain': self.safety_controller.check_light_curtain(),
            'emergency_stop': not self.safety_controller.is_emergency_stop_active(),
            'door_status': self.safety_controller.check_door_status()
        }
        
    def trigger_emergency_stop(self):
        """Trigger the emergency stop."""
        self.safety_controller.trigger_emergency_stop()
        self.inspection_sequence = None
        self.current_step = 0
        self.results = []
    
    def start_inspection_from_scene(self, part_type: str, scene_info: Dict[str, Any]) -> bool:
        """
        Start inspection using a predefined scene.
        
        Args:
            part_type: Type of part to inspect
            scene_info: Scene information with inspection type, camera angles, etc.
            
        Returns:
            bool: True if inspection started successfully
        """
        try:
            # Check safety status
            if not self.arm_controller.check_safety_status():
                print("Safety check failed - cannot start inspection")
                return False
                
            # Validate part type
            if part_type not in self.config:
                raise ValueError(f"Unknown part type: {part_type}")
            
            # Get part dimensions
            part_dimensions = self.config[part_type]["dimensions"]
            
            # Calculate inspection points based on part dimensions and camera specs
            inspection_points = calculate_inspection_grid(part_dimensions, CAMERA_CONFIG)
            
            # Filter inspection points based on scene camera angles
            camera_angles = scene_info.get("camera_angles", [])
            if camera_angles:
                self.inspection_sequence = [p for p in inspection_points if p["type"] in camera_angles]
            else:
                # If no specific camera angles, use all points
                self.inspection_sequence = inspection_points
            
            # Apply scene-specific modifications
            inspection_type = scene_info.get("inspection_type", "comprehensive")
            lighting = scene_info.get("lighting", "standard")
            
            # Add scene metadata to each inspection point
            for point in self.inspection_sequence:
                point["scene_inspection_type"] = inspection_type
                point["scene_lighting"] = lighting
                point["scene_name"] = scene_info.get("name", "Unknown Scene")
            
            print(f"Starting scene-based inspection for part: {part_type}")
            print(f"Scene: {scene_info.get('name', 'Unknown')}")
            print(f"Inspection type: {inspection_type}")
            print(f"Camera angles: {camera_angles}")
            print(f"Lighting: {lighting}")
            print(f"Inspection sequence created with {len(self.inspection_sequence)} steps")
            
            self.current_step = 0
            self.results = []
            self.inspection_type = inspection_type
            return True
            
        except Exception as e:
            print(f"Error starting scene-based inspection: {str(e)}")
            return False
    
    def start_inspection_from_custom_scene(self, part_type: str, custom_scene: Dict[str, Any]) -> bool:
        """
        Start inspection using a custom scene with recorded poses.
        
        Args:
            part_type: Type of part to inspect
            custom_scene: Custom scene with recorded poses
            
        Returns:
            bool: True if inspection started successfully
        """
        try:
            # Check safety status
            if not self.arm_controller.check_safety_status():
                print("Safety check failed - cannot start inspection")
                return False
                
            # Validate part type
            if part_type not in self.config:
                raise ValueError(f"Unknown part type: {part_type}")
            
            # Convert recorded poses to inspection sequence
            self.inspection_sequence = []
            
            for i, pose in enumerate(custom_scene["poses"]):
                # Get scene configuration from pose
                scene_config = pose.get('scene_config', {})
                inspection_type = scene_config.get('inspection_type', 'custom_scene')
                view_type = scene_config.get('view_type', 'custom_view')
                lighting = scene_config.get('lighting', 'standard')
                camera_settings = scene_config.get('camera_settings', 'default')
                
                # Convert pose to inspection step
                inspection_step = {
                    "type": "custom_pose",
                    "position": pose["end_effector_position"],
                    "orientation": pose["end_effector_orientation"],
                    "joint_positions": pose["joint_positions"],
                    "description": pose["description"],
                    "step_index": i,
                    "scene_name": custom_scene["name"],
                    "scene_description": custom_scene["description"],
                    "inspection_type": inspection_type,
                    "scene_inspection_type": inspection_type,
                    "view_type": view_type,
                    "lighting": lighting,
                    "camera_settings": camera_settings
                }
                self.inspection_sequence.append(inspection_step)
            
            print(f"Starting custom scene inspection for part: {part_type}")
            print(f"Custom scene: {custom_scene['name']}")
            print(f"Description: {custom_scene['description']}")
            print(f"Inspection sequence created with {len(self.inspection_sequence)} steps from recorded poses")
            
            # Log scene configuration details
            for i, step in enumerate(self.inspection_sequence):
                print(f"  Step {i+1}: {step['description']} - {step['inspection_type']} - {step['view_type']} - {step['lighting']}")
            
            self.current_step = 0
            self.results = []
            self.inspection_type = "custom_scene"
            return True
            
        except Exception as e:
            print(f"Error starting custom scene inspection: {str(e)}")
            return False 