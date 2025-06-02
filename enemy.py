import arcade
import math
import random
from common import get_distance
from constants import ENEMY_COLOR, ENEMY_HIT_COLOR

class Enemy:
    def __init__(self, x, y, speed, health, damage):
        self.center_x = x
        self.center_y = y
        self.speed = speed
        self.max_health = health
        self.current_health = health
        self.damage = damage
        self.radius = 5
        self.color = ENEMY_COLOR
        self.hit_particles = []  # list of (x, y, dx, dy, life)
        self.ground_particles = []  # list of (x, y, life)
        self.is_dying = False
        self.death_timer = 30
        self.dead = False


        self.scrap_dropped = False
        self.scrap_position = None
        self._scrap_velocity = (0.0, 0.0)
        self._scrap_acceleration = 0.0

    def update_towards_base(self, main_base):
        dx = main_base.center_x - self.center_x
        dy = main_base.center_y - self.center_y
        dist = max(1, get_distance(main_base.center_x, self.center_x, main_base.center_y, self.center_y))
        self.center_x += self.speed * dx / dist
        self.center_y += self.speed * dy / dist

    def update(self, main_base, player=None):
        if self.is_dying:
            if not self.scrap_dropped:
                # Drop the scrap once
                self.scrap_position = (self.center_x, self.center_y)
                self.scrap_dropped = True
            else:
                if player and self.scrap_position:
                    sx, sy = self.scrap_position
                    px, py = player.center_x, player.center_y
                    dx = px - sx
                    dy = py - sy
                    dist = math.hypot(dx, dy)

                    if dist > 10:
                        # Desired direction toward player
                        dir_x = dx / dist
                        dir_y = dy / dist

                        # Gradually increase acceleration over time
                        accel_growth = 0.4
                        self._scrap_acceleration = min(self._scrap_acceleration + accel_growth, 50)

                        # Desired velocity increases with acceleration
                        desired_speed = self._scrap_acceleration
                        desired_vx = dir_x * desired_speed
                        desired_vy = dir_y * desired_speed

                        # Current velocity
                        vx, vy = self._scrap_velocity

                        # Steering force
                        steer_strength = 0.2
                        vx += (desired_vx - vx) * steer_strength
                        vy += (desired_vy - vy) * steer_strength

                        max_speed = 20
                        speed = math.hypot(vx, vy)
                        if speed > max_speed:
                            scale = max_speed / speed
                            vx *= scale
                            vy *= scale

                        # Update position
                        sx += vx
                        sy += vy
                        self.scrap_position = (sx, sy)
                        self._scrap_velocity = (vx, vy)
                    else:
                        player.scrap += 1
                        self.dead = True
                        self.scrap_position = None
                        self._scrap_velocity = (0.0, 0.0)
                        self._scrap_acceleration = 0.0


        else:
            self.update_towards_base(main_base=main_base)

        # Update particles
        for i, (x, y, dx, dy, life) in enumerate(self.hit_particles):
            self.hit_particles[i] = (x + dx, y + dy, dx, dy, life - 1)
        self.hit_particles = [p for p in self.hit_particles if p[4] > 0]
        self.ground_particles = [(x, y, life - 1) for x, y, life in self.ground_particles if life > 1]


    def draw(self):
        # Draw scrap if dropped
        if self.scrap_dropped and self.scrap_position:
            sx, sy = self.scrap_position
            arcade.draw_circle_filled(sx, sy, 4, arcade.color.GRAY)

        # Draw ground particles
        for x, y, life in self.ground_particles:
            alpha = max(10, int(255 * (life / 60)))
            color = ENEMY_COLOR[:3] + (alpha,)
            arcade.draw_circle_filled(x, y, 5, color)

        # Draw enemy
        if not self.is_dying:
            arcade.draw_circle_filled(self.center_x, self.center_y, self.radius, self.color)
        self.draw_hit()

        # Draw health bar as a shrinking horizontal line (centered above enemy)
        if self.current_health > 0:
            max_bar_width = 20  # Wider for visibility
            bar_height = 5
            health_ratio = max(0, self.current_health / self.max_health)
            current_bar_width = max_bar_width * health_ratio

            # Compute bar edges centered on the enemy
            left_x = self.center_x - max_bar_width / 2
            right_x = left_x + current_bar_width
            y = self.center_y + 12  # Position above the enemy

            # Draw background HP bar
            arcade.draw_line(
                self.center_x - max_bar_width / 2,
                y,
                self.center_x + max_bar_width / 2,
                y,
                (50, 50, 50),  # dark gray background
                line_width=bar_height
            )

            # Foreground HP bar
            arcade.draw_line(
                left_x,
                y,
                right_x,
                y,
                ENEMY_COLOR,
                line_width=bar_height
            )

    def draw_hit(self):
        for x, y, dx, dy, life in self.hit_particles:
            alpha = max(30, int(255 * (life / 15)))
            color = ENEMY_COLOR[:3] + (alpha,)
            arcade.draw_circle_filled(x, y, 2, color)

    def add_hit_particles(self, angle):
        for _ in range(10):
            offset_angle = angle + math.radians(0) + math.radians((random.random() - 0.1) * 30)
            speed = 2 + (random.random() * 5)
            dx = math.cos(offset_angle) * speed
            dy = math.sin(offset_angle) * speed
            self.hit_particles.append((self.center_x, self.center_y, dx, dy, 15))

        if self.current_health <= 0 and not self.is_dying:
            self.ground_particles.append((self.center_x, self.center_y, 60))
            self.start_dying()

    def start_dying(self):
        self.is_dying = True
        self.death_timer = 100
