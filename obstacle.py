import arcade
from common import get_distance
from constants import OBSTACLE_COLOR

class Obstacle(arcade.SpriteCircle):
    def __init__(self, x, y, radius=100):
        super().__init__(radius=radius, color=OBSTACLE_COLOR, soft=True)
        self.center_x = x
        self.center_y = y
        self.radius = radius


    def is_entity_inside(self, entity):
        dist = get_distance(entity.center_x, self.center_x, entity.center_y, self.center_y)
        return dist <= self.radius