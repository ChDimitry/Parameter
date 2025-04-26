import arcade
from config import KILOMETER
from weapon import Weapon
import math
import time
from common import get_distance

class Base:
    def __init__(self, x, y, previous_base=None, main_base=None):
        self.main_base = main_base
        self.center_x = x
        self.center_y = y
        self.color = arcade.color.GRAY
        self.weapon = Weapon(owner=self)
        self.distance_from_base = 0

        self.points = 0
        self.level = 1

        # Rectangle properties
        self.width = 20
        self.height = 20
        self.rotation = 0
        self.rotation_speed = 2

        self.is_collecting = False
        self.collected = 0
        self.previous_base = previous_base
        self.assigned_well = None

    def update(self, enemies, bullets, wells):
        self.distance_from_base = math.hypot(self.center_x, self.center_y)
        self.update_rotation(enemies)
        self.weapon.update(enemies)
        self.weapon.try_fire(enemies, bullets)

        if self.points >= 10:
            self.level += 1
            self.points = 0
            self.weapon.level_up(damage=1, range=10, bullet_speed=1, fire_rate=0.05)

        if self.is_collecting and self.previous_base:
            self.previous_base.is_collecting = True

        # Check if inside a resource well
        self.is_collecting = False
        for well in wells:
            if well.is_entity_inside(self) and well.capacity > 0:
                self.is_collecting = True
                self.assigned_well = well
                # self.previous_base.is_collecting = True 
                if not hasattr(well, 'last_transfer'):
                    well.last_transfer = 0
                if time.time() - well.last_transfer >= 1:
                    well.capacity -= 1
                    self.collected += 1
                    self.main_base.collected += 1
                    well.last_transfer = time.time()

            if well.capacity <= 0:
                well.active = False


    def update_rotation(self, enemies):
        # Automatically rotate to face the nearest enemy if possible
        if not enemies:
            return

        closest_enemy = None
        closest_dist = float('inf')

        for enemy in enemies:
            dist = math.hypot(
                enemy.center_x - self.center_x,
                enemy.center_y - self.center_y
            )
            if dist < closest_dist:
                closest_enemy = enemy
                closest_dist = dist

        if closest_enemy:
            dx = closest_enemy.center_x - self.center_x
            dy = closest_enemy.center_y - self.center_y
            target_angle_rad = math.atan2(dy, dx)
            target_angle_deg = math.degrees(target_angle_rad)

            angle_diff = (target_angle_deg - self.rotation + 180) % 360 - 180
            if abs(angle_diff) < self.rotation_speed:
                self.rotation = target_angle_deg
            else:
                self.rotation += self.rotation_speed * (1 if angle_diff > 0 else -1)
            self.rotation %= 360

    def draw(self, enemies):
        # Create rect with proper values
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

        # Draw barrel line for visual aiming
        end_x = self.center_x + math.cos(math.radians(self.rotation)) * 20
        end_y = self.center_y + math.sin(math.radians(self.rotation)) * 20

        arcade.draw_line(self.center_x, self.center_y, end_x, end_y, arcade.color.RED, 1)

        # Draw level text
        arcade.draw_text(
            f"Level: {self.level}",
            self.center_x, self.center_y + 22,
            arcade.color.WHITE,
            font_size=12,
            anchor_x="center",
            anchor_y="center"
        )
        
        # Draw collected resources text
        if not self.main_base:
            arcade.draw_text(
                f"Collected: {self.collected}",
                self.center_x, self.center_y - 22,
                arcade.color.WHITE,
                font_size=12,
                anchor_x="center",
                anchor_y="center"
            )

        arcade.draw_circle_filled(
            self.center_x,
            self.center_y,
            self.weapon.range,
            (100, 100, 255, 20)  # Very soft fill color
        )

        self.weapon.draw(enemies)
        
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