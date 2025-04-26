import arcade
import random
from config import SCREEN_WIDTH, SCREEN_HEIGHT, KILOMETER
from player import Player
from enemy import Enemy
import math
import arcade.camera
from common import get_distance

class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Outer Parameter")
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        self.player = None
        self.enemies = []
        self.bullets = []
        self._keys = {}

        self.time_passed = 0

        self.camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()

    def setup(self):
        self.player = Player(0, 0)

    def on_draw(self):
        self.clear()
        # Draw world
        self.camera.use()

        self.player.draw()
        
        for enemy in self.enemies:
            enemy.draw()

        # BULLETS DRAW
        for bullet in self.bullets:
            arcade.draw_circle_filled(bullet["x"], bullet["y"], bullet["radius"], bullet["color"])

        arcade.draw_circle_outline(
            self.player.center_x,
            self.player.center_y,
            200,
            arcade.color.BLUE_SAPPHIRE,
            1
        )

        arcade.draw_circle_outline(
            0,
            0,
            50,
            arcade.color.BLUE_SAPPHIRE,
            1
        )

        # Draw UI
        self.gui_camera.use()
        distance_px = self.player.distance_from_base
        distance_km = int(distance_px / KILOMETER)
        arcade.draw_text(
            f"{distance_km} KM",
            10, SCREEN_HEIGHT - 30,
            arcade.color.WHITE,
            20
        )

        # draw players position
        arcade.draw_text(
            f"({int(self.player.center_x)}, {int(self.player.center_y)})",
            10, SCREEN_HEIGHT - 60,
            arcade.color.WHITE,
            20
        )

        # draw player points
        arcade.draw_text(
            f"{self.player.points}",
            10, SCREEN_HEIGHT - 90,
            arcade.color.WHITE,
            20
        )
        
        

    def on_update(self, delta_time):
        self.player.update(self.enemies, self.bullets, self._keys)

        for enemy in self.enemies:
            enemy.update_towards_player(self.player)

        # BULLETS UPDATE
        for bullet in self.bullets:
            bullet["x"] += bullet["dx"]
            bullet["y"] += bullet["dy"]

        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                dist = get_distance(bullet["x"], enemy.center_x, bullet["y"], enemy.center_y)
                if dist < bullet["radius"] + enemy.radius:
                    # Check if the bullet hits the enemy
                    enemy.health -= bullet["damage"]
                    if enemy.health <= 0:
                        self.enemies.remove(enemy)
                        self.player.points += 1
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break

        self.spawn_enemies()
        self.camera.position = (self.player.center_x, self.player.center_y)
        self.time_passed += 0.0001

    def spawn_enemies(self):
        if len(self.enemies) < 20:
            px = self.player.center_x
            py = self.player.center_y
            margin = 900

            side = random.choice(['top', 'bottom', 'left', 'right'])

            if side == 'top':
                x = random.randint(int(px - margin), int(px + margin))
                y = py + (margin - 300)
            elif side == 'bottom':
                x = random.randint(int(px - margin), int(px + margin))
                y = py - (margin - 300)
            elif side == 'left':
                x = px - margin
                y = random.randint(int(py - margin), int(py + margin))
            else:  # right
                x = px + margin
                y = random.randint(int(py - margin), int(py + margin))

            self.enemies.append(Enemy(x, y, speed=1, health=10, damage=5))


    def on_key_press(self, symbol, modifiers):
        self._keys[symbol] = True

    def on_key_release(self, symbol, modifiers):
        self._keys[symbol] = False

if __name__ == "__main__":
    window = GameWindow()
    window.setup()
    arcade.run()