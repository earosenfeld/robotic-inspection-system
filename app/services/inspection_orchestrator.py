import time
import json
from typing import Dict, Any, List, Optional
from app.controllers.robotic_arm_controller import RoboticArmController
from app.controllers.camera_controller import CameraController
from app.controllers.safety_controller import SafetyController
from app.models.robotic_arm import RoboticArm
from app.models.camera import Camera
from app.utils.image_simulation import ImageSimulator
from app.models.safety_system import SafetySystem

class InspectionOrchestrator:
    """Orchestrates the inspection workflow and coordinates between controllers."""
    
    def __init__(self):
        """Initialize the orchestrator with all controllers."""
        # Create robotic arm model first
        self.arm_model = RoboticArm()
        self.arm_controller = RoboticArmController(self.arm_model)
        self.camera_model = Camera()
        self.camera_controller = CameraController(self.camera_model)
        self.safety_system = SafetySystem()
        self.safety_controller = SafetyController(self.safety_system)
        self.image_simulator = ImageSimulator()
        
        # Inspection state
        self.current_part = None
        self.current_inspection_type = None
        self.inspection_sequence = []
        self.current_scene_index = 0
        self.is_running = False
        self.results = []
        
        # Load inspection configurations
        self._load_inspection_configs()
        
    def _load_inspection_configs(self):
        """Load inspection configurations from JSON files."""
        try:
            with open('data/configs/parts_inspection_config.json', 'r') as f:
                raw_config = json.load(f)
            
            # Convert the raw config to the expected format with scenes
            self.inspection_configs = {}
            for part_name, part_config in raw_config.items():
                self.inspection_configs[part_name] = {}
                
                # Get inspection types from the config
                inspection_types = part_config.get('inspection_types', [])
                
                # Create scenes for each inspection type
                for inspection_type in inspection_types:
                    self.inspection_configs[part_name][inspection_type] = {
                        "scenes": self._create_scenes_for_inspection_type(inspection_type, part_name)
                    }
                    
        except FileNotFoundError:
            print("[WARNING] Config file not found, using fallback configuration")
            # Fallback configuration
            self.inspection_configs = {
                "Small Part": {
                    "scratches_small": {
                        "scenes": [
                            {"name": "Top Surface", "position": [0, 0, 0.1], "fov": 50, "defect_type": "scratches"},
                            {"name": "Side Surface", "position": [0.05, 0, 0.1], "fov": 50, "defect_type": "scratches"}
                        ]
                    },
                    "fingerprints": {
                        "scenes": [
                            {"name": "Surface Check", "position": [0, 0, 0.1], "fov": 50, "defect_type": "fingerprints"}
                        ]
                    }
                },
                "Medium Part": {
                    "scratches_large": {
                        "scenes": [
                            {"name": "Top Surface", "position": [0, 0, 0.15], "fov": 75, "defect_type": "scratches"},
                            {"name": "Side Surface", "position": [0.1, 0, 0.15], "fov": 75, "defect_type": "scratches"},
                            {"name": "Bottom Surface", "position": [0, 0, 0.05], "fov": 75, "defect_type": "scratches"}
                        ]
                    },
                    "fingerprints": {
                        "scenes": [
                            {"name": "Surface Check", "position": [0, 0, 0.15], "fov": 75, "defect_type": "fingerprints"}
                        ]
                    },
                    "surface_quality": {
                        "scenes": [
                            {"name": "Quality Check", "position": [0, 0, 0.15], "fov": 75, "defect_type": "surface_quality"}
                        ]
                    }
                },
                "Large Part": {
                    "scratches_large": {
                        "scenes": [
                            {"name": "Top Surface", "position": [0, 0, 0.2], "fov": 100, "defect_type": "scratches"},
                            {"name": "Side Surface 1", "position": [0.15, 0, 0.2], "fov": 100, "defect_type": "scratches"},
                            {"name": "Side Surface 2", "position": [-0.15, 0, 0.2], "fov": 100, "defect_type": "scratches"},
                            {"name": "Bottom Surface", "position": [0, 0, 0.05], "fov": 100, "defect_type": "scratches"}
                        ]
                    },
                    "fingerprints": {
                        "scenes": [
                            {"name": "Surface Check", "position": [0, 0, 0.2], "fov": 100, "defect_type": "fingerprints"}
                        ]
                    },
                    "surface_quality": {
                        "scenes": [
                            {"name": "Quality Check", "position": [0, 0, 0.2], "fov": 100, "defect_type": "surface_quality"}
                        ]
                    },
                    "edge_quality": {
                        "scenes": [
                            {"name": "Edge Check", "position": [0, 0, 0.2], "fov": 100, "defect_type": "edge_quality"}
                        ]
                    }
                }
            }
    
    def _create_scenes_for_inspection_type(self, inspection_type: str, part_name: str) -> List[Dict[str, Any]]:
        """Create scenes configuration for a given inspection type and part."""
        # Base positions and FOVs based on part size - more realistic workspace
        base_configs = {
            "Small Part": {
                "base_height": 0.3,
                "base_fov": 50,
                "positions": [
                    [0.2, 0.0, 0.3],    # Front inspection
                    [0.0, 0.2, 0.3],    # Right side
                    [0.0, -0.2, 0.3],   # Left side
                    [0.2, 0.0, 0.4]     # Top inspection
                ]
            },
            "Medium Part": {
                "base_height": 0.4,
                "base_fov": 75,
                "positions": [
                    [0.3, 0.0, 0.4],    # Front inspection
                    [0.0, 0.3, 0.4],    # Right side
                    [0.0, -0.3, 0.4],   # Left side
                    [0.3, 0.0, 0.5],    # Top inspection
                    [0.2, 0.0, 0.3]     # Lower angle
                ]
            },
            "Large Part": {
                "base_height": 0.5,
                "base_fov": 100,
                "positions": [
                    [0.4, 0.0, 0.5],    # Front inspection
                    [0.0, 0.4, 0.5],    # Right side
                    [0.0, -0.4, 0.5],   # Left side
                    [0.4, 0.0, 0.6],    # Top inspection
                    [0.3, 0.0, 0.4]     # Lower angle
                ]
            }
        }
        
        config = base_configs.get(part_name, base_configs["Small Part"])
        
        # Create scenes based on inspection type
        scenes = []
        scene_names = []
        
        if "scratches" in inspection_type:
            scene_names = ["Top Surface", "Side Surface", "Bottom Surface"]
        elif "fingerprints" in inspection_type:
            scene_names = ["Surface Check"]
        elif "surface_quality" in inspection_type:
            scene_names = ["Quality Check"]
        elif "edge_quality" in inspection_type:
            scene_names = ["Edge Check"]
        else:
            scene_names = ["General Inspection"]
        
        # Map defect types
        defect_type_map = {
            "scratches_small": "scratches",
            "scratches_large": "scratches",
            "fingerprints": "fingerprints",
            "surface_quality": "surface_quality",
            "edge_quality": "edge_quality"
        }
        
        defect_type = defect_type_map.get(inspection_type, "general")
        
        # Create scenes
        for i, name in enumerate(scene_names):
            if i < len(config["positions"]):
                position = config["positions"][i]
            else:
                # Use first position if we run out of positions
                position = config["positions"][0]
                
            scenes.append({
                "name": name,
                "position": position,
                "fov": config["base_fov"],
                "defect_type": defect_type
            })
        
        return scenes
    
    def get_available_parts(self) -> List[str]:
        """Get list of available parts for inspection."""
        return list(self.inspection_configs.keys())
    
    def get_part_inspection_types(self, part_name: str) -> List[str]:
        """Get available inspection types for a specific part."""
        if part_name in self.inspection_configs:
            return list(self.inspection_configs[part_name].keys())
        return []
    
    def start_inspection(self, part_name: str, inspection_type: str) -> bool:
        """Start a new inspection for the specified part and type."""
        try:
            print(f"[DEBUG] Starting inspection for {part_name} - {inspection_type}")
            
            # Validate inputs
            if part_name not in self.inspection_configs:
                print(f"[ERROR] Invalid part name: {part_name}")
                return False
                
            if inspection_type not in self.inspection_configs[part_name]:
                print(f"[ERROR] Invalid inspection type: {inspection_type} for part {part_name}")
                return False
            
            # Set current inspection parameters
            self.current_part = part_name
            self.current_inspection_type = inspection_type
            self.current_scene_index = 0
            self.is_running = True
            self.results = []
            
            # Get inspection sequence
            self.inspection_sequence = self.inspection_configs[part_name][inspection_type]["scenes"]
            print(f"[DEBUG] Inspection sequence loaded: {self.inspection_sequence}")
            
            # Initialize controllers
            try:
                self.arm_controller.reset()
                print("[DEBUG] Arm controller reset.")
            except Exception as e:
                print(f"[ERROR] Arm controller reset failed: {e}")
                return False
            try:
                if hasattr(self.camera_controller, 'initialize'):
                    self.camera_controller.initialize()
                    print("[DEBUG] Camera controller initialized.")
            except Exception as e:
                print(f"[ERROR] Camera controller initialization failed: {e}")
                return False
            try:
                if hasattr(self.safety_controller, 'initialize'):
                    self.safety_controller.initialize()
                    print("[DEBUG] Safety controller initialized.")
            except Exception as e:
                print(f"[ERROR] Safety controller initialization failed: {e}")
                return False
            
            print(f"[DEBUG] Inspection started successfully. {len(self.inspection_sequence)} scenes to process.")
            return True
            
        except Exception as e:
            print(f"[ERROR] Exception in start_inspection: {str(e)}")
            return False
    
    def execute_next_step(self) -> Dict[str, Any]:
        """Execute the next step in the inspection sequence."""
        try:
            if not self.is_running:
                return {"success": False, "message": "No inspection running"}
            
            if self.current_scene_index >= len(self.inspection_sequence):
                self.is_running = False
                return {"success": False, "message": "Inspection completed"}
            
            # Get current scene
            current_scene = self.inspection_sequence[self.current_scene_index]
            scene_number = self.current_scene_index + 1
            total_scenes = len(self.inspection_sequence)
            
            print(f"Executing scene {scene_number}/{total_scenes}: {current_scene['name']}")
            
            # Check safety
            if not self.safety_controller.check_safety_status():
                return {"success": False, "message": "Safety check failed"}
            
            # Move arm to position
            target_position = current_scene['position']
            if not self.move_to_position(target_position):
                return {"success": False, "message": "Failed to move arm to position"}
            
            # Wait for arm to settle
            time.sleep(0.5)
            
            # Capture image
            capture_result = self.camera_controller.capture_image(
                position=target_position,
                orientation=[0, 0, 0],  # Default orientation
                scene_description={"type": current_scene['defect_type']}
            )
            
            # Handle the tuple return (image, results)
            if capture_result is not None and len(capture_result) == 2:
                image, camera_results = capture_result
            else:
                image = None
            
            if image is None:
                # Generate simulated image
                image = self.image_simulator.generate_inspection_image(
                    self.current_part,
                    current_scene['defect_type'],
                    defect_probability=0.2
                )
            
            # Perform inspection analysis
            inspection_result = self._analyze_image(image, current_scene['defect_type'])
            
            # Create result record
            result = {
                "scene_number": scene_number,
                "scene_name": current_scene['name'],
                "pose_description": f"Position {target_position}",
                "defect_type": current_scene['defect_type'],
                "result": inspection_result,
                "fov": current_scene['fov'],
                "timestamp": time.time()
            }
            
            self.results.append(result)
            
            # Move to next scene
            self.current_scene_index += 1
            
            # Check if inspection is complete
            if self.current_scene_index >= len(self.inspection_sequence):
                self.is_running = False
                print("Inspection completed")
            
            # Get current arm positions for visualization
            arm_positions = self.arm_controller.arm.get_joint_positions()
            
            return {
                "success": True,
                "result": result,
                "image": image,
                "arm_positions": arm_positions,
                "scene_complete": not self.is_running
            }
            
        except Exception as e:
            print(f"Error executing step: {str(e)}")
            return {"success": False, "message": f"Step execution error: {str(e)}"}
    
    def move_to_position(self, position: List[float]) -> bool:
        """Move the arm to a specific position."""
        try:
            # Default orientation (pointing down)
            orientation = [0, 0, 0]
            return self.arm_controller.move_to_pose(position, orientation)
        except Exception as e:
            print(f"Error moving to position: {str(e)}")
            return False
    
    def _analyze_image(self, image, defect_type: str) -> str:
        """Analyze the captured image for defects."""
        # Simulate image analysis
        import random
        
        # Different defect types have different detection probabilities
        defect_probabilities = {
            "scratches": 0.15,
            "fingerprints": 0.25,
            "surface_quality": 0.10,
            "edge_quality": 0.20
        }
        
        probability = defect_probabilities.get(defect_type, 0.15)
        
        # Simulate detection
        if random.random() < probability:
            return "FAIL"
        else:
            return "PASS"
    
    def get_inspection_status(self) -> Dict[str, Any]:
        """Get current inspection status."""
        return {
            "is_running": self.is_running,
            "current_scene": self.current_scene_index,
            "total_scenes": len(self.inspection_sequence),
            "current_part": self.current_part,
            "current_inspection_type": self.current_inspection_type,
            "safety_status": self.safety_controller.check_safety_status(),
            "camera_status": {"ready": True},  # Assume camera is always ready for simulation
            "results_count": len(self.results)
        }
    
    def get_current_scene_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the current scene."""
        if not self.is_running or self.current_scene_index >= len(self.inspection_sequence):
            return None
        
        current_scene = self.inspection_sequence[self.current_scene_index]
        return {
            "scene_number": self.current_scene_index + 1,
            "total_scenes": len(self.inspection_sequence),
            "scene_name": current_scene['name'],
            "defect_type": current_scene['defect_type'],
            "fov": current_scene['fov'],
            "position": current_scene['position']
        }
    
    def reset_inspection(self):
        """Reset the inspection to initial state."""
        self.current_part = None
        self.current_inspection_type = None
        self.inspection_sequence = []
        self.current_scene_index = 0
        self.is_running = False
        self.results = []
        
        # Reset controllers
        self.arm_controller.reset()
        self.camera_controller.reset()
        self.safety_controller.reset()
        
        print("Inspection reset to initial state")
    
    def emergency_stop(self):
        """Immediately stop all operations and reset to safe state."""
        print("EMERGENCY STOP ACTIVATED")
        
        # Stop all operations
        self.is_running = False
        self.current_scene_index = 0
        
        # Trigger safety system emergency stop
        try:
            self.safety_controller.trigger_emergency_stop()
            print("Safety system emergency stop triggered")
        except Exception as e:
            print(f"Error triggering safety emergency stop: {e}")
        
        # Reset arm to safe position
        try:
            self.arm_controller.reset()
            print("Arm reset to safe position")
        except Exception as e:
            print(f"Error resetting arm: {e}")
        
        # Reset camera
        try:
            self.camera_controller.reset()
            print("Camera reset")
        except Exception as e:
            print(f"Error resetting camera: {e}")
        
        # Clear inspection state
        self.current_part = None
        self.current_inspection_type = None
        self.inspection_sequence = []
        self.results = []
        
        print("Emergency stop complete - system in safe state")
    
    @property
    def arm(self):
        """Get the robotic arm model for direct access."""
        return self.arm_controller.arm 