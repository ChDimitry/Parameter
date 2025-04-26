import arcade
import math
import time
from common import get_distance

class Weapon:
    def __init__(self, owner, damage=5, range=200, bullet_speed=10, fire_rate=0.3):
        self.owner = owner
        self.damage = damage
        self.range = range
        self.bullet_speed = bullet_speed
        self.fire_rate = fire_rate
        self.last_shot_time = 0

        self.angle = 0


        self.bullets = []

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
                self.bullets.append({
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

    def update(self, enemies):
        # BULLETS UPDATE
        for bullet in self.bullets:
            bullet["x"] += bullet["dx"]
            bullet["y"] += bullet["dy"]

        for bullet in self.bullets[:]:
            for enemy in enemies[:]:
                dist = get_distance(bullet["x"], enemy.center_x, bullet["y"], enemy.center_y)
                if dist < bullet["radius"] + enemy.radius:
                    # Check if the bullet hits the enemy
                    enemy.health -= bullet["damage"]
                    if enemy.health <= 0:
                        enemies.remove(enemy)
                        self.owner.points += 1
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break


    def draw(self, enemies):
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

                # BULLETS DRAW
        for bullet in self.bullets:
            arcade.draw_circle_filled(bullet["x"], bullet["y"], bullet["radius"], bullet["color"])