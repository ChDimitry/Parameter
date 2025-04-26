import arcade
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

    def update_towards_player(self, player):
        dx = player.center_x - self.center_x
        dy = player.center_y - self.center_y
        dist = max(1, get_distance(player.center_x, self.center_x, player.center_y , self.center_y))
        self.center_x += self.speed * dx / dist
        self.center_y += self.speed * dy / dist

    def draw(self):
        arcade.draw_circle_filled(self.center_x, self.center_y, self.radius, self.color)
