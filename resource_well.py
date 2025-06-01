import arcade
import random
from constants import RESOURCE_WELL_BG_COLOR, RESOURCE_WELL_OUTLINE_COLOR, RESOURCE_WELL_TEXT_COLOR

class ResourceWell:
    def __init__(self, x=None, y=None, x_max=1000, y_max=1000, capacity=100, radius=50):
        self.center_x = x if x is not None else random.randint(-x_max, x_max)
        self.center_y = y if y is not None else random.randint(-y_max, y_max)
        self.capacity = capacity
        self.radius = radius
        self.active = True

        self.last_transfer = 0

    def draw(self):
        arcade.draw_circle_filled(
            self.center_x,
            self.center_y,
            self.radius,
            RESOURCE_WELL_BG_COLOR
        )
        arcade.draw_circle_outline(
            self.center_x,
            self.center_y,
            self.radius,
            RESOURCE_WELL_OUTLINE_COLOR,
            2
        )
        # Show remaining resource text
        arcade.draw_text(
            f"{self.capacity}",
            self.center_x, self.center_y,
            RESOURCE_WELL_TEXT_COLOR,
            font_size=10,
            anchor_x="center",
            anchor_y="center"
        )

    def is_entity_inside(self, entity):
        dist = ((entity.center_x - self.center_x) ** 2 + (entity.center_y - self.center_y) ** 2) ** 0.5
        return dist <= self.radius
