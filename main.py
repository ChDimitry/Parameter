import arcade
import random
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from constants import GROUND_COLOR
from player import Player
from enemy import Enemy
from anchor_node import AnchorNode
from base import Base
from resource_well import ResourceWell
# from obstacle import Obstacle
import arcade.camera
from common import get_distance, is_entity_inside
import math
from uiPanel import UIPanel

class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Outer Parameter")
        arcade.set_background_color(GROUND_COLOR)

        self.enemies = []
        self.wells: list = []
        self.main_base = Base(0, 0, player=None)

        self.anchor_node_north = AnchorNode(1, 0, 100, closest_node=self.main_base, main_base=self.main_base)
        self.anchor_node_west = AnchorNode(2, -100, 0, closest_node=self.main_base, main_base=self.main_base)
        self.anchor_node_east = AnchorNode(3, 100, 0, closest_node=self.main_base, main_base=self.main_base)
        self.anchor_node_south = AnchorNode(4, 0, -100, closest_node=self.main_base, main_base=self.main_base)

        self.player = Player(0, 0, main_base=self.main_base)
        self.main_base.player = self.player
        self.anchor_node_north.player = self.player
        self.nodes: list = [self.main_base, self.anchor_node_north, self.anchor_node_west, self.anchor_node_east, self.anchor_node_south]


        self._keys = {}
        self.flora_list = arcade.SpriteList()
        self.obstacles = arcade.SpriteList()

        self.time_passed = 0

        self.camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()

        self.ui_panel = None

    def setup(self):
        

        well = ResourceWell(x=200, y=200, capacity=5, radius=75)
        self.wells.append(well)
        # well = ResourceWell(x=-200, y=200, capacity=5, radius=75)
        # self.wells.append(well)
        # well = ResourceWell(x=-200, y=-200, capacity=5, radius=75)
        # self.wells.append(well)

        # well = ResourceWell(x=400, y=400, capacity=10, radius=75)
        # self.wells.append(well)
        # well = ResourceWell(x=-400, y=400, capacity=10, radius=75)
        # self.wells.append(well)

        well = ResourceWell(x=400, y=-400, capacity=25, radius=75)
        self.wells.append(well)
        well = ResourceWell(x=-600, y=-600, capacity=100, radius=75)
        self.wells.append(well)
        
        # obstacle = Obstacle(x=200, y=-200, radius=200)
        # self.obstacles.append(obstacle)
        # obstacle = Obstacle(x=-400, y=-400, radius=200)
        # self.obstacles.append(obstacle)

        self.ui_panel = UIPanel()

        for _ in range(500):
            sprite = arcade.SpriteCircle(radius=100, color=(30, 40, 30, 10), soft=True)
            sprite.center_x = random.randint(-2000, 2000)
            sprite.center_y = random.randint(-2000, 2000)
            self.flora_list.append(sprite)

    def on_draw(self):
        self.clear()
        # Draw world
        self.camera.use()
        # Draw wells
        for well in self.wells:
            well.draw(self.time_passed * 100)

        self.player.draw()
        
        for enemy in self.enemies:
            enemy.draw()

        for node in self.nodes:
            node.draw()

        # self.obstacles.draw()

        self.flora_list.draw()

        self.gui_camera.use()

        # Draw GUI
        self.ui_panel.draw(self.player, self.nodes)
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
        self.player.update(self.enemies, self._keys, self.obstacles, self.nodes)
        self.enemies = [e for e in self.enemies if not e.dead]
        self.wells = [w for w in self.wells if w.active]

        for enemy in self.enemies:
            enemy.update(self.player.main_base, self.player)
            # Check if enemy touched the main base, if so, end the game
            if is_entity_inside(enemy, self.main_base, radius=1):
                arcade.close_window()
                print("Game Over! The enemy reached the main base.")
                return

        for node in self.nodes:
            node.update(self.enemies, self.wells)
            # if node.is_collecting:
            #     self.active_collecting_nodes.add(node)
            # else:
            #     self.active_collecting_nodes.discard(node)

        self.spawn_enemies()
        self.camera.position = (self.player.center_x, self.player.center_y)
        self.time_passed += 0.0005  # Increment time passed for enemy spawning logic

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