# Factory game [terrain handler]
# Author: Frank MR
# May 26th 2025

import threading
import random
import engine
import rendering
import perlin_noise
import time
import os
from . import ores
from state import game

class Tile(rendering.OnWorldObject):

    hill = engine.load_image_transformations([os.path.join(game.IMAGES_DIR, "hill.png") for _ in range(15)], dimensions=(2, 2))
    grass = engine.load_image_transformations([os.path.join(game.IMAGES_DIR, "grass.png") for _ in range(15)], dimensions=(2, 2))
    sand = engine.load_image_transformations([os.path.join(game.IMAGES_DIR, "sand.png") for _ in range(15)], dimensions=(2, 2))
    water = engine.load_image_transformations([os.path.join(game.IMAGES_DIR, "water.png") for _ in range(15)], dimensions=(2, 2))


    def __init__(self, height, position):
        super().__init__(position=position, rotation=random.choice(list(game.ROTATIONS.keys())))
        self.rect.topleft = position
        self.tile = None
        self.images = self._get_color(height)
        self.ore = None

    def _get_color(self, height):
        if height < -0.5:
            self.tile = "water"
            return self.water
        elif height < -0.2:
            self.tile = "sand"
            return self.sand
        elif height < 0.5:
            self.tile = "grass"
            return self.grass
        else:
            self.tile = "hill"
            return self.hill
    
    def become_ore(self, ore):
        if self.tile == "water":
            return
        
        self.tile = ore.name
        self.images = ore.images
        self.ore = ore.item

class Chunk:

    def __init__(self, x, y, seed=game.seed):
        self.x = x
        self.y = y
        self.seed = seed
        self.noises = generate_noise(game.NOISES_APPLIED, seed, game.TERRAIN_OCTAVES)

        self.tiles = {}
        self.real_tiles = []
        self.loaded = False
        self.local_tilesize = game.TILESIZE*2
    
    def gen_terrain(self):
        chunksize = game.CHUNKSIZE * game.TILESIZE
        self.zero_zero = (self.x * chunksize, self.y * chunksize)

        # Load the terrain
        for x in range(0, game.CHUNKSIZE, 2):
            for y in range(0, game.CHUNKSIZE, 2):
                position = (self.zero_zero[0] + x * game.TILESIZE, self.zero_zero[1] + y * game.TILESIZE)
                height = self.noises[0]([(position[0]/game.TILESIZE)/game.AMPLITUDE, (position[1]/game.TILESIZE)/game.AMPLITUDE]) * 2
                tile = Tile(height, position)
                self.tiles[(x, y)] = tile
                self.tiles[(x+1, y+1)] = tile
                self.tiles[(x+1, y)] = tile
                self.tiles[(x, y+1)] = tile

                self.real_tiles.append(tile)

        # Generate an ore patch originating from the middle if chunk is 1 in 100
        if random.randint(1, 10) == 1:
            origin_tile = (game.CHUNKSIZE//2, game.CHUNKSIZE//2)
            self.ores = [origin_tile]
            for _ in range(20):
                neighbours = self.get_neighbouring_tiles()
                self.ores.append(random.choice(neighbours))
            
            for tile in self.ores:
                if self.tiles[tile] in self.real_tiles:
                    self.tiles[tile].become_ore(ores.Iron)






        self.loaded = True 

    def get_neighbouring_tiles(self):
        neighbour_tiles = []
        for o in self.ores:
            for x in range(-1, 2):
                for y in range(-1, 2):
                    if (o[0]+x, o[1]+y) not in self.ores and (o[0]+x, o[1]+y) in self.tiles:
                        neighbour_tiles.append((o[0]+x, o[1]+y))
                                    
        return neighbour_tiles


    def render_chunk(self):
        for tile in self.real_tiles:
            tile.render()
        


terrain_lock = threading.Lock()

def handle_gen_terrain_queue():
    """Goes through the gen terrain queue and generates the terrain of the first chunk it gets"""
    while True:
        with terrain_lock:
            if len(game.gen_queue) > 0:
                chunk = game.gen_queue.pop(0)

                if chunk in game.terr_chunks:
                    game.terr_chunks[chunk].gen_terrain()
                elif chunk not in game.noise_queue:
                        game.noise_queue.append(chunk)

        time.sleep(0.01)
            
                
def handle_noise_queue():
    """Goes through the noise queue and generates the first chunk it gets"""
    while True:
        with terrain_lock:
            if len(game.noise_queue) > 0:

                chunk = game.noise_queue.pop(0)

                if chunk in game.terr_chunks:
                    continue

                game.terr_chunks[chunk] = Chunk(chunk[0], chunk[1])
        
        time.sleep(0.01)

def start():
    """Starts processing the terrain queues"""

    # Make 3 worker threads that go through generating noise
    for t in range(3):
        threading.Thread(target=handle_noise_queue).start()

    # Make 3 worker threads that go through generating terrain
    for t in range(3):
        threading.Thread(target=handle_gen_terrain_queue).start()

def generate_noise(amount, seed, octaves):
    """Returns a dictionary of different noise levels"""
    noises = {}
    octave_mixer = octaves
    for i in range(amount):
        noises[i] = perlin_noise.PerlinNoise(octaves=octaves * octave_mixer, seed=seed)
        octave_mixer = octave_mixer * 2
    return noises