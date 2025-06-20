import numpy as np
import cv2
import random
from typing import Optional

class ImageSimulator:
    """Simulates camera images for the inspection system."""
    
    def __init__(self):
        """Initialize the image simulator."""
        self.image_width = 640
        self.image_height = 480
        
    def generate_base_image(self, part_type: str = "generic") -> np.ndarray:
        """Generate a base image for the specified part type."""
        # Create a base image with a metallic surface appearance
        base_image = np.zeros((self.image_height, self.image_width, 3), dtype=np.uint8)
        
        # Add metallic texture
        noise = np.random.randint(0, 30, (self.image_height, self.image_width), dtype=np.uint8)
        base_image[:, :, 0] = 100 + noise  # Blue channel
        base_image[:, :, 1] = 120 + noise  # Green channel  
        base_image[:, :, 2] = 140 + noise  # Red channel
        
        # Add some variation based on part type
        if part_type == "Small Part":
            # Add small geometric features
            cv2.rectangle(base_image, (200, 150), (440, 330), (80, 100, 120), 2)
        elif part_type == "Medium Part":
            # Add medium geometric features
            cv2.rectangle(base_image, (150, 100), (490, 380), (80, 100, 120), 3)
        elif part_type == "Large Part":
            # Add large geometric features
            cv2.rectangle(base_image, (100, 50), (540, 430), (80, 100, 120), 4)
        
        return base_image
    
    def generate_inspection_image(self, part_type: str, defect_type: str, defect_probability: float = 0.2) -> np.ndarray:
        """Generate an inspection image with potential defects."""
        # Start with base image
        image = self.generate_base_image(part_type)
        
        # Add defects based on type and probability
        if random.random() < defect_probability:
            image = self._add_defect(image, defect_type, part_type)
        
        # Add some realistic lighting variations
        image = self._add_lighting_effects(image)
        
        return image
    
    def _add_defect(self, image: np.ndarray, defect_type: str, part_type: str) -> np.ndarray:
        """Add a specific type of defect to the image."""
        if defect_type == "scratches":
            return self._add_scratches(image, part_type)
        elif defect_type == "fingerprints":
            return self._add_fingerprints(image, part_type)
        elif defect_type == "surface_quality":
            return self._add_surface_quality_issues(image, part_type)
        elif defect_type == "edge_quality":
            return self._add_edge_quality_issues(image, part_type)
        else:
            return image
    
    def _add_scratches(self, image: np.ndarray, part_type: str) -> np.ndarray:
        """Add scratch defects to the image."""
        num_scratches = random.randint(1, 3)
        
        for _ in range(num_scratches):
            # Random scratch parameters
            start_x = random.randint(50, self.image_width - 50)
            start_y = random.randint(50, self.image_height - 50)
            length = random.randint(20, 100)
            angle = random.uniform(0, 2 * np.pi)
            thickness = random.randint(1, 3)
            
            # Calculate end point
            end_x = int(start_x + length * np.cos(angle))
            end_y = int(start_y + length * np.sin(angle))
            
            # Ensure end point is within image bounds
            end_x = max(0, min(end_x, self.image_width - 1))
            end_y = max(0, min(end_y, self.image_height - 1))
            
            # Draw scratch (darker line)
            cv2.line(image, (start_x, start_y), (end_x, end_y), (40, 50, 60), thickness)
            
            # Add some variation to make it look more realistic
            for i in range(thickness):
                offset = random.randint(-2, 2)
                cv2.line(image, 
                        (start_x + offset, start_y + offset), 
                        (end_x + offset, end_y + offset), 
                        (30, 40, 50), 1)
        
        return image
    
    def _add_fingerprints(self, image: np.ndarray, part_type: str) -> np.ndarray:
        """Add fingerprint defects to the image."""
        num_prints = random.randint(1, 2)
        
        for _ in range(num_prints):
            # Random fingerprint center
            center_x = random.randint(100, self.image_width - 100)
            center_y = random.randint(100, self.image_height - 100)
            radius = random.randint(15, 30)
            
            # Create fingerprint pattern (concentric circles with noise)
            for r in range(radius, 0, -2):
                intensity = random.randint(60, 100)
                cv2.circle(image, (center_x, center_y), r, (intensity, intensity, intensity), 1)
                
                # Add some noise to make it look more realistic
                for _ in range(random.randint(3, 8)):
                    angle = random.uniform(0, 2 * np.pi)
                    x = int(center_x + r * np.cos(angle))
                    y = int(center_y + r * np.sin(angle))
                    if 0 <= x < self.image_width and 0 <= y < self.image_height:
                        image[y, x] = (intensity - 20, intensity - 20, intensity - 20)
        
        return image
    
    def _add_surface_quality_issues(self, image: np.ndarray, part_type: str) -> np.ndarray:
        """Add surface quality issues to the image."""
        # Add some surface roughness or discoloration
        num_areas = random.randint(2, 5)
        
        for _ in range(num_areas):
            # Random area
            x1 = random.randint(50, self.image_width - 100)
            y1 = random.randint(50, self.image_height - 100)
            x2 = x1 + random.randint(30, 80)
            y2 = y1 + random.randint(30, 80)
            
            # Create surface quality issue (slightly different color/texture)
            issue_type = random.choice(['discoloration', 'roughness', 'stain'])
            
            if issue_type == 'discoloration':
                # Add color variation
                color_shift = random.randint(-30, 30)
                roi = image[y1:y2, x1:x2]
                roi[:, :, 0] = np.clip(roi[:, :, 0] + color_shift, 0, 255)
                roi[:, :, 1] = np.clip(roi[:, :, 1] + color_shift, 0, 255)
                roi[:, :, 2] = np.clip(roi[:, :, 2] + color_shift, 0, 255)
                
            elif issue_type == 'roughness':
                # Add noise to simulate roughness
                roi = image[y1:y2, x1:x2]
                noise = np.random.randint(-20, 20, roi.shape, dtype=np.int16)
                roi = np.clip(roi.astype(np.int16) + noise, 0, 255).astype(np.uint8)
                image[y1:y2, x1:x2] = roi
                
            elif issue_type == 'stain':
                # Add a stain-like pattern
                cv2.ellipse(image, (x1 + (x2-x1)//2, y1 + (y2-y1)//2), 
                           ((x2-x1)//2, (y2-y1)//2), 0, 0, 360, (70, 80, 90), -1)
        
        return image
    
    def _add_edge_quality_issues(self, image: np.ndarray, part_type: str) -> np.ndarray:
        """Add edge quality issues to the image."""
        # Add edge defects like burrs or chips
        num_edges = random.randint(1, 3)
        
        for _ in range(num_edges):
            # Random edge location
            edge_x = random.randint(50, self.image_width - 50)
            edge_y = random.randint(50, self.image_height - 50)
            edge_length = random.randint(20, 60)
            
            # Edge defect type
            defect_type = random.choice(['burr', 'chip', 'rough_edge'])
            
            if defect_type == 'burr':
                # Add small protrusions along edge
                for i in range(0, edge_length, 5):
                    x = edge_x + i
                    y = edge_y + random.randint(-3, 3)
                    if 0 <= x < self.image_width and 0 <= y < self.image_height:
                        cv2.circle(image, (x, y), 1, (50, 60, 70), -1)
                        
            elif defect_type == 'chip':
                # Add a chip in the edge
                chip_size = random.randint(3, 8)
                cv2.circle(image, (edge_x + edge_length//2, edge_y), chip_size, (30, 40, 50), -1)
                
            elif defect_type == 'rough_edge':
                # Add roughness along edge
                for i in range(0, edge_length, 2):
                    x = edge_x + i
                    y = edge_y + random.randint(-2, 2)
                    if 0 <= x < self.image_width and 0 <= y < self.image_height:
                        image[y, x] = (40, 50, 60)
        
        return image
    
    def _add_lighting_effects(self, image: np.ndarray) -> np.ndarray:
        """Add realistic lighting effects to the image."""
        # Add subtle lighting variations
        height, width = image.shape[:2]
        
        # Create a gradient for lighting
        gradient = np.zeros((height, width), dtype=np.float32)
        for y in range(height):
            for x in range(width):
                # Simulate overhead lighting
                gradient[y, x] = 1.0 - 0.3 * (y / height) + 0.1 * np.sin(x / 50)
        
        # Apply lighting effect
        for c in range(3):
            image[:, :, c] = np.clip(image[:, :, c] * gradient, 0, 255).astype(np.uint8)
        
        # Add some random shadows
        num_shadows = random.randint(1, 3)
        for _ in range(num_shadows):
            shadow_x = random.randint(0, width - 50)
            shadow_y = random.randint(0, height - 50)
            shadow_w = random.randint(20, 50)
            shadow_h = random.randint(20, 50)
            
            # Create shadow mask
            shadow_mask = np.zeros((shadow_h, shadow_w), dtype=np.float32)
            cv2.ellipse(shadow_mask, (shadow_w//2, shadow_h//2), (shadow_w//2, shadow_h//2), 
                       0, 0, 360, 0.3, -1)
            
            # Apply shadow
            roi = image[shadow_y:shadow_y+shadow_h, shadow_x:shadow_x+shadow_w]
            for c in range(3):
                roi[:, :, c] = np.clip(roi[:, :, c] * (1 - shadow_mask), 0, 255).astype(np.uint8)
        
        return image 