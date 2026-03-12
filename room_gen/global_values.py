# Recursive minigames [values]
# Frank MR
# April 04 2025

import pygame
import random
import json
import os

pygame.init()

class GameSettings:
    def __init__(self):
        """Pygame-setup constants constants"""
        self.SCREEN_WIDTH = 900
        self.SCREEN_HEIGHT = 900
        self.SCREEN = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.FPS = pygame.time.Clock()
        self.FPS_LIMIT = 60
        self.TILESIZE = 30





        """Camera zoom values"""
        self.ZOOM_IN_MAX = 2.5
        self.ZOOM_OUT_MAX = 0.2
        self.ZOOM_CHANGE = 10
        self.zoom = 1





        """Player values"""
        self.PLAYER_SPEED = 1
        self.PLAYER_SPEED *= self.TILESIZE//2





        """Room generation values"""
        self.ROOMS_LIMIT = 5

        self.WALL = "W"
        self.DOOR = "D"
        self.ENTRANCE = "E"
        self.PLUG = "P"
        self.INV_PLUG = "F"
        
        self.NO_SOCKET = "0"
        self.NORTH_SOCKET = "1"
        self.EAST_SOCKET = "2"
        self.SOUTH_SOCKET = "3"
        self.WEST_SOCKET = "4"

        self.NORTH = "NORTH"
        self.EAST = "EAST"
        self.SOUTH = "SOUTH"
        self.WEST = "WEST"

        self.VALID_DIRECTION = {
            "NORTH": "SOUTH",
            "SOUTH": "NORTH",
            "EAST": "WEST",
            "WEST": "EAST"
        }

        self.RIGHT = "RIGHT"
        self.LEFT = "LEFT"
        self.MID = "MIDDLE"

        self.last_turn = random.choice([self.RIGHT, self.LEFT])

        # Format of dictionary
        # example
        """
        {
        "room_name" = 
            {
            "array" = ["WWW",
                       "---",
                       "WWW"],
            "orentation" = "EAST",
            "name" = "room_name"
            }
        }
        """

        # Load the rooms json and turn into dictionary
        ROOMS_JSON = os.path.join(os.path.dirname(__file__), "rooms.json")
        if os.path.exists(ROOMS_JSON):
            with open(ROOMS_JSON, "r") as f:
                self.ROOMS_DICT = json.load(f)
        else:
            raise "No rooms json found."

        # Rooms currently loaded
        self.loaded_rooms = []





        """Pygame sprite-groups"""
        self.drawables = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.entities = pygame.sprite.Group()
        self.gui = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()

game = GameSettings()