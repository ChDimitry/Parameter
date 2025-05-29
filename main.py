import arcade
import random
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from player import Player
from enemy import Enemy
from resource_well import ResourceWell
import arcade.camera
from common import get_distance
import math
from uiPanel import UIPanel

class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Outer Parameter")
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        self.player = None
        self.enemies = []
        self.bullets = []
        self.wells = []
        self._keys = {}

        self.time_passed = 0

        self.camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()

        self.ui_panel = None

    def setup(self):
        self.player = Player(0, 0)
        # Spawn 10 random wells
        for _ in range(10):
            well = ResourceWell(x_max=1000, y_max=1000, capacity=100, radius=75)
            self.wells.append(well)

        self.ui_panel = UIPanel(self.player)

    def on_draw(self):
        self.clear()
        # Draw world
        self.camera.use()

        # Draw wells
        for well in self.wells:
            well.draw()

        self.player.draw()
        
        for enemy in self.enemies:
            enemy.draw()

        self.gui_camera.use()

        # Draw GUI
        self.ui_panel.draw()

        view = self.camera.viewport
        left = view.left
        right = view.right
        bottom = view.bottom
        top = view.top
        # Compute screen center from player position
        center_x = self.player.center_x
        center_y = self.player.center_y

        for enemy in self.enemies:
            if not enemy.is_dying and get_distance(enemy.center_x, center_x, enemy.center_y, center_y) >= 400:
                dx = enemy.center_x - center_x
                dy = enemy.center_y - center_y
                angle = math.atan2(dy, dx)

                # Compute world position of triangle tip
                dist = 400
                world_x = center_x + math.cos(angle) * dist
                world_y = center_y + math.sin(angle) * dist
                screen_x, screen_y = self.camera.project((world_x, world_y))

                size = 15
                tip_x = screen_x
                tip_y = screen_y
                base_angle = angle + math.pi
                left_x = tip_x + math.cos(base_angle + math.radians(30)) * size
                left_y = tip_y + math.sin(base_angle + math.radians(30)) * size
                right_x = tip_x + math.cos(base_angle - math.radians(30)) * size
                right_y = tip_y + math.sin(base_angle - math.radians(30)) * size

                arcade.draw_triangle_filled(tip_x, tip_y, left_x, left_y, right_x, right_y, arcade.color.WHITE)



    def on_update(self, delta_time):
        self.player.update(self.enemies, self.bullets, self._keys, self.wells)
        self.enemies = [e for e in self.enemies if not e.dead]

        for enemy in self.enemies:
            enemy.update(self.player.main_base)

        # self.bases[0].weapon.level_up(damage=1, range=10, bullet_speed=1, fire_rate=0.05)

        self.spawn_enemies()
        self.camera.position = (self.player.center_x, self.player.center_y)
        self.time_passed += 0.001  # Increment time passed for enemy spawning logic

    def spawn_enemies(self):
        if len(self.enemies) < 1 + int(self.time_passed):
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

            self.enemies.append(Enemy(x, y, speed=1, health=5, damage=5))

    def on_key_press(self, symbol, modifiers):
        self._keys[symbol] = True

    def on_key_release(self, symbol, modifiers):
        self._keys[symbol] = False

if __name__ == "__main__":
    window = GameWindow()
    window.setup()
    arcade.run()