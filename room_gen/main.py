# Recursive minigames [main]
# Frank MR
# April 04 2025

# Built-in
import pygame

# Custom modules
import engine
from global_values import *

engine.initialize_game()

while True:
        # Start a fresh new frame without anything from the previous one
        game.SCREEN.fill((255,255,255))

        mouse_screen_pos = pygame.mouse.get_pos()
        mouse_world_pos = (
                mouse_screen_pos[0] + engine.camera.x_off,
                mouse_screen_pos[1] + engine.camera.y_off
        )
        key_inputs = pygame.key.get_pressed()

        engine.check_events(pygame.event.get())
        engine.update_player(key_inputs, mouse_world_pos)
        engine.update_room_gen()

        # Update the camera and get its values
        engine.camera.update()
        cam_values = ((engine.camera.x_off,engine.camera.y_off), game.zoom)

        # Update() renders the spritegroups onto the screen.
        game.gui.update()
        game.drawables.update(cam_values)
        game.entities.update(cam_values)
        game.obstacles.update(cam_values)

        # Update the screen and limit FPS
        pygame.display.update()
        game.FPS.tick(game.FPS_LIMIT)