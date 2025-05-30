import arcade
from weapon import Weapon
import math
import time

class Node:
    def __init__(self, x, y, previous_base=None, main_base=None, color=arcade.color.BLUE_SAPPHIRE, player=None):
        self.player = player
        self.main_base = main_base
        self.center_x = x
        self.center_y = y
        self.color = color
        self.weapon = Weapon(owner=self)
        self.distance_from_base = 0

        self.scrap = 0
        self.level = 1

        # Rectangle properties
        self.width = 20
        self.height = 20

        self.is_collecting = False
        self.collected = 0
        self.collection_rate = 5
        self.previous_base = previous_base
        self.assigned_well = None

    def update(self, enemies, wells):
        self.distance_from_base = math.hypot(self.center_x, self.center_y)
        # self.update_rotation(enemies)
        self.weapon.update(enemies, player=self.player)
        self.weapon.try_fire(enemies)

        if self.is_collecting and self.previous_base:
            self.previous_base.is_collecting = True

        # Check if inside a resource well
        self.is_collecting = False
        for well in wells:
            if well.is_entity_inside(self) and well.capacity > 0:
                self.is_collecting = True
                self.assigned_well = well
                # self.previous_base.is_collecting = True 
                if time.time() - well.last_transfer >= self.collection_rate:
                    well.capacity -= 1
                    # self.collected += 1
                    self.main_base.collected_resources += 1
                    well.last_transfer = time.time()

            if well.capacity <= 0:
                well.active = False

    def draw(self):
        # Draw cicle for the node
        arcade.draw_circle_filled(
            self.center_x, self.center_y, 
            self.width / 2, 
            self.color
        )
        self.weapon.draw()
        
        if self.previous_base and self.is_collecting:
            flow_speed = 50
            flow_spacing = 50
            elapsed = time.time() % 1000
            flow_offset = (elapsed * flow_speed) % flow_spacing

            start_x, start_y = self.center_x, self.center_y
            end_x, end_y = self.previous_base.center_x, self.previous_base.center_y

            segment_length = math.hypot(end_x - start_x, end_y - start_y)
            if segment_length > 0:
                direction_x = (end_x - start_x) / segment_length
                direction_y = (end_y - start_y) / segment_length

                steps = int(segment_length // flow_spacing)
                for s in range(steps):
                    pos = (flow_offset + s * flow_spacing)
                    if pos > segment_length:
                        continue
                    dot_x = start_x + direction_x * pos
                    dot_y = start_y + direction_y * pos
                    arcade.draw_circle_filled(dot_x, dot_y, 4, arcade.color.LIGHT_GREEN)