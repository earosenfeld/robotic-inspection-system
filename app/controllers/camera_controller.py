from typing import Tuple, Optional
import numpy as np
from app.models.camera import Camera

class CameraController:
    """Controller for the camera system."""
    
    def __init__(self, camera: Camera):
        """
        Initialize the camera controller.
        
        Args:
            camera: Camera instance to control
        """
        self.camera = camera
        self.is_capturing = False
        
    def capture_image(self, position, orientation, scene_description):
        """
        Simulate capturing an image at a given position and orientation.
        Args:
            position: List or array of [x, y, z]
            orientation: List or array of [rx, ry, rz]
            scene_description: String describing the scene
        Returns:
            Simulated image (e.g., numpy array or placeholder)
        """
        return self.camera.capture_image(position, orientation, scene_description)
        
    def set_exposure(self, exposure_time: float):
        """
        Set the camera exposure time.
        
        Args:
            exposure_time: Exposure time in milliseconds
        """
        self.camera.set_exposure(exposure_time)
        
    def set_gain(self, gain: float):
        """
        Set the camera gain.
        
        Args:
            gain: Camera gain value
        """
        self.camera.set_gain(gain)
        
    def set_resolution(self, width: int, height: int):
        """
        Set camera resolution.
        
        Args:
            width: Image width in pixels
            height: Image height in pixels
        """
        self.camera.width = width
        self.camera.height = height
        
    def get_status(self) -> dict:
        """
        Get camera status.
        
        Returns:
            dict: Camera status information
        """
        return {
            'is_capturing': self.is_capturing,
            'exposure_time': self.camera.exposure_time,
            'gain': self.camera.gain,
            'resolution': (self.camera.width, self.camera.height)
        }
        
    def reset(self):
        """Reset camera to default settings."""
        self.camera = Camera()
        self.is_capturing = False
        
    def get_camera_parameters(self) -> dict:
        """
        Get current camera parameters.
        
        Returns:
            dict: Camera parameters
        """
        return {
            'exposure': self.camera.exposure_time,
            'gain': self.camera.gain,
            'resolution': self.camera.resolution
        } 