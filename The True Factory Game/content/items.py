# Factory game [items constructor]
# Author: Frank MR
# May 26th 2025

import pygame
import base
import engine
from state import game
import os


class RawIron(base.Item):
    image_paths = []
    for i in range(15):
        image_paths.append(os.path.join(game.IMAGES_DIR, "iron_ore.png"))
    
    images = engine.load_image_transformations(image_paths, dimensions=(0.5, 0.5))

    name = "Iron Ore"

    def __init__(self, rotation, position, dimensions=(0.5, 0.5)):
        super().__init__(rotation, position, dimensions)

class IronPlate(base.Item):
    image_paths = []
    for i in range(15):
        image_paths.append(os.path.join(game.IMAGES_DIR, "iron_plate.png"))
    
    images = engine.load_image_transformations(image_paths, dimensions=(0.5, 0.5))

    name = "Iron Plate"

    def __init__(self, rotation, position, dimensions=(0.5, 0.5)):
        super().__init__(rotation, position, dimensions)


        
        
        