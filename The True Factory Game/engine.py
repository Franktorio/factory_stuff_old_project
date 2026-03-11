# Factory game [logic handler]
# Author: Frank MR
# May 26th 2025

import pygame
import math

# Custom imports
from state import game
import rendering

# Dragging variables
dragging_conveyor = False
conv_drag_start = (0, 0)
delete_drag_start = (0, 0)

left_clicking = False
clicking_gui = False
mouse_down_pos = (0, 0)

def load_image_transformations(image_paths_or_surface, dimensions=(1, 1), rotation=0, flipped=False):
    """
    Loads all the possible transformations an image can have
    Returns a dictionary with all the transformations
    """
    transformed_images = {}
    temp_counter = 0
    for direction in game.ROTATIONS:
        transformed_images[direction] = {}
        for i in range(15): # 15 because every image only has 15 frames
            transformed_images[direction][i] = {}
            for zoom in game.ZOOM_VALUES:
                temp_counter += 1
                if not isinstance(image_paths_or_surface[i], pygame.surface.Surface):
                    image = pygame.image.load(image_paths_or_surface[i]).convert_alpha()
                    image = pygame.transform.scale(image, (game.TILESIZE*dimensions[0], game.TILESIZE*dimensions[1])) # Make the image TILESIZE
                    if flipped:
                        image = pygame.transform.flip(image, True, False)
                    image = pygame.transform.rotate(image, rotation)
                else:
                    image = image_paths_or_surface[i]
                image = pygame.transform.rotate(image, game.ROTATIONS[direction])
                image = pygame.transform.scale(image, 
                                                (math.ceil(image.get_width() * zoom),
                                                 math.ceil(image.get_height() * zoom))
                                              )
                transformed_images[direction][i][zoom] = image
    return transformed_images

def handle_zoom(event):
    """Changes zoom level"""
    if event.y > 0:
        if game.zoom_index < len(game.ZOOM_VALUES) - 1:
            game.zoom_index += 1
        else:
            game.zoom_index = len(game.ZOOM_VALUES) - 1
    else:
        if game.zoom_index > 0:
            game.zoom_index -= 1
        else:
            game.zoom_index = 0
    game.zoom = game.ZOOM_VALUES[game.zoom_index]

def keydown_events(event):
    """Handles keydown events"""
    if event.key == pygame.K_r:
        rotate()

def mouse_down():
    pressed = pygame.mouse.get_pressed()

    if pressed[0]:
        left_click_down()

def mouse_up():
    """Handles mouse up events"""
    global left_clicking
    pressed = pygame.mouse.get_pressed()

    if left_clicking and not pressed[0]:
        left_click_up()

def left_click_down():
    """
    Handles left click events.
    """
    global mouse_down_pos, left_clicking, clicking_gui

    # Log the mouse position for dragging logic
    mouse_down_pos = game.tile_mouse_pos
    left_clicking = True
    clicked_gui = False

    for gui in rendering.GraphicalUserInterface.all_guis:
        gui = rendering.GraphicalUserInterface.all_guis[gui]

        if gui.rect.collidepoint(game.mouse_screen_pos) and isinstance(gui, rendering.GuiButton):
            gui.interact()
            clicked_gui = True
        elif gui.rect.collidepoint(game.mouse_screen_pos):
            clicked_gui = True
        
    if clicked_gui:
        clicking_gui = True
        return
    
    if game.tile_mouse_pos in game.world_array:
        game.world_array[game.tile_mouse_pos].interact()
        return

def left_click_up():
    """
    Handles left click release events.
    """
    global dragging_conveyor, delete_drag_start, left_clicking, clicking_gui

    left_clicking = False

    if clicking_gui:
        clicking_gui = False
        return

    if dragging_conveyor:
        drag_conveyor(place=True)
        return

    if delete_drag_start != (0, 0):
        delete_drag_start = (0, 0)
        return
    
    
    place_at(game.tile_mouse_pos, game.selected_rotation[0], game.player.selected[0])

def update_mouse():
    """
    Decides if the player is dragging or not.
    """
    global left_clicking, mouse_down_pos, dragging_conveyor, clicking_gui
    
    if clicking_gui:
        return

    if game.player.selected[0] == None:
        return

    if left_clicking and game.tile_mouse_pos != mouse_down_pos:
        if game.player.selected[0].name == "Conveyor":
            drag_conveyor()

def handle_events():
    """
    Gets a list of every event in PyGame and updates the game accordingly.
    """
    events = pygame.event.get()

    for event in events:

        if event.type == pygame.QUIT:
            pygame.quit()

        if event.type == pygame.MOUSEWHEEL:
            handle_zoom(event)

        if event.type == pygame.KEYDOWN:
            keydown_events(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_down()
        
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_up()

def drag_conveyor(place=False):
    """
    Handles the dragging of a conveyor belt.
    """
    global dragging_conveyor, conv_drag_start, mouse_down_pos

    if not dragging_conveyor:
        dragging_conveyor = True
        conv_drag_start = mouse_down_pos

    path = pathfind(conv_drag_start, game.tile_mouse_pos)

    needed_counter = 0

    if not path:
        return

    for tile_pos, direction in path:
        if tile_pos in game.world_array:
            continue

        needed_counter += 1

        position = (tile_pos[0] * game.TILESIZE, tile_pos[1] * game.TILESIZE)

        if place:
            place_at(tile_pos, direction, game.player.selected[0])
            dragging_conveyor = False
        else:
            
            if not needed_counter >= game.player.selected[1]:
                ghost = game.player.selected[0](position=position, rotation=direction, ghost=True)
                ghost.render(alpha=100)

def place_at(tile_pos, rotation, item):
    """
    Attempts to place the given item at a tile, removes 1 from the player's inventory if it can be placed
    """
    pos = (tile_pos[0] * game.TILESIZE, tile_pos[1] * game.TILESIZE)

    if item == None:
        return
    
    building = item(rotation=rotation, position=pos, ghost=False)
    
    if game.player.can_use(item, 1) and building.place(pos):
        game.player.remove_from_inventory(item, 1)
    else:
        building.destroy()

def right_click():
    """
    Handles right click events.
    """
    if game.tile_mouse_pos in game.world_array:
        game.player.add_to_inventory(type(game.world_array[game.tile_mouse_pos]), 1)
        game.world_array[game.tile_mouse_pos].destroy()

def rotate():
    """
    Rotates the selected item.
    """

    current_rotation = game.selected_rotation.pop(0)
    game.selected_rotation.append(current_rotation)



def update_ghost():
    """
    Makes and renders a ghost of the selected item.
    """
    global dragging_conveyor

    if dragging_conveyor:
        return

    if game.player.selected[0] != None:
        try:
            ghost = game.player.selected[0](position=game.snapped_mouse_pos, rotation=game.selected_rotation[0], ghost=True)
            ghost.render(alpha=100)
        except Exception as e:
            print(f"Error rendering ghost: {e}")


def update_inputs():
    """
    Updates the game inputs.
    """
    global rotated, left_clicked, right_clicked, dragging_conveyor

    game.player.update()
    update_mouse()

    if game.mouse_pressed[2]:
        right_click()
    else:
        right_clicked = False



def queue_chunks():
    """
    Queues chunks to be handled by the worker threads in the terrain.py module
    """

    c_x, c_y = game.player_chunk_pos

    inner_ring = [
        (c_x-1, c_y-1), (c_x, c_y-1), (c_x+1, c_y-1),
        (c_x-1, c_y), (c_x, c_y), (c_x+1, c_y),
        (c_x-1, c_y+1), (c_x, c_y+1), (c_x+1, c_y+1)
    ]
    
    middle_ring = [
        (c_x-2, c_y-2), (c_x-1, c_y-2), (c_x, c_y-2), (c_x+1, c_y-2), (c_x+2, c_y-2),
        (c_x-2, c_y-1), (c_x+2, c_y-1),
        (c_x-2, c_y),   (c_x+2, c_y),
        (c_x-2, c_y+1), (c_x+2, c_y+1),
        (c_x-2, c_y+2), (c_x-1, c_y+2), (c_x, c_y+2), (c_x+1, c_y+2), (c_x+2, c_y+2)
    ]

    outter_ring = [
        (c_x-3, c_y-3), (c_x-2, c_y-3), (c_x-1, c_y-3), (c_x, c_y-3), (c_x+1, c_y-3), (c_x+2, c_y-3), (c_x+3, c_y-3),
        (c_x-3, c_y-2), (c_x+3, c_y-2),
        (c_x-3, c_y-1), (c_x+3, c_y-1),
        (c_x-3, c_y),   (c_x+3, c_y),
        (c_x-3, c_y+1), (c_x+3, c_y+1),
        (c_x-3, c_y+2), (c_x+3, c_y+2),
        (c_x-3, c_y+3), (c_x-2, c_y+3), (c_x-1, c_y+3), (c_x, c_y+3), (c_x+1, c_y+3), (c_x+2, c_y+3), (c_x+3, c_y+3)
    ]

    # Queue noise
    for chunk in outter_ring + middle_ring:

        if chunk not in game.terr_chunks and chunk not in game.noise_queue:
            game.noise_queue.append(chunk)

    # Queue terrain
    for chunk in inner_ring:
        if chunk in game.terr_chunks:

            if not game.terr_chunks[chunk].loaded and chunk not in game.gen_queue:
                game.gen_queue.append(chunk)

        elif chunk not in game.gen_queue:
            game.gen_queue.append(chunk)

    # Middle ring terrain
    for chunk in inner_ring:
        if chunk in game.terr_chunks:

            if not game.terr_chunks[chunk].loaded and chunk not in game.gen_queue:
                game.gen_queue.append(chunk)

        elif chunk not in game.gen_queue:
            game.gen_queue.append(chunk)


def render_terrain():
    """
    Renders the terrain.
    """
    c_x, c_y = game.player_chunk_pos

    inner_ring = [
        (c_x-1, c_y-1), (c_x, c_y-1), (c_x+1, c_y-1),
        (c_x-1, c_y), (c_x, c_y), (c_x+1, c_y),
        (c_x-1, c_y+1), (c_x, c_y+1), (c_x+1, c_y+1)
    ]

    middle_ring = [
        (c_x-2, c_y-2), (c_x-1, c_y-2), (c_x, c_y-2), (c_x+1, c_y-2), (c_x+2, c_y-2),
        (c_x-2, c_y-1), (c_x+2, c_y-1),
        (c_x-2, c_y),   (c_x+2, c_y),
        (c_x-2, c_y+1), (c_x+2, c_y+1),
        (c_x-2, c_y+2), (c_x-1, c_y+2), (c_x, c_y+2), (c_x+1, c_y+2), (c_x+2, c_y+2)
    ]

    for v2 in inner_ring + middle_ring:
        if v2 in game.terr_chunks:
            game.terr_chunks[v2].render_chunk()
    


def get_distance_to(start, end):
    """
    Returns the distance between two v2s.
    """
    return math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)



def get_terrain_info(v2):
    """
    Returns the terrain info of a v2.
    """
    chunk_pos = (math.floor(v2[0] / game.CHUNKSIZE), math.floor(v2[1] / game.CHUNKSIZE))
    inchunk_pos = (v2[0] % game.CHUNKSIZE, v2[1] % game.CHUNKSIZE)

    return game.terr_chunks[chunk_pos].tiles[inchunk_pos].tile



def get_neighbours(tile, end, neighbours, visited):
    """
    In-place function that adds new neighbouring tiles to a dictionary
    """
    x, y = tile

    neighbours_v2s = [(x-1, y), (x, y+1), (x, y-1), (x+1, y)]

    added_neighbours = False

    for neighbour in neighbours_v2s:

        if neighbour == end:
            neighbours[neighbour] = {
                "dist": get_distance_to(neighbour, end),
                "prev": tile
                }
            return True

        if get_terrain_info(neighbour) == "water":
            continue

        if neighbour in game.world_array:
            continue

        if neighbour in neighbours or neighbour in visited:
            continue
        
        neighbours[neighbour] = {
            "dist": get_distance_to(neighbour, end),
            "prev": tile
            }
        
        added_neighbours = True
    
    return added_neighbours


def reconstruct_path(start, end, neighbours):
    # Reconstruct positions from end to start (without directions yet)
    positions = [end]
    while positions[-1] != start:
        positions.append(neighbours[positions[-1]]["prev"])

    positions.reverse()  # Now from start to end

    path = []
    for i in range(len(positions)-1):
        pos = positions[i]


        x_off = positions[i+1][0] - pos[0]
        y_off = positions[i+1][1] - pos[1]

        if x_off == 1:
            direction = "e"
        elif x_off == -1:
            direction = "w"
        elif y_off == 1:
            direction = "s"
        elif y_off == -1:
            direction = "n"

        path.append((pos, direction))

    return path




def pathfind(start, end):
    """
    Returns a list of v2s that form a path from start to end.

    - Gives up if it takes too long to find a path (attempts > distance^2)
    """

    max_attempts = get_distance_to(start, end)**2
    attempts = 0

    neighbours = {}
    visited = set()

    neighbours[start] = {
        "dist": get_distance_to(start, end),
        "prev": None
        }
    
    if get_terrain_info(end) == "water":
        return False
    
    if end in game.world_array:
        return False
    
    if not get_neighbours(start, end, neighbours, visited):
        return False

    while True:
        # Develop the path from tile closest to end
        closest = min(neighbours, key=lambda k: neighbours[k]["dist"])
        if closest in visited:
            neighbours[closest]["dist"] += 1
            continue

        visited.add(closest)

        if closest == end:
            break

        attempts += 1
        if attempts >= max_attempts:
            return False

        get_neighbours(closest, end, neighbours, visited)

        # Check if there are no more unvisited neighbours
        no_neighbours = True
        for neighbour in neighbours:
            if neighbour not in visited:
                no_neighbours = False
        
        if no_neighbours:
            return
    
    if end not in neighbours:
        return False
        
    return reconstruct_path(start, end, neighbours)
    



        

