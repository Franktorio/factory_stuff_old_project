# Factory game [conveyor constructor]
# Author: Frank MR
# May 26th 2025

import base
import engine
import os
from state import game


class Conveyor(base.Entity):
    straight_paths = [os.path.join(game.IMAGES_DIR, f"conv_{i+1}.png") for i in range(15)]
    turned_paths = [os.path.join(game.IMAGES_DIR, f"conv_r{i+1}.png") for i in range(15)]

    # Straight conveyors
    straight_imgs = engine.load_image_transformations(straight_paths, dimensions=(1, 1))

    right_turn = engine.load_image_transformations(turned_paths, dimensions=(1, 1), rotation=90)
    left_turn = engine.load_image_transformations(turned_paths, dimensions=(1, 1), rotation=270, flipped=True)
    
    name = "Conveyor"

    def __init__(self, position, ghost, rotation=game.selected_rotation[0]):
        super().__init__(position=position, rotation=rotation, ghost=ghost, dimensions=(1, 1), is_conveyor=True)
        self.images = self.straight_imgs
        self._get_rotation()

    
    def _get_rotation(self):
        neighbours = self.check_neighbours()
        self.images = self.straight_imgs

        if len(neighbours) == 1:
            neighbour = neighbours[0]

            # Check if neighbour is on my right (of where conveyor facing)
            if self.rotation == "n" and neighbour.world_pos[0] > self.world_pos[0]:
                self.images = self.right_turn
            elif self.rotation == "e" and neighbour.world_pos[1] > self.world_pos[1]:
                self.images = self.right_turn
            elif self.rotation == "s" and neighbour.world_pos[0] < self.world_pos[0]:
                self.images = self.right_turn
            elif self.rotation == "w" and neighbour.world_pos[1] < self.world_pos[1]:
                self.images = self.right_turn
            
            # Check if neighbour is on my left (of where conveyor facing)
            if self.rotation == "n" and neighbour.world_pos[0] < self.world_pos[0]:
                self.images = self.left_turn
            elif self.rotation == "e" and neighbour.world_pos[1] < self.world_pos[1]:
                self.images = self.left_turn
            elif self.rotation == "s" and neighbour.world_pos[0] > self.world_pos[0]:
                self.images = self.left_turn
            elif self.rotation == "w" and neighbour.world_pos[1] > self.world_pos[1]:
                self.images = self.left_turn
    
    def check_neighbours(self):
        """Looks for neighbouring conveyors"""

        positions = [(self.world_pos[0], self.world_pos[1] - 1), (self.world_pos[0] + 1, self.world_pos[1]), (self.world_pos[0], self.world_pos[1] + 1), (self.world_pos[0] - 1, self.world_pos[1])]
        neighbour_conveyors = []
        for pos in positions:
            if pos in game.world_array and pos != self.output_tile:
                try:
                    if game.world_array[pos].output_tile == self.world_pos:
                        neighbour_conveyors.append(game.world_array[pos])
                except AttributeError:
                    pass
        return neighbour_conveyors

    def update(self):
        self.update_conveyor()
        self._get_rotation()










    
    
