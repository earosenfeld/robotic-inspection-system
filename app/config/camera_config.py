"""Camera configuration settings."""

# Camera specifications
CAMERA_CONFIG = {
    "field_of_view": {
        "horizontal": 100,  # mm
        "vertical": 100,    # mm
    },
    "resolution": {
        "width": 1920,      # pixels
        "height": 1080,     # pixels
    },
    "focal_length": 50,     # mm
    "working_distance": 300,  # mm
    "overlap_percentage": 10  # Desired overlap between inspection points (percentage)
}

def calculate_inspection_grid(part_dimensions: dict, camera_config: dict = CAMERA_CONFIG) -> list:
    """
    Calculate optimal inspection points based on part dimensions and camera specifications.
    
    Args:
        part_dimensions: Dictionary containing part dimensions
            {
                "length": float,  # mm
                "width": float,   # mm
                "height": float   # mm
            }
        camera_config: Camera configuration dictionary
    
    Returns:
        List of inspection points with positions and orientations
    """
    # Get camera field of view
    fov_x = camera_config["field_of_view"]["horizontal"]
    fov_y = camera_config["field_of_view"]["vertical"]
    
    # Calculate overlap in mm
    overlap_x = fov_x * (camera_config["overlap_percentage"] / 100)
    overlap_y = fov_y * (camera_config["overlap_percentage"] / 100)
    
    # Calculate effective coverage area (accounting for overlap)
    effective_x = fov_x - overlap_x
    effective_y = fov_y - overlap_y
    
    # Calculate number of points needed in each direction
    num_points_x = int(part_dimensions["length"] / effective_x) + 1
    num_points_y = int(part_dimensions["width"] / effective_y) + 1
    
    # Calculate inspection points
    inspection_points = []
    
    # Top view points
    for i in range(num_points_x):
        for j in range(num_points_y):
            x = (i * effective_x) - (part_dimensions["length"] / 2)
            y = (j * effective_y) - (part_dimensions["width"] / 2)
            z = camera_config["working_distance"]
            
            inspection_points.append({
                "position": [x, y, z],
                "orientation": [0, 0, 0],  # Looking straight down
                "type": "top_view",
                "description": f"Top view inspection point ({i+1},{j+1})"
            })
    
    # Side view points (for each side)
    # Front view
    for i in range(num_points_x):
        for k in range(int(part_dimensions["height"] / effective_y) + 1):
            x = (i * effective_x) - (part_dimensions["length"] / 2)
            y = part_dimensions["width"] / 2 + camera_config["working_distance"]
            z = (k * effective_y) - (part_dimensions["height"] / 2)
            
            inspection_points.append({
                "position": [x, y, z],
                "orientation": [0, 0, 0],  # Looking straight at front
                "type": "front_view",
                "description": f"Front view inspection point ({i+1},{k+1})"
            })
    
    # Back view
    for i in range(num_points_x):
        for k in range(int(part_dimensions["height"] / effective_y) + 1):
            x = (i * effective_x) - (part_dimensions["length"] / 2)
            y = -part_dimensions["width"] / 2 - camera_config["working_distance"]
            z = (k * effective_y) - (part_dimensions["height"] / 2)
            
            inspection_points.append({
                "position": [x, y, z],
                "orientation": [0, 0, 3.14159],  # Looking straight at back
                "type": "back_view",
                "description": f"Back view inspection point ({i+1},{k+1})"
            })
    
    return inspection_points 