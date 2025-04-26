import arcade
from config import PLAYER_SPEED, KILOMETER, BASE_COST
from weapon import Weapon
import math
from base import Base
import time
from common import get_distance

class Player:
    def __init__(self, x, y):
        self.center_x = x
        self.center_y = y
        self.radius = 5  # no longer used
        self.color = arcade.color.BLUE_YONDER
        self.weapon = Weapon(owner=self, damage=5, range=100, bullet_speed=20, fire_rate=0.3)
        self.distance_from_base = 0
        self.points = 0
        self.maximum_capable_distance = 3
        self.distance_left = 0

        self.player_speed = 0

        # Movement state
        self._momentum_x = 0
        self._momentum_y = 0
        self._momentum_gain = 0.1
        self._max_momentum = 2
        self.x_direction = 0
        self.y_direction = 0

        # Rectangle properties
        self.width = 16
        self.height = 16
        self.rotation = 0
        self.rotation_speed = 2



        self.bases = [Base(0, 0, previous_base=None)]
        self.last_base_spawn_time = 0
        self.base_spawn_cooldown = 0.5
        self.collecting_bases = 0

        self.active_flows = []
        self.active_collecting_wells = set()


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
            self.y_direction = 1
        elif key_s:
            self._momentum_y -= self._momentum_gain
            self._momentum_y = max(self._momentum_y, -self._max_momentum)
            self.y_direction = -1
        else:
            if self._momentum_y > 0:
                self._momentum_y = max(0, self._momentum_y - self._momentum_gain)
            elif self._momentum_y < 0:
                self._momentum_y = min(0, self._momentum_y + self._momentum_gain)

        # X
        if key_d:
            self._momentum_x += self._momentum_gain
            self._momentum_x = min(self._momentum_x, self._max_momentum)
            self.x_direction = 1
        elif key_a:
            self._momentum_x -= self._momentum_gain
            self._momentum_x = max(self._momentum_x, -self._max_momentum)
            self.x_direction = -1
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

    def try_spawn_base(self):
        if self.points >= BASE_COST and time.time() - self.last_base_spawn_time >= self.base_spawn_cooldown and self.distance_from_base < self.maximum_capable_distance:
            prev_base = self.bases[-1] if self.bases else None
            new_base = Base(self.center_x, self.center_y, previous_base=prev_base)
            self.bases.append(new_base)
            self.last_base_spawn_time = time.time()
            self.points -= BASE_COST

    def handle_input(self, keys):
        if keys.get(arcade.key.SPACE, False):
            self.try_spawn_base()

    def update(self, enemies, bullets, keys, wells):
        self.distance_from_base = (get_distance(self.center_x, self.bases[-1].center_x, self.center_y, self.bases[-1].center_y) / KILOMETER) if self.bases else (math.hypot(self.center_x, self.center_y) / KILOMETER)
        self.update_movement(keys)
        self.handle_input(keys)
        self.weapon.update(enemies)
        self.weapon.try_fire(enemies, bullets)

        for base in self.bases:
            base.update(enemies, bullets, wells)
                            
    def draw(self, enemies):
        # Line from base to player
        # Build a path from (0, 0) -> bases -> player
        points = [(0, 0)]

        # Add all base positions
        for base in self.bases:
            points.append((base.center_x, base.center_y))

        # Add player position at the end
        points.append((self.center_x, self.center_y))

        # Draw lines connecting all points
        arcade.draw_line_strip(
            points[:-1],
            (100, 255, 100, 50),  # Color
            3  # Line width
        )
        # Draw the last line from the last base to the player
        if self.distance_from_base <= self.maximum_capable_distance:
            arcade.draw_line(
                points[-2][0], points[-2][1],
                points[-1][0], points[-1][1],
                (100, 255, 100, 50),
                1  # Line width
            )
        # # Draw line from player to base
        # if self.bases:
        #     arcade.draw_line(
        #         0, 0,
        #         self.bases[0].center_x, self.bases[0].center_y,
        #         arcade.color.GRAY if self.distance_from_base < self.maximum_capable_distance else arcade.color.RED,
        #         1
        #     )

        if self.distance_from_base > self.maximum_capable_distance:
            arcade.draw_line(
                self.center_x, self.center_y,
                self.bases[-1].center_x, self.bases[-1].center_y,
                (0, 0, 0, 50),
                1
            )

        # # Create rect with proper values
        rect = arcade.Rect(
            left=0, right=0,
            bottom=0, top=0,
            width=self.width,
            height=self.height,
            x=self.center_x,
            y=self.center_y
        )

        arcade.draw_rect_filled(
            rect,
            self.color,
            tilt_angle=self.rotation
        )

        # Draw level text
        arcade.draw_text(
            f"{int(self.distance_from_base)} KM",
            self.center_x, self.center_y + 22,
            arcade.color.WHITE,
            font_size=10,
            anchor_x="center",
            anchor_y="center"
        )

        # Number of collecting bases
        # arcade.draw_text(
        #     f"{self.collecting_bases}",
        #     self.center_x, self.center_y - 22,
        #     arcade.color.WHITE,
        #     font_size=10,
        #     anchor_x="center",
        #     anchor_y="center"
        # )

        end_x = self.center_x + math.cos(math.radians(self.rotation)) * 20
        end_y = self.center_y + math.sin(math.radians(self.rotation)) * 20

        arcade.draw_line(self.center_x, self.center_y, end_x, end_y, arcade.color.RED, 1)

        self.weapon.draw(enemies)

        for base in self.bases:
            base.draw(enemies)
