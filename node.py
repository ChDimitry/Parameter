import arcade
from weapon import Weapon
from constants import NODE_CONNECTION_LINE_COLOR, RESOURCE_FLOW_COLOR, NODE_GLOW_COLOR
import math
import time
from common import is_entity_inside

class Node:
    def __init__(self, _id,  x, y, closest_node=None, main_base=None, player=None):
        self._id = _id
        self.player = player
        self.main_base = main_base
        self.center_x = x
        self.center_y = y
        # self.weapon = Weapon(owner=self)

        self.scrap = 0
        self.level = 1

        self.width = 10

        self.is_collecting = False
        self.collected = 0

        self.closest_node = closest_node
        self.assigned_well = None
        self.is_inside_well = False

        self.link_length = closest_node.link_length + 1

        self.collection_rate = self.link_length # Collection rate based on link length

    def update(self, enemies, wells):
        # If node is collecting, start updating and shooting and activate the closest node
        if self.is_collecting:
            self.closest_node.is_collecting = True

        else:
            if not self.closest_node.assigned_well:
                self.closest_node.is_collecting = False
        
        if self.assigned_well:
            self.closest_node.assigned_well = self.assigned_well

        # Check if inside a resource well
        for well in wells:
            if is_entity_inside(entity=well, object=self, radius=well.radius) and well.active:
                self.is_inside_well = True
                self.is_collecting = True # Start collecting if inside a well
                self.assigned_well = well # Assign the well to this node
                well.assigned_node = self # Assign this node to the well
                if time.time() - well.last_transfer >= self.collection_rate:
                    well.capacity -= 1
                    self.main_base.collected_resources += 1
                    well.last_transfer = time.time()

            if well.capacity <= 0:
                well.active = False

        # This code is silly
        # TODO: Refactor this logic to be more efficient
        if self.assigned_well and self.assigned_well.capacity <= 0 and self.is_collecting:
            self.is_collecting = False

        if self.assigned_well and self.assigned_well.capacity <= 0 and self.is_inside_well:
            self.main_base.weapon.level_up(*self.assigned_well.upgrade_attributes)
            self.main_base.upgrades.append(self.assigned_well.upgrade_symbol)
            self.is_inside_well = False

    def draw(self):    
        if self.is_collecting:
            glow_color = NODE_GLOW_COLOR

            # Glow when collecting
            for i in range(3, 0, -1):
                arcade.draw_circle_filled(
                    self.center_x, self.center_y,
                    self.width / 2 + i * 2.5,  # Slightly wider rings for a diffused effect
                    NODE_GLOW_COLOR[:3] + (2.5 * i,)  # Softer alpha per layer
                )
        else:
            glow_color = (100, 100, 100, 50)


        # --- Core Node ---
        arcade.draw_circle_filled(
            self.center_x, self.center_y,
            self.width / 2,
            glow_color
        )

        # --- Collection Line and Flow ---
        if self.closest_node:
            if self.is_collecting:
                flow_speed = 50
                flow_spacing = 50
                elapsed = time.time() % 1000
                flow_offset = (elapsed * flow_speed) % flow_spacing

                start_x, start_y = self.center_x, self.center_y
                end_x, end_y = self.closest_node.center_x, self.closest_node.center_y

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
                        arcade.draw_circle_filled(dot_x, dot_y, 4, RESOURCE_FLOW_COLOR)

            # Draw a line to the closest node
            arcade.draw_line(
                self.center_x, self.center_y,
                self.closest_node.center_x, self.closest_node.center_y,
                NODE_CONNECTION_LINE_COLOR, 2
            )
