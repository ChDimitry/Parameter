import arcade
import random
from constants import OBSTACLE_COLOR


SHAPES = [
    [(-40, -40), (40, -40), (40, 40), (-40, 40)],                      # Square
    [(0, -50), (50, 0), (0, 50), (-50, 0)],                             # Diamond
    [(0, -60), (50, -20), (30, 40), (-30, 40), (-50, -20)],             # Pentagon
    [(0, -50), (50, -25), (30, 50), (-30, 50), (-50, -25)],             # Widened pentagon
    [(0, -50), (60, 0), (30, 50), (-30, 50), (-60, 0)],                 # Arrowhead
]


class Obstacle(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__(hit_box_algorithm="none")

        self.center_x = x
        self.center_y = y
        self.color = OBSTACLE_COLOR

        # Choose a random shape from the SHAPES list
        self.shape_points = random.choice(SHAPES)

    def draw(self):
        # Translate shape to current position
        translated_points = [
            (self.center_x + x, self.center_y + y)
            for (x, y) in self.shape_points
        ]
        arcade.draw_polygon_filled(translated_points, self.color)

    def is_entity_inside(self, entity):
        return arcade.is_point_in_polygon(
            entity.center_x, entity.center_y, self.get_adjusted_hit_box()
        )
