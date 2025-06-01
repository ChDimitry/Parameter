import arcade
import math
import time
from common import get_distance
from dataclasses import dataclass
from typing import Tuple, Optional
import random
from constants import BULLET_COLOR


@dataclass
class Bullet:
    x: float
    y: float
    dx: float
    dy: float
    radius: float
    damage: int
    color: Tuple[int, int, int, int]
    lifespan: float = 1.5
    target: Optional[object] = None
    trail: list = None  # list of (x, y, alpha)

    def __post_init__(self):
        self.trail = []

class Weapon:
    def __init__(self, owner, damage=5, range=100, bullet_speed=5, fire_rate=1):
        self.owner = owner
        self.damage = damage
        self.range = range
        self.bullet_speed = bullet_speed
        self.fire_rate = fire_rate
        self.last_shot_time = 0
        self.angle = 0
        self.bullets = []

        self.current_target = None

    def can_fire(self):
        return time.time() - self.last_shot_time >= self.fire_rate

    def try_fire(self, enemies):
        if not self.can_fire():
            return

        for enemy in enemies:
            dist = get_distance(
                self.owner.center_x, enemy.center_x,
                self.owner.center_y, enemy.center_y
            )
            # Check if the enemy is within range and not dying
            if dist < self.range and not enemy.is_dying and self.current_target != enemy:
                self.current_target = enemy
                self.angle = math.atan2(
                    enemy.center_y - self.owner.center_y,
                    enemy.center_x - self.owner.center_x
                )

                # Apply angle offset for visual arc
                angle_offset = math.radians(random.uniform(-45, 45))
                firing_angle = self.angle + angle_offset

                self.bullets.append(
                    Bullet(
                        x=self.owner.center_x,
                        y=self.owner.center_y,
                        dx=math.cos(firing_angle) * self.bullet_speed,
                        dy=math.sin(firing_angle) * self.bullet_speed,
                        radius=4,
                        damage=self.damage,
                        color=BULLET_COLOR,
                        target=self.current_target
                    )
                )

                self.last_shot_time = time.time()
                break

    def level_up(self, damage, range, bullet_speed, fire_rate):
        self.damage += damage
        self.range += range
        self.bullet_speed += bullet_speed
        self.fire_rate = max(0.05, self.fire_rate - fire_rate)

    def update(self, enemies, player):
        for bullet in self.bullets:
            if bullet.target and bullet.lifespan > 0:
                # Homing toward target
                to_target_x = bullet.target.center_x - bullet.x
                to_target_y = bullet.target.center_y - bullet.y
                distance = math.hypot(to_target_x, to_target_y)

                if distance > 1:
                    to_target_x /= distance
                    to_target_y /= distance

                    steer_strength = 0.1
                    bullet.dx = (1 - steer_strength) * bullet.dx + steer_strength * to_target_x * self.bullet_speed 
                    bullet.dy = (1 - steer_strength) * bullet.dy + steer_strength * to_target_y * self.bullet_speed

            bullet.x += bullet.dx
            bullet.y += bullet.dy
            bullet.lifespan -= 1 / 60

            # Save current position to trail
            bullet.trail.append((bullet.x, bullet.y, int(255 * bullet.lifespan / 7.0)))
            if len(bullet.trail) > 7:
                bullet.trail.pop(0)

        for bullet in self.bullets[:]:
            if bullet.lifespan <= 0:
                self.bullets.remove(bullet)
                continue

            for enemy in enemies[:]:
                dist = get_distance(bullet.x, enemy.center_x, bullet.y, enemy.center_y)
                if dist < bullet.radius + enemy.radius:
                    enemy.health -= bullet.damage
                    enemy.add_hit_particles(math.atan2(bullet.dy, bullet.dx))

                    # When the enemy dies self.current_target will become None and the owner will search for a new enemy to shoot

                    if enemy.health <= 0:
                        player.scrap += 1
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break

    def draw(self):
        for bullet in self.bullets:
            # Draw trail
            for tx, ty, alpha in bullet.trail:
                size = 2
                color = BULLET_COLOR[:3] + (max(10, alpha),)
                arcade.draw_circle_filled(tx, ty, size, color, num_segments=10)

            # Draw main bullet
            arcade.draw_circle_filled(bullet.x, bullet.y, bullet.radius, bullet.color)
            # arcade.draw_circle_filled(bullet.x, bullet.y, bullet.radius + 1, (255, 255, 255, 100))
