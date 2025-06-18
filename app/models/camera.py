import numpy as np
import cv2
from typing import Tuple, Optional, Dict, Any

class Camera:
    def __init__(self, resolution: Tuple[int, int] = (640, 480)):
        """
        Initialize simulated camera.
        
        Args:
            resolution: Camera resolution (width, height)
        """
        self.resolution = resolution
        self.focal_length = 500  # pixels
        self.principal_point = (resolution[0] // 2, resolution[1] // 2)
        
    def capture_image(self, position: np.ndarray, orientation: np.ndarray,
                     scene_description: Dict[str, Any]) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Simulate capturing an image at the given position and orientation.
        
        Args:
            position: Camera position [x, y, z]
            orientation: Camera orientation [roll, pitch, yaw]
            scene_description: Dictionary describing the scene to simulate
            
        Returns:
            Tuple of (image, inspection_results)
        """
        # Create a blank image
        image = np.zeros((self.resolution[1], self.resolution[0], 3), dtype=np.uint8)
        
        # Simulate different types of scenes based on description
        if 'type' in scene_description:
            if scene_description['type'] == 'color_check':
                image = self._simulate_color_check(scene_description)
            elif scene_description['type'] == 'shape_detection':
                image = self._simulate_shape_detection(scene_description)
            elif scene_description['type'] == 'text_reading':
                image = self._simulate_text_reading(scene_description)
            else:
                image = self._simulate_random_scene()
        else:
            image = self._simulate_random_scene()
            
        # Add some noise to make it more realistic
        noise = np.random.normal(0, 10, image.shape).astype(np.uint8)
        image = cv2.add(image, noise)
        
        # Simulate inspection results
        results = self._simulate_inspection(image, scene_description)
        
        return image, results
    
    def _simulate_color_check(self, description: Dict[str, Any]) -> np.ndarray:
        """Simulate a color check scene."""
        image = np.zeros((self.resolution[1], self.resolution[0], 3), dtype=np.uint8)
        
        # Draw color patches
        colors = description.get('expected_colors', [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 255, 0)   # Yellow
        ])
        
        patch_size = (self.resolution[0] // 4, self.resolution[1] // 2)
        for i, color in enumerate(colors):
            x = i * patch_size[0]
            image[0:patch_size[1], x:x+patch_size[0]] = color
            
        return image
    
    def _simulate_shape_detection(self, description: Dict[str, Any]) -> np.ndarray:
        """Simulate a shape detection scene."""
        image = np.zeros((self.resolution[1], self.resolution[0], 3), dtype=np.uint8)
        
        # Draw random shapes
        shapes = description.get('expected_shapes', ['circle', 'square', 'triangle'])
        for shape in shapes:
            if shape == 'circle':
                cv2.circle(image, 
                          (np.random.randint(100, self.resolution[0]-100),
                           np.random.randint(100, self.resolution[1]-100)),
                          50, (0, 255, 0), -1)
            elif shape == 'square':
                cv2.rectangle(image,
                            (np.random.randint(100, self.resolution[0]-150),
                             np.random.randint(100, self.resolution[1]-150)),
                            (np.random.randint(200, self.resolution[0]-50),
                             np.random.randint(200, self.resolution[1]-50)),
                            (255, 0, 0), -1)
            elif shape == 'triangle':
                pts = np.array([
                    [np.random.randint(100, self.resolution[0]-100),
                     np.random.randint(100, self.resolution[1]-100)],
                    [np.random.randint(100, self.resolution[0]-100),
                     np.random.randint(100, self.resolution[1]-100)],
                    [np.random.randint(100, self.resolution[0]-100),
                     np.random.randint(100, self.resolution[1]-100)]
                ])
                cv2.fillPoly(image, [pts], (0, 0, 255))
                
        return image
    
    def _simulate_text_reading(self, description: Dict[str, Any]) -> np.ndarray:
        """Simulate a text reading scene."""
        image = np.zeros((self.resolution[1], self.resolution[0], 3), dtype=np.uint8)
        
        # Draw text
        text = description.get('expected_text', 'TEST123')
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(image, text,
                   (self.resolution[0]//4, self.resolution[1]//2),
                   font, 2, (255, 255, 255), 2)
                   
        return image
    
    def _simulate_random_scene(self) -> np.ndarray:
        """Generate a random scene for testing."""
        image = np.zeros((self.resolution[1], self.resolution[0], 3), dtype=np.uint8)
        
        # Add some random shapes and colors
        for _ in range(5):
            color = (np.random.randint(0, 255),
                    np.random.randint(0, 255),
                    np.random.randint(0, 255))
            cv2.circle(image,
                      (np.random.randint(0, self.resolution[0]),
                       np.random.randint(0, self.resolution[1])),
                      np.random.randint(10, 50),
                      color, -1)
                      
        return image
    
    def _simulate_inspection(self, image: np.ndarray,
                           description: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate inspection results based on the image and scene description.
        
        Args:
            image: Captured image
            description: Scene description
            
        Returns:
            Dictionary containing inspection results
        """
        results = {
            'timestamp': np.datetime64('now'),
            'passed': True,
            'confidence': 0.95,
            'measurements': {},
            'defects': []
        }
        
        # Simulate different types of inspections
        if 'type' in description:
            if description['type'] == 'color_check':
                results.update(self._simulate_color_inspection(image, description))
            elif description['type'] == 'shape_detection':
                results.update(self._simulate_shape_inspection(image, description))
            elif description['type'] == 'text_reading':
                results.update(self._simulate_text_inspection(image, description))
                
        return results
    
    def _simulate_color_inspection(self, image: np.ndarray,
                                 description: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate color inspection results."""
        return {
            'color_matches': True,
            'color_confidence': 0.98,
            'color_measurements': {
                'red': np.random.uniform(0.95, 1.0),
                'green': np.random.uniform(0.95, 1.0),
                'blue': np.random.uniform(0.95, 1.0)
            }
        }
    
    def _simulate_shape_inspection(self, image: np.ndarray,
                                 description: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate shape inspection results."""
        return {
            'shapes_found': len(description.get('expected_shapes', [])),
            'shape_confidence': 0.97,
            'shape_measurements': {
                'area': np.random.uniform(1000, 2000),
                'perimeter': np.random.uniform(100, 200)
            }
        }
    
    def _simulate_text_inspection(self, image: np.ndarray,
                                description: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate text inspection results."""
        return {
            'text_found': True,
            'text_confidence': 0.99,
            'text_measurements': {
                'readability_score': np.random.uniform(0.9, 1.0),
                'character_count': len(description.get('expected_text', ''))
            }
        } 