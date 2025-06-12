from node import Node

class AnchorNode(Node):
    def __init__(self, _id,  x, y, closest_node=None, main_base=None, player=None):
        super().__init__(_id, x, y, closest_node, main_base, player)
