import arcade
import math
import time
from dataclasses import dataclass
from config import KILOMETER, BASE_COST
from constants import NODE_CONNECTION_LINE_COLOR, PLAYER_COLOR
from weapon import Weapon
from base import Base
from node import Node
from common import get_distance
from typing import Tuple

@dataclass
class Flow:
    x1: float
    y1: float
    x2: float
    y2: float
    width: float
    color: Tuple[int, int, int, int]

class Player:
    def __init__(self, x, y, main_base: Base):
        # Position and appearance
        self.center_x = x
        self.center_y = y
        self.width = 16
        self.height = 16
        self.rotation = 0
        self.rotation_speed = 2
        self.color = PLAYER_COLOR

        # Weapon system and level
        self.weapon = Weapon(owner=self, damage=2, range=100, bullet_speed=7, fire_rate=0.5)
        self.level = 0

        # Movement and momentum (private)
        self._momentum_x = 0
        self._momentum_y = 0
        self._momentum_gain = 0.1
        self._max_momentum = 2
        self._x_direction_flag = 0
        self._y_direction_flag = 0
        self._player_speed = 0

        # Resource management
        self.scrap = 0
        self._collecting_bases = 0
        self._active_collecting_nodes = set()
        self._able_to_spawn = True

        # Node connection and placement logic
        self._maximum_node_distance = 1.5
        self._minimum_node_distance = 1
        self._distance_from_node = 0
        self._closest_node = None
        self._current_node_id = 0

        # Base and node spawning
        self.main_base = main_base
        self.main_base.main_base = self.main_base
        self._last_base_spawn_time = 0
        self._base_spawn_cooldown = 0.5

    def update_movement(self, keys):
        dx = dy = 0

        key_w = keys.get(arcade.key.W, False)
        key_s = keys.get(arcade.key.S, False)
        key_a = keys.get(arcade.key.A, False)
        key_d = keys.get(arcade.key.D, False)

        # Y
        if key_w:
            self._momentum_y += self._momentum_gain
            self._momentum_y = min(self._momentum_y, self._max_momentum)
            self._y_direction_flag = 1
        elif key_s:
            self._momentum_y -= self._momentum_gain
            self._momentum_y = max(self._momentum_y, -self._max_momentum)
            self._y_direction_flag = -1
        else:
            if self._momentum_y > 0:
                self._momentum_y = max(0, self._momentum_y - self._momentum_gain)
            elif self._momentum_y < 0:
                self._momentum_y = min(0, self._momentum_y + self._momentum_gain)

        # X
        if key_d:
            self._momentum_x += self._momentum_gain
            self._momentum_x = min(self._momentum_x, self._max_momentum)
            self._x_direction_flag = 1
        elif key_a:
            self._momentum_x -= self._momentum_gain
            self._momentum_x = max(self._momentum_x, -self._max_momentum)
            self._x_direction_flag = -1
        else:
            if self._momentum_x > 0:
                self._momentum_x = max(0, self._momentum_x - self._momentum_gain)
            elif self._momentum_x < 0:
                self._momentum_x = min(0, self._momentum_x + self._momentum_gain)

        dx += self._momentum_x
        dy += self._momentum_y

        self.player_speed = math.hypot(dx, dy)

        # Normalize diagonal movement speed
        max_speed = max(abs(self._momentum_x), abs(self._momentum_y), self._max_momentum)
        if self.player_speed > max_speed:
            factor = max_speed / self.player_speed
            dx *= factor
            dy *= factor
            self.player_speed = max_speed

        self.center_x += dx
        self.center_y += dy

        # ROTATION
        if dx != 0 or dy != 0:
            target_angle_rad = math.atan2(dy, dx)
            target_angle_deg = math.degrees(target_angle_rad)

            angle_diff = (target_angle_deg - self.rotation + 180) % 360 - 180
            if abs(angle_diff) < self.rotation_speed:
                self.rotation = target_angle_deg
            else:
                self.rotation += self.rotation_speed * (1 if angle_diff > 0 else -1)
            self.rotation %= 360

    def try_spawn_node(self, nodes):
        # Check if player can spawn a new node
        if self.scrap >= BASE_COST and \
        time.time() - self._last_base_spawn_time >= self._base_spawn_cooldown and \
        self.distance_from_node < self._maximum_node_distance and \
        self.distance_from_node > self._minimum_node_distance:
            # Create a new node at the player's position
            closest_node = self.closest_node if self.closest_node else self.main_base
            new_node = Node(self._current_node_id, self.center_x, self.center_y, closest_node=closest_node, main_base=self.main_base)
            self._current_node_id += 1

            nodes.append(new_node)
            self.last_base_spawn_time = time.time()
            self.scrap -= BASE_COST

    def handle_input(self, keys, nodes):
        # Handle movement keys
        if keys.get(arcade.key.SPACE, False) and self._able_to_spawn:
            self.try_spawn_node(nodes)
            
        self.update_movement(keys)

    def update_closest_node(self, nodes):
        self.closest_node = min(nodes[1:], key=lambda node: get_distance(self.center_x, node.center_x, self.center_y, node.center_y))

    def update(self, enemies, keys, obstacles, nodes):
        # for obstacle in obstacles:
        #     if obstacle.is_entity_inside(self):
        #         self.able_to_spawn = False
        #     else:
        #         self.able_to_spawn = True

        self.update_closest_node(nodes)
        # Calculate distance from the closest node
        self.distance_from_node = get_distance(
            self.center_x, self.closest_node.center_x,
            self.center_y, self.closest_node.center_y
        ) / KILOMETER

        self.handle_input(keys, nodes)
        self.weapon.update(enemies)
        self.weapon.try_fire(enemies)

    def draw(self):
        # Draw a line to the closest node if it exists
        if self.closest_node:
            arcade.draw_line(
                self.center_x, self.center_y,
                self.closest_node.center_x, self.closest_node.center_y,
                NODE_CONNECTION_LINE_COLOR if (self.distance_from_node < self._maximum_node_distance and self.distance_from_node > self._minimum_node_distance) else (0, 0, 0, 50), 1
            )

        # Draw the player as a rectangle
        rect = arcade.Rect(0, 0, 0, 0, self.width, self.height, self.center_x, self.center_y)
        arcade.draw_rect_filled(rect, self.color, tilt_angle=self.rotation)

        # Draw the weapon
        self.weapon.draw()

