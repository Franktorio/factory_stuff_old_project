# Factory game [conveyor constructor]
# Author: Frank MR
# May 26th 2025

import base
import engine
import os
from state import game


class Drill(base.Building):
    image_paths = []
    for i in range(15):
        image_paths.append(os.path.join(game.IMAGES_DIR, "drill_1.png"))

    images = engine.load_image_transformations(image_paths, dimensions=(3, 3))

    name = "Drill"

    def __init__(self, position, ghost, rotation):
        super().__init__(position=position, rotation=rotation, ghost=ghost, dimensions=(3, 3), has_output=True, out_capacity=10)
        self.cooldown = 0

        self.mining = None
        self.mining_rate = 200
        self.mining_progress = 0

    def place(self, snapped_mouse_pos):
        if super().place(snapped_mouse_pos):
            self._check_if_ore()
            return True
    
    def _check_if_ore(self):
        """Returns either None or an item if drill is on-top of ore patch"""
        

        for tile in self.standing_on:
            if tile.ore != None:
                self.mining = tile.ore
                self.mining_rate -= 20

    def update(self):
        if self.mining != None:
            if self.mining_progress > 1:
                self.mining_progress -= 1
            else:
                self.mining_progress = self.mining_rate
                self.add_output(self.mining)


        self.update_building()
    