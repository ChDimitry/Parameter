import arcade
from config import SCREEN_HEIGHT, BASE_COST

class UIPanel:
    def __init__(self):
        # Panel properties
        self.width = 200
        self.height = 200
        self.center_x = 130  # Center x of the UI box
        self.center_y = SCREEN_HEIGHT - 130  # Center y

        # Text properties
        self.x_shift = 90
        self.y_shift = 80
        self.y_gap = 0

        # Font
        self.font_name = "Kenney Pixel"
        self.font_size = 12
        self.text_color = arcade.color.WHITE
        self.background_color = arcade.color.BLACK_OLIVE
        self.border_color = arcade.color.ASH_GREY

    def draw(self, player, nodes):
        # Draw panel background using Rect
        rect = arcade.Rect(
            left=self.center_x - self.width // 2,
            right=self.center_x + self.width // 2,
            bottom=self.center_y - self.height // 2,
            top=self.center_y + self.height // 2,
            width=self.width,
            height=self.height,
            x=self.center_x,
            y=self.center_y
        )
        arcade.draw_rect_filled(
            rect,
            self.background_color,
            tilt_angle=0
        )

        # Gather player info
        node_count = len(nodes)
        collecting_count = len(player._active_collecting_nodes)
        scrap = player.scrap
        collected_resources = player.main_base.collected_resources 
        distance = int(player.distance_from_node)

        # Draw text
        arcade.draw_text(f"# Nodes: {node_count}", self.center_x - self.x_shift, self.center_y + self.y_shift, self.text_color, self.font_size, font_name=self.font_name)
        arcade.draw_text(f"# Collecting: {collecting_count}", self.center_x - 90, self.center_y + self.y_shift - 20, self.text_color, self.font_size, font_name=self.font_name)
        arcade.draw_text(f"Scrap: {scrap}", self.center_x - self.x_shift, self.center_y + self.y_shift - 40, self.text_color, self.font_size, font_name=self.font_name)
        arcade.draw_text(f"Distance: {distance} KM", self.center_x - self.x_shift, self.center_y + self.y_shift - 60, self.text_color, self.font_size, font_name=self.font_name)
        arcade.draw_text(f"# Resources: {collected_resources}", self.center_x - self.x_shift, self.center_y + self.y_shift - 80, self.text_color, self.font_size, font_name=self.font_name)
        arcade.draw_text(f"Base Cost: {BASE_COST} Scrap", self.center_x - self.x_shift, self.center_y + self.y_shift - 100, self.text_color, self.font_size, font_name=self.font_name)