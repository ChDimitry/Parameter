import arcade
from config import PLAYER_SPEED, KILOMETER
from weapon import Weapon
import math

class Player:
    def __init__(self, x, y):
        self.center_x = x
        self.center_y = y
        self.radius = 5  # no longer used
        self.color = arcade.color.BLUE_YONDER
        self.weapon = Weapon(owner=self)
        self.distance_from_base = 0
        self.points = 0
        self.maximum_capable_distance = 2
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
        self.width = 12
        self.height = 6
        self.rotation = 0
        self.rotation_speed = 2

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

    def update(self, enemies, bullets, keys):
        self.distance_from_base = math.hypot(self.center_x, self.center_y)
        self.update_movement(keys)
        self.weapon.try_fire(enemies, bullets)

    def draw(self):
        # Line from base to player
        arcade.draw_line(
            0, 0,
            self.center_x, self.center_y,
            arcade.color.BLUE_SAPPHIRE,
            self.maximum_capable_distance - int(self.distance_from_base / KILOMETER)
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

        end_x = self.center_x + math.cos(math.radians(self.rotation)) * 20
        end_y = self.center_y + math.sin(math.radians(self.rotation)) * 20

        arcade.draw_line(self.center_x, self.center_y, end_x, end_y, arcade.color.RED, 1)

        self.weapon.draw()