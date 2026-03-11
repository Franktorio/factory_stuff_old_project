# Factory game [centralized settings]
# Author: Franco MR
# May 26th 2025

import os
import pygame
pygame.init()

class GameSettings:
    def __init__(self):
        """Pygame-setup constants constants"""
        self.SCREEN_WIDTH = 1200
        self.SCREEN_HEIGHT = 900
        
        self.SCREEN = pygame.display.set_mode(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT),
            pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED
        )
        
        self.FPS = pygame.time.Clock()
        self.FPS_LIMIT = 60
        self.TILESIZE = 30
        self.IMAGES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "content/images"))



        """Camera zoom values"""
        self.ZOOM_VALUES = [0.5, 0.6, 0.71, 0.8, 0.9, 1.0, 1.09, 1.2, 1.3, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
        self.zoom_index = 9
        self.zoom = self.ZOOM_VALUES[self.zoom_index]

        self.camera = None


        """Player values"""
        self.PLAYER_SPEED = 5
        self.player = None
        

        """Terrain Generation"""
        self.NOISES_APPLIED = 1
        self.TERRAIN_OCTAVES = 3
        self.CHUNKSIZE = 32 # 32 tiles
        self.AMPLITUDE = 1000


        self.seed = 3945

        self.terr_chunks = {}
        self.noise_queue = []
        self.gen_queue = []


        
        """Logic constants"""
        self.ROTATIONS = {
            "n": 0,
            "e": 270,
            "s": 180,
            "w": 90
        }
        self.OFFSETS = {
            "n": (0, 1),
            "e": (-1, 0),
            "s": (0, -1),
            "w": (1, 0)
        }
        self.RENDER_DISTANCE = 16 # In tiles

        self.keys_pressed = pygame.key.get_pressed()

        # Get all mouse positions and key inputs
        self.mouse_pressed = pygame.mouse.get_pressed()
        self.mouse_screen_pos = (0, 0) # Placeholder position
        self.mouse_world_pos = (0, 0)
        self.snapped_mouse_pos = (0, 0)
        self.tile_mouse_pos = (0, 0)
        self.chunk_mouse_pos = (0, 0)
        self.inchunk_mouse_pos = (0, 0)

        # Clamped player position
        self.player_world_pos = (0, 0)
        self.player_chunk_pos = (0, 0)

        # Spaghetti mess
        self.MAX_ANIM_FRAME = 14 # starts from 0 so theres 15
        self.global_anim_frame = 0

        self.selected_rotation = ["n", "e", "s", "w"] # When checking rotation, it checks index 0

        self.world_array = {}

        self.unlocked_recipes = []

game = GameSettings()