import arcade
import random
import math
from constants import RESOURCE_WELL_BG_COLOR, RESOURCE_WELL_OUTLINE_COLOR, RESOURCE_WELL_TEXT_COLOR

class ResourceWell:
    def __init__(self, x=None, y=None, x_max=1000, y_max=1000, capacity=100, radius=50, upgrade_attributes=[], upgrade_type=None):
        self.center_x = x if x is not None else random.randint(-x_max, x_max)
        self.center_y = y if y is not None else random.randint(-y_max, y_max)
        self.capacity = capacity
        self.radius = radius
        self.active = True
        self.upgrade_attributes = upgrade_attributes
        self.upgrade_type = upgrade_type

        self.last_transfer = 0
        
        self.assigned_node = None 

        self.upgrade_symbols = {
            "damage": "✦",
            "range": "○",
            "bullet_speed": "➤",
            "fire_rate": "⚡"
        }
        self.upgrade_symbol = self.upgrade_symbols.get(self.upgrade_type, "")

    def draw(self, time_elapsed=0):
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
            RESOURCE_WELL_OUTLINE_COLOR if self.assigned_node else (100, 100, 100, 100),
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

        # Draw collection rate of node
        if self.assigned_node:
            arcade.draw_text(
                f"Rate: 1 Scrap/{self.assigned_node.collection_rate}s",
                self.center_x, self.center_y - 15,
                RESOURCE_WELL_TEXT_COLOR,
                font_size=10,
                anchor_x="center",
                anchor_y="center"
            )
        

        if self.upgrade_type:
            arcade.draw_text(
                self.upgrade_symbol,
                self.center_x, self.center_y + 15,
                RESOURCE_WELL_OUTLINE_COLOR if self.assigned_node else (100, 100, 100, 100),
                font_size=14,
                anchor_x="center"
            )
