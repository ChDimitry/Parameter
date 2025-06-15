import arcade
import random
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from constants import GROUND_COLOR
from player import Player
from enemy import Enemy
from anchor_node import AnchorNode
from base import Base
from resource_well import ResourceWell
from obstacle import Obstacle
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

        self.resource_wells = {
            "range": {
                "capacity": 5,
                "radius": 5,
                "attributes": [0, 50, 0, 0]
            }
            , "damage": {
                "capacity": 5,
                "radius": 5,
                "attributes": [0.5, 0, 0, 0]
            }
            , "bullet_speed": {
                "capacity": 5,
                "radius": 5,
                "attributes": [0, 0, 0.25, 0]
            }
            , "fire_rate": {
                "capacity": 5,
                "radius": 5,
                "attributes": [0, 0, 0, 0.1]
            }
        }

        self._keys = {}
        self.flora_list = arcade.SpriteList()
        self.obstacles = arcade.SpriteList()

        self.time_passed = 0

        self.camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()

        self.ui_panel = None

    def generate_resource_wells_in_rings(self, ring_configs):
        """
        Generate resource wells in concentric rings with optional spacing and upgrade control.

        Each config dictionary can contain:
            - radius (float): Distance from center for the ring
            - count (int): Number of wells in this ring
            - capacity (int, optional): Scrap each well starts with
            - well_radius (float, optional): Visual radius of well
            - upgrade_pool (list[str], optional): Allowed upgrade types
            - min_spacing (float, optional): Minimum distance between wells (applies along arc)
            - fixed_angles (list[float], optional): If provided, used directly
        """
        for config in ring_configs:
            radius = config['radius']
            count = config['count']
            capacity = config.get('capacity', 5)
            well_radius = config.get('well_radius', 75)
            upgrade_pool = config.get('upgrade_pool', ["range", "damage", "bullet_speed", "fire_rate"])
            min_spacing = config.get('min_spacing', 0)  # in pixels along arc
            fixed_angles = config.get('fixed_angles')

            placed_angles = []

            def is_far_enough(candidate_angle):
                cx = math.cos(candidate_angle) * radius
                cy = math.sin(candidate_angle) * radius
                for existing_angle in placed_angles:
                    ex = math.cos(existing_angle) * radius
                    ey = math.sin(existing_angle) * radius
                    dist = math.hypot(ex - cx, ey - cy)
                    if dist < min_spacing:
                        return False
                return True

            angles = []
            if fixed_angles and len(fixed_angles) == count:
                angles = fixed_angles
            else:
                attempts = 0
                while len(angles) < count and attempts < 500:
                    angle = random.uniform(0, 2 * math.pi)
                    if min_spacing == 0 or is_far_enough(angle):
                        angles.append(angle)
                        placed_angles.append(angle)
                    attempts += 1

            for angle in angles:
                x = math.cos(angle) * radius
                y = math.sin(angle) * radius

                upgrade_type = random.choice(upgrade_pool)
                attributes = {
                    "range":        [0, 50, 0, 0],
                    "damage":       [0.5, 0, 0, 0],
                    "bullet_speed": [0, 0, 0.25, 0],
                    "fire_rate":    [0, 0, 0, 0.1]
                }[upgrade_type]

                well = ResourceWell(
                    x=x,
                    y=y,
                    capacity=capacity,
                    radius=well_radius,
                    upgrade_attributes=attributes,
                    upgrade_type=upgrade_type
                )
                self.wells.append(well)



    def setup(self):
        self.ui_panel = UIPanel()

        ring_configs = [
            {
                "radius": 200,
                "count": 3,
                "capacity": 5,
                "well_radius": 60,
                "upgrade_pool": ["range"],
                "min_spacing": 100
            },
            {
                "radius": 500,
                "count": 5,
                "capacity": 8,
                "well_radius": 65,
                "upgrade_pool": ["damage", "range"],
                "min_spacing": 180
            },
            {
                "radius": 1000,
                "count": 7,
                "capacity": 10,
                "well_radius": 70,
                "upgrade_pool": ["bullet_speed"],
                "min_spacing": 200
            },
            {
                "radius": 2000,
                "count": 10,
                "capacity": 12,
                "well_radius": 75,
                "upgrade_pool": ["fire_rate", "damage"],
                "min_spacing": 250
            },
            {
                "radius": 5000,
                "count": 15,
                "capacity": 15,
                "well_radius": 80,
                "upgrade_pool": ["range", "bullet_speed", "fire_rate"],
                "min_spacing": 300
            },
        ]

        self.generate_resource_wells_in_rings(ring_configs)

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

        self.obstacles.draw()

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