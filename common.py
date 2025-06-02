import math

def get_distance(from_x: float, to_x: float, from_y: float, to_y: float):
    """Calculate the distance between two points."""
    return ((from_x - to_x) ** 2 + (from_y - to_y) ** 2) ** 0.5

def is_entity_inside(entity, object, radius: float):
    """Check if an entity is inside the radius of this object."""
    dist = get_distance(entity.center_x, object.center_x, entity.center_y, object.center_y)
    return dist <= radius
