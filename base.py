import arcade
from weapon import Weapon
import math

class Base:
    def __init__(self, x, y, previous_base=None, main_base=None, color=arcade.color.GRAY, player=None):
        self.player = player
        self.main_base = main_base
        self.center_x = x
        self.center_y = y
        self.color = color
        self.weapon = Weapon(owner=self, damage=5, range=100, bullet_speed=5, fire_rate=1)
        self.distance_from_base = 0

        self.scrap = 0
        self.level = 1

        # Rectangle properties
        self.width = 20
        self.height = 20
        self.rotation = 0
        self.rotation_speed = 2

        self.is_collecting = False
        self.collected_resources = 0
        self.collection_rate = 5

    def update(self, enemies, wells):
        self.distance_from_base = math.hypot(self.center_x, self.center_y)
        self.update_rotation(enemies)
        self.weapon.update(enemies, player=self.player)
        self.weapon.try_fire(enemies)

        if self.collected_resources >= 50:
            self.level += 1
            self.collected_resources = 0
            self.weapon.level_up(damage=1, range=10, bullet_speed=0, fire_rate=0.05)

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

    def draw(self):
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

        # Draw level text
        arcade.draw_text(
            f"Level: {self.level}",
            self.center_x, self.center_y + 22,
            arcade.color.WHITE,
            font_size=12,
            anchor_x="center",
            anchor_y="center"
        )

        # Base range
        arcade.draw_circle_filled(
            self.center_x,
            self.center_y,
            self.weapon.range,
            (100, 100, 255, 20)  # Very soft fill color
        )

        self.weapon.draw()
        
        # if self.previous_base and self.is_collecting:
        #     flow_speed = 50
        #     flow_spacing = 50
        #     elapsed = time.time() % 1000
        #     flow_offset = (elapsed * flow_speed) % flow_spacing

        #     start_x, start_y = self.center_x, self.center_y
        #     end_x, end_y = self.previous_base.center_x, self.previous_base.center_y

        #     segment_length = math.hypot(end_x - start_x, end_y - start_y)
        #     if segment_length > 0:
        #         direction_x = (end_x - start_x) / segment_length
        #         direction_y = (end_y - start_y) / segment_length

        #         steps = int(segment_length // flow_spacing)
        #         for s in range(steps):
        #             pos = (flow_offset + s * flow_spacing)
        #             if pos > segment_length:
        #                 continue
        #             dot_x = start_x + direction_x * pos
        #             dot_y = start_y + direction_y * pos
        #             arcade.draw_circle_filled(dot_x, dot_y, 4, arcade.color.LIGHT_GREEN)