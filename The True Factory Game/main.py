# Factory game [mainloop]
# Author: Franco MR
# May 26th 2025

import pygame
import time
import math
import threading

# Custom imports
from state import game
import rendering
import engine

# Variables that do not need to be global
fps = 0
temp_counter = 0
game_loaded = False

####################################################################################################

def loading_screen_fn():
    """
    Show a loading screen that keeps the window responsive.
    """
    texts_shown = ["Loading", "Loading.", "Loading..", "Loading..."]
    font = pygame.font.Font(None, 36)
    while not game_loaded:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        game.SCREEN.fill((0, 0, 0))
        text = texts_shown.pop(0)
        texts_shown.append(text)
        text_pg = font.render(text, True, (255, 255, 255))
        text_rect = text_pg.get_rect(center=(game.SCREEN_WIDTH/2, game.SCREEN_HEIGHT/2))
        game.SCREEN.blit(text_pg, text_rect)
        pygame.display.update()
        time.sleep(0.5)


def load_content():
    global game_loaded, coordinate_text
    import content
    import world_gen
    player = content.player.Player()
    game.player = player
    rendering.camera.target_rect = player.rect
    rendering.camera.update()
    coordinate_text = content.guis.coordinates_text
    player.add_to_inventory(content.conveyor.Conveyor, 20000)
    player.add_to_inventory(content.drill.Drill, 2)
    player.add_to_inventory(content.assembler.Assembler, 1)
    player.add_to_inventory(content.furnace.Furnace, 2)


    GEN_NOISE_CHUNK = 50
    for x in range(-GEN_NOISE_CHUNK, GEN_NOISE_CHUNK):
        for y in range(-GEN_NOISE_CHUNK, GEN_NOISE_CHUNK):
            game.terr_chunks[(x, y)] = world_gen.terrain.Chunk(x, y)
    
    GEN_TERRAIN_CHUNKS = 20
    for x in range(-GEN_TERRAIN_CHUNKS, GEN_TERRAIN_CHUNKS):
        for y in range(-GEN_TERRAIN_CHUNKS, GEN_TERRAIN_CHUNKS):
            game.terr_chunks[(x, y)].gen_terrain()

    world_gen.terrain.start()
    game_loaded = True



def fps_counter():
    """
    Counts the fps of the game.
    """
    global fps
    while True:
        print(f"UPS: {fps} | Zoom: {game.zoom}")
        fps = 0
        time.sleep(1)

threading.Thread(target=loading_screen_fn).start()
threading.Thread(target=load_content).start()
threading.Thread(target=fps_counter).start()

while not game_loaded:
    pygame.event.pump()
    time.sleep(0.1)

####################################################################################################

while True:
    #print("================= Frame start =================")
    tmp = time.perf_counter()
    # Start a fresh new frame without anything from the previous one
    game.SCREEN.fill((0,0,0))

    # Get all mouse positions and key inputs
    game.mouse_screen_pos = pygame.mouse.get_pos()

    # I have no idea how I came up with this, this is a miracle that ocurred while changing a bunch of values around
    game.mouse_world_pos = (
        (game.mouse_screen_pos[0] - game.SCREEN_WIDTH/2) / game.zoom + rendering.camera.rect.centerx - game.SCREEN_WIDTH/2,
        (game.mouse_screen_pos[1] - game.SCREEN_HEIGHT/2) / game.zoom + rendering.camera.rect.centery - game.SCREEN_HEIGHT/2
    )

    game.snapped_mouse_pos = (
        round(game.mouse_world_pos[0] / game.TILESIZE) * game.TILESIZE,
        round(game.mouse_world_pos[1] / game.TILESIZE) * game.TILESIZE
    )

    game.tile_mouse_pos = (
        round(game.mouse_world_pos[0] / game.TILESIZE),
        round(game.mouse_world_pos[1] / game.TILESIZE)
    )

    game.chunk_mouse_pos = (
        math.floor(game.tile_mouse_pos[0] / game.CHUNKSIZE),
        math.floor(game.tile_mouse_pos[1] / game.CHUNKSIZE)
    )

    game.inchunk_mouse_pos = (
        game.tile_mouse_pos[0] % game.CHUNKSIZE,
        game.tile_mouse_pos[1] % game.CHUNKSIZE
    )

    game.player_world_pos = (
        math.floor(game.player.rect.centerx / game.TILESIZE),
        math.floor(game.player.rect.centery / game.TILESIZE)
    )

    game.player_chunk_pos = (
        math.floor(game.player_world_pos[0] / game.CHUNKSIZE),
        math.floor(game.player_world_pos[1] / game.CHUNKSIZE)
    )

    rendering.camera.update()

    engine.queue_chunks()
    engine.render_terrain()
    
    

    # Change global dictionary with all keys pressed
    game.keys_pressed = pygame.key.get_pressed()
    game.mouse_pressed = pygame.mouse.get_pressed(num_buttons=3)


    # Check changes from the player
    engine.handle_events()
    engine.update_inputs()

    # Increases the global animation frame
    temp_counter += 1
    if temp_counter > 4:
        if game.global_anim_frame >= game.MAX_ANIM_FRAME:
            game.global_anim_frame = 0
        else:

            game.global_anim_frame += 1

    # Render everything
    rendering.OnWorldObject.render_update() # Render and update everything placed down
    engine.update_ghost()
    coordinate_text.update_text(f"X: {game.player_world_pos[0]} Y: {game.player_world_pos[1]}")
    rendering.GraphicalUserInterface.render_update() # Render and update the graphical user interface

    # Update the screen
    pygame.display.update()
    game.FPS.tick(game.FPS_LIMIT)
    fps += 1


