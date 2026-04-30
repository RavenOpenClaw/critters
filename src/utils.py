"""
Utility functions for spatial calculations and other shared logic.
"""
import math

def get_distance_to_boundary(entity, target):
    """
    Calculate the Euclidean distance from an entity's center to the nearest point 
    on a target's rectangular boundary.
    
    Args:
        entity: The entity initiating the interaction (must have .x, .y).
        target: The world object being targeted (must have .x, .y, .width, .height, .cell_size).
        
    Returns:
        float: The distance to the nearest edge/corner. 0.0 if the entity is inside or touching.
    """
    # Target rectangle boundaries in pixels
    t_left = target.x
    t_right = target.x + target.width * target.cell_size
    t_top = target.y
    t_bottom = target.y + target.height * target.cell_size
    
    # Nearest point on the rectangle to the entity's center
    dx = max(t_left - entity.x, 0, entity.x - t_right)
    dy = max(t_top - entity.y, 0, entity.y - t_bottom)
    
    return math.sqrt(dx*dx + dy*dy)
