# Factory game [furnace constructor]
# Author: Frank MR
# May 26th 2025

import base
import engine
import os
import recipes
from state import game


class Furnace(base.Building):
    paths_off = []
    for i in range(15):
        paths_off.append(os.path.join(game.IMAGES_DIR, "furnace_off.png"))

    paths_on = []
    for i in range(15):
        paths_on.append(os.path.join(game.IMAGES_DIR, "furnace_on.png"))

    images_off = engine.load_image_transformations(paths_off, dimensions=(3, 3))
    images_on = engine.load_image_transformations(paths_on, dimensions=(3, 3))

    name = "Furnace"

    def __init__(self, position, ghost, rotation):
        super().__init__(position=position, rotation=rotation, ghost=ghost, dimensions=(3, 3), has_input=True, has_output=True, out_capacity=10, in_capacity=10)
        self.cooldown = 0
        self.images = self.images_off

    
    def update(self):
        self.images = self.images_off

        if len(self.input_inv) > 0 and self.cooldown == 0 and len(self.output_inv) < self.out_capacity:
            for item in self.input_inv:
                if item in recipes.furnace_recipes:
                    for i in range(recipes.furnace_recipes[item]["output"][1]):
                        self.add_output(recipes.furnace_recipes[item]["output"][0])
                    self.input_inv[item] -= 1
                    self.cooldown = recipes.furnace_recipes[item]["time"]
                    break
                else:
                    # Burn the item if it is not in the recipes
                    self.input_inv[item] -= 1
                    self.cooldown = 30
                    break
        
        if self.cooldown > 0:
            self.cooldown -= 1
            self.images = self.images_on



        self.update_building()
    