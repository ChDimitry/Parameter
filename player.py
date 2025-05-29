import arcade
import math
import time
from dataclasses import dataclass
from config import PLAYER_SPEED, KILOMETER, BASE_COST
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
    def __init__(self, x, y):
        self.center_x = x
        self.center_y = y
        self.color = arcade.color.BLUE_YONDER
        self.weapon = Weapon(owner=self, damage=5, range=100, bullet_speed=5, fire_rate=0.5)
        self.distance_from_base = 0
        self.scrap = 0
        self.maximum_capable_distance = 3
        self.player_speed = 0

        # Momentum properties
        self._momentum_x = 0
        self._momentum_y = 0
        self._momentum_gain = 0.1
        self._max_momentum: float = 2
        self._x_direction_flag = 0
        self._y_direction_flag = 0

        self.width = 16
        self.height = 16
        self.rotation = 0
        self.rotation_speed = 2

        # Initialize player nodes
        self.nodes: list = [Base(0, 0, color=arcade.color.GOLD, player=self)]
        self.main_base = self.nodes[0]
        self.main_base.main_base = self.main_base

        self.last_base_spawn_time = 0
        self.base_spawn_cooldown = 0.5
        self.collecting_bases = 0

        self.active_flows: list[Flow] = []
        self.active_collecting_nodes = set()

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

    def try_spawn_node(self, wells):
        # Check if player can spawn a new node
        if self.scrap >= BASE_COST and time.time() - self.last_base_spawn_time >= self.base_spawn_cooldown and self.distance_from_base < self.maximum_capable_distance:
            prev_base = self.nodes[-1] if self.nodes else None
            new_node = Node(self.center_x, self.center_y, previous_base=prev_base, main_base=self.nodes[0], color=arcade.color.BABY_BLUE, player=self)

            # Check if new base is within any well's radius
            for well in wells:
                if get_distance(new_node.center_x, well.center_x, new_node.center_y, well.center_y) < well.radius:
                    new_node.is_collecting = True
                    new_node.assigned_well = well
                    break

            self.nodes.append(new_node)
            self.last_base_spawn_time = time.time()
            self.scrap -= BASE_COST

    def handle_input(self, keys, wells):
        # Handle movement keys
        if keys.get(arcade.key.SPACE, False):
            self.try_spawn_node(wells)
            
        self.update_movement(keys)

    def update(self, enemies, bullets, keys, wells):
        self.distance_from_base = get_distance(
            self.center_x, self.nodes[-1].center_x,
            self.center_y, self.nodes[-1].center_y
        ) / KILOMETER

        self.handle_input(keys, wells)
        self.weapon.update(enemies, self)
        self.weapon.try_fire(enemies, bullets)

        self.active_flows.clear()

        for node in self.nodes:
            # Update each node's state only it is collecting
            if node.is_collecting:
                node.update(enemies, bullets, wells)
                self.active_collecting_nodes.add(node)
                # Add flow
                self.active_flows.append(
                    Flow(
                    x1=node.center_x,
                    y1=node.center_y,
                    x2=node.main_base.center_x,
                    y2=node.main_base.center_y,
                    width=2,
                    color=arcade.color.LIGHT_BLUE))
            else:
                self.active_collecting_nodes.discard(node)

    def draw(self):
        points = [(0, 0)] + [(b.center_x, b.center_y) for b in self.nodes] + [(self.center_x, self.center_y)]
        arcade.draw_line_strip(points[:-1], (100, 255, 100, 50), 3)

        if self.distance_from_base <= self.maximum_capable_distance:
            arcade.draw_line(points[-2][0], points[-2][1], points[-1][0], points[-1][1], (100, 255, 100, 50), 1)
        else:
            arcade.draw_line(self.center_x, self.center_y, self.nodes[-1].center_x, self.nodes[-1].center_y, (0, 0, 0, 50), 1)

        rect = arcade.Rect(0, 0, 0, 0, self.width, self.height, self.center_x, self.center_y)
        arcade.draw_rect_filled(rect, self.color, tilt_angle=self.rotation)

        end_x = self.center_x + math.cos(math.radians(self.rotation)) * 20
        end_y = self.center_y + math.sin(math.radians(self.rotation)) * 20
        arcade.draw_line(self.center_x, self.center_y, end_x, end_y, arcade.color.RED, 1)

        self.weapon.draw()

        for node in self.nodes:
            node.draw()
