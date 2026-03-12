# Recursive minigames [engine]
# Frank MR
# April 04 2025

# Built-in
from tkinter import N
import pygame
import random

# Custom modules
import objects
from global_values import *



def initialize_game():
    """
    Defines and initializes things required for the game
    """
    global player, camera

    # Define player and update camera
    player = objects.Player(100)
    camera = objects.Camera(player.rect)

    first_room = objects.Room(game.ROOMS_DICT["EastStraight1"])
    first_room.generate_room()
    first_room.close_entrance()


def check_events(events):
    """
    Gets a list of every event in PyGame and updates the game accordingly.
    """
    for event in events:

        if event.type == pygame.QUIT:
            pygame.quit()

        if event.type == pygame.MOUSEWHEEL:
            # Change zoom level
            game.zoom += event.y / game.ZOOM_CHANGE
            if game.zoom >= game.ZOOM_IN_MAX:
                game.zoom = game.ZOOM_IN_MAX
            elif game.zoom <= game.ZOOM_OUT_MAX:
                game.zoom = game.ZOOM_OUT_MAX

def get_rand_room_dict():
    """
    Returns a random dictionary from the rooms dictionary

    none -> dict of {
                    "array": 2dArray, 
                    "turns": [bool,bool,bool],
                    "name": "room_name"
                    }
    """

    # Get a random room from the dictionary
    rand_room = random.choice(list(game.ROOMS_DICT.keys()))

    return game.ROOMS_DICT[rand_room]

def update_room_gen():
    """
    Generates and unloads rooms.

    (read room class for more information)
    """

    latest_room = game.loaded_rooms[-1]

    # Break the function if the player hasnt opened the doors of latest room
    if check_collision((0,0), latest_room.doors, player.rect) in [(True, False), (False, True), (True, True)]:
    
        latest_room.kill_doors()
        while True:
            new_room = get_rand_room_dict()

            # Check if the room's entrance is invalid
            if not (new_room["entrance_orientation"] == game.VALID_DIRECTION[latest_room.exit_orientation]):
                continue
            
            # Check if the last turn is equal to the new_room's turn
            if game.last_turn == new_room["turn"] and new_room["turn"] != game.MID:
                continue

            break
        
        # Update last turn if the last room wasn't straight
        if new_room["turn"] != game.MID:
            game.last_turn = new_room["turn"]
        new_room = objects.Room(new_room)
        new_room.generate_room(latest_room.socket)

        if len(game.loaded_rooms) > game.ROOMS_LIMIT:
            game.loaded_rooms[0].unload()
            game.loaded_rooms[0].close_entrance()

def check_collision(vector2, spritegroup, rect):
    """
    Checks if collision between a rect and a sprite group is true or not.
    It returns two different values checking collision on X and Y axis separately.

    tuple of (int, int), object_w_rect, rect -> tuple of (Bool, Bool)
    """
    # Define collisions
    x_coll = False
    y_coll = False

    movement_x, movement_y = vector2
    rect_copy = rect.copy()

    # Iterate through every rect in the group
    for sprite in spritegroup:
        sprite_rect = sprite.rect

        # Check X axis collisions
        rect_copy.x += movement_x
        if rect_copy.colliderect(sprite_rect):
            x_coll = True
        rect_copy.center = rect.center # Return the copied-rect to the original position

        # Check Y axis collisions
        rect_copy.y += movement_y
        if rect_copy.colliderect(sprite_rect):
            y_coll = True
        rect_copy.center = rect.center

    # Check if the position is also valid diagonally
    if not x_coll and not y_coll:
        for sprite in spritegroup:
            sprite_rect = sprite.rect

            rect_copy.y += movement_y
            rect_copy.x += movement_x

            if rect_copy.colliderect(sprite_rect):
                return random.choice([(True, False), (False, True)])
            rect_copy.center = rect.center

    return (x_coll, y_coll)

def update_player(key_inputs, mouse_pos):
    """
    Updates everything the player might be doing.
    """
    # Get the position the player will be if it wants to move
    movement_x, movement_y = player.check_movement(key_inputs, mouse_pos)

    # No need to check if player can move if its not trying to move
    if (0, 0) != (movement_x, movement_y):
        coll_x, coll_y = check_collision((movement_x, movement_y), game.obstacles, player.rect)

        # coll_x, coll_y = (False, False) # Un-comment to debug without colliding with stuff

        # Not colliding on X axis
        if not coll_x:
            player.rect.x += movement_x
        
        # Not colliding on Y axis
        if not coll_y:
            player.rect.y += movement_y

