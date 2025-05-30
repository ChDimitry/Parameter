import arcade
import math
import random
from common import get_distance

class Enemy:
    def __init__(self, x, y, speed, health, damage):
        self.center_x = x
        self.center_y = y
        self.speed = speed
        self.health = health
        self.damage = damage
        self.radius = 5
        self.color = arcade.color.RED
        self.hit_particles = []  # list of (x, y, dx, dy, life)
        self.ground_particles = []  # list of (x, y, life)
        self.is_dying = False
        self.death_timer = 30
        self.dead = False

    def update_towards_base(self, main_base):
        dx = main_base.center_x - self.center_x
        dy = main_base.center_y - self.center_y
        dist = max(1, get_distance(main_base.center_x, self.center_x, main_base.center_y, self.center_y))
        self.center_x += self.speed * dx / dist
        self.center_y += self.speed * dy / dist

    def update(self, main_base):
        if self.is_dying:
            self.death_timer -= 1
            if self.death_timer <= 0:
                self.dead = True
        else:
            self.update_towards_base(main_base=main_base)

        # Update hit particles
        for i, (x, y, dx, dy, life) in enumerate(self.hit_particles):
            self.hit_particles[i] = (x + dx, y + dy, dx, dy, life - 1)
        self.hit_particles = [p for p in self.hit_particles if p[4] > 0]

        # Update ground particles
        self.ground_particles = [(x, y, life - 1) for x, y, life in self.ground_particles if life > 1]

    def draw(self):
        # Draw ground particles
        for x, y, life in self.ground_particles:
            alpha = max(10, int(255 * (life / 60)))
            color = arcade.color.DARK_BROWN[:3] + (alpha,)
            arcade.draw_circle_filled(x, y, 5, color)

        # Draw enemy
        if not self.is_dying:
            arcade.draw_circle_filled(self.center_x, self.center_y, self.radius, self.color)
        self.draw_hit()

    def draw_hit(self):
        for x, y, dx, dy, life in self.hit_particles:
            alpha = max(30, int(255 * (life / 15)))
            color = arcade.color.RED[:3] + (alpha,)
            arcade.draw_circle_filled(x, y, 2, color)

    def add_hit_particles(self, angle):
        for _ in range(6):
            offset_angle = angle + math.radians(0) + math.radians((random.random() - 0.1) * 40)
            speed = 2 + (random.random() * 1.5)
            dx = math.cos(offset_angle) * speed
            dy = math.sin(offset_angle) * speed
            self.hit_particles.append((self.center_x, self.center_y, dx, dy, 15))

        self.ground_particles.append((self.center_x, self.center_y, 60))

        if self.health <= 0 and not self.is_dying:
            self.start_dying()

    def start_dying(self):
        self.is_dying = True
        self.death_timer = 100
