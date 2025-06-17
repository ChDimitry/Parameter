import arcade

def get_distance(from_x: float, to_x: float, from_y: float, to_y: float):
    """Calculate the distance between two points."""
    return ((from_x - to_x) ** 2 + (from_y - to_y) ** 2) ** 0.5

def is_entity_inside(entity, object, radius: float):
    """Check if an entity is inside the radius of this object."""
    dist = get_distance(entity.center_x, object.center_x, entity.center_y, object.center_y)
    return dist <= radius

def get_text_object(text: str, x: float, y: float, color=(255, 255, 255), font_size=10):
    """Create a text object for rendering."""
    return arcade.Text(        
        text,
        x, y,
        color=color,
        font_size=font_size,
        anchor_x="center",
        anchor_y="center"
    )