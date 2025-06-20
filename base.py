import arcade
from weapon import Weapon
from constants import REQUIRED_SCRAP, BASE_COLOR, BASE_RANGE_COLOR

from common import get_text_object

class Base:
    def __init__(self, x, y, main_base=None, player=None):
        self.player = player
        self.main_base = main_base
        self.center_x = x
        self.center_y = y
        self.color = BASE_COLOR
        self.weapon = Weapon(owner=self, damage=1, range=100, bullet_speed=5, fire_rate=0.5)

        self.scrap = 0
        self.level = 0

        # Rectangle properties
        self.width = 20
        self.height = 20
        self.rotation = 0
        self.rotation_speed = 10

        self.is_collecting = False
        self.collected_resources = 0
        self.collection_rate = 5
        self.assigned_well = None

        self.link_length = 0

        self.upgrades: list[str] = []


        # Labels for weapon stats
        self.weapon_damage_label = get_text_object(f"Damage: {self.weapon.damage}", self.center_x, self.center_y - 20)
        self.weapon_range_label = get_text_object(f"Range: {self.weapon.range}", self.center_x, self.center_y - 35)
        self.weapon_fire_rate_label = get_text_object(f"Fire Rate: {self.weapon.fire_rate}", self.center_x, self.center_y - 50)
        self.weapon_bullet_speed_label = get_text_object(f"Bullet Speed: {self.weapon.bullet_speed}", self.center_x, self.center_y - 65)


    def update(self, enemies, wells):
        self.update_rotation()
        self.weapon.update(enemies)
        self.weapon.try_fire(enemies)

        if self.collected_resources >= REQUIRED_SCRAP:
            self.level += 1
            self.collected_resources = 0
            # self.weapon.level_up(damage=0.50, range=50, bullet_speed=0.25, fire_rate=0.05)
    
    def update_rotation(self):
        # Align base rotation toward weapon angle
        target_angle = self.weapon.angle

        angle_diff = (target_angle - self.rotation + 180) % 360 - 180
        if abs(angle_diff) < self.rotation_speed:
            self.rotation = target_angle
        else:
            self.rotation += self.rotation_speed * (1 if angle_diff > 0 else -1)
        self.rotation %= 360

    def draw(self):
        # # Fade-in from outer ring inward using outlines
        # num_rings = 20
        # max_radius = self.weapon.range
        # base_color = BASE_RANGE_COLOR[:3]
        # max_alpha = BASE_RANGE_COLOR[3] if len(BASE_RANGE_COLOR) > 3 else 50
        # outline_thickness = 5  # You can tweak this

        # for i in range(num_rings):
        #     fade_factor = 1 - (i / num_rings)
        #     radius = max_radius * fade_factor
        #     alpha = int(max_alpha * fade_factor**2)  # Outer = most visible

        #     color = (*base_color, alpha)

        #     arcade.draw_circle_outline(
        #         self.center_x,
        #         self.center_y,
        #         radius,
        #         color,
        #         border_width=outline_thickness
        #     )


        # Create rect with proper values
        rect = arcade.Rect(
            left=0, right=0,
            bottom=0, top=0,
            width=self.width,
            height=self.height,
            x=self.center_x,
            y=self.center_y
        )
        arcade.draw_rect_filled(
            rect,
            self.color,
            tilt_angle=self.rotation
        )
        
        # Draw level text
        arcade.draw_text(
            f"{self.level}",
            self.center_x, self.center_y,
            arcade.color.BLACK,
            font_size=11,
            anchor_x="center",
            anchor_y="center"
        )

        spacing = 15  # Space between symbols
        total_width = (len(self.upgrades) - 1) * spacing
        for i, upgrade in enumerate(self.upgrades):
            x_offset = -total_width / 2 + i * spacing
            arcade.draw_text(
                upgrade,
                self.center_x + x_offset,
                self.center_y + 25,
                arcade.color.WHITE,
                font_size=14,
                anchor_x="center",
                anchor_y="center"
            )

        # Draw the weapon's damage, range, bullet speed, and fire rate
        # Icon - stat

        self.weapon_damage_label.text = f"Damage: {self.weapon.damage:.2f}"
        self.weapon_damage_label.draw()
        self.weapon_range_label.text = f"Range: {self.weapon.range}"
        self.weapon_range_label.draw()
        self.weapon_fire_rate_label.text = f"Fire Rate: {self.weapon.fire_rate:.2f}"
        self.weapon_fire_rate_label.draw()
        self.weapon_bullet_speed_label.text = f"Bullet Speed: {self.weapon.bullet_speed:.2f}"
        self.weapon_bullet_speed_label.draw()

        # Draw the number of collecting nodes on the right side of the base
        # self.number_of_collecting_nodes.text = f"Collecting Nodes: {len(self.player.active_collecting_nodes)}"
        # self.number_of_collecting_nodes.draw()
        

        self.weapon.draw()
