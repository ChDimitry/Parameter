import arcade
import math
import time

class Weapon:
    def __init__(self, owner, damage=5, range=200, bullet_speed=10, fire_rate=0.3):
        self.owner = owner
        self.damage = damage
        self.range = range
        self.bullet_speed = bullet_speed
        self.fire_rate = fire_rate
        self.last_shot_time = 0

        self.angle = 0

    def can_fire(self):
        return time.time() - self.last_shot_time >= self.fire_rate

    def try_fire(self, enemies, bullets):
        if not self.can_fire():
            return

        for enemy in enemies:
            dist = math.hypot(
                enemy.center_x - self.owner.center_x,
                enemy.center_y - self.owner.center_y
            )
            if dist < self.range:
                self.angle = math.atan2(enemy.center_y - self.owner.center_y,
                                   enemy.center_x - self.owner.center_x)
                bullets.append({
                    "x": self.owner.center_x,
                    "y": self.owner.center_y,
                    "dx": math.cos(self.angle) * self.bullet_speed,
                    "dy": math.sin(self.angle) * self.bullet_speed,
                    "radius": 3,
                    "damage": self.damage,
                    "color": arcade.color.YELLOW,
                })
                self.last_shot_time = time.time()
                break

    def draw(self):
        end_x = self.owner.center_x + math.cos(self.angle) * 20
        end_y = self.owner.center_y + math.sin(self.angle) * 20

        arcade.draw_line(
            self.owner.center_x,
            self.owner.center_y,
            end_x,
            end_y,
            arcade.color.YELLOW,
            1
        )
