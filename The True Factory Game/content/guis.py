# Factory game [gui constructor]
# Author: Frank MR
# May 26th 2025

import rendering
from state import game



top_left_bg = rendering.GuiBackground(
    screen_pos=(0, 0),
    width_px=150,
    height_px=50,
    color=(50, 50, 50),
    hidden=False
)
title_text = rendering.GuiText(
    center=(top_left_bg.rect.centerx, top_left_bg.rect.centery - 15),
    text="The True Factory Game",
    font_size=10,
    color=(255, 255, 255),
    hidden=False
)
settings_n_info_btn = rendering.GuiButton(
    center=(top_left_bg.rect.centerx, top_left_bg.rect.centery+5),
    width_px=140,
    height_px=20,
    color=(60, 60, 60),
    hidden=False,
    target_func=lambda: toggle_settings()
)
settings_n_info_btn_text = rendering.GuiText(
    center=(settings_n_info_btn.rect.centerx, settings_n_info_btn.rect.centery),
    text="Settings & Info",
    font_size=10,
    color=(255, 255, 255),
    hidden=False
)

settings_window = []
settings_window.append(rendering.GuiBackground(
    center=(game.SCREEN_WIDTH // 2, game.SCREEN_HEIGHT // 2),
    width_px=400,
    height_px=500,
    color=(50, 50, 50),
    hidden=True
))
settings_window.append(rendering.GuiBox(
    center=(settings_window[0].rect.centerx, settings_window[0].rect.top+30),
    width_px=300,
    height_px=50,
    color=(60, 60, 60),
    hidden=True
))
settings_window.append(rendering.GuiText(
    center=settings_window[1].rect.center,
    text="Settings & Info",
    font_size=16,
    color=(255, 255, 255),
    hidden=True
))


def toggle_settings():
    """
    Toggles the settings window.
    """
    if settings_window[0].hidden:
        for element in settings_window:
            element.hidden = False
    else:
        for element in settings_window:
            element.hidden = True


coordinates_text_bg = rendering.GuiBackground(
    screen_pos=(0, 40),
    width_px=100,
    height_px=25,
    color=(50, 50, 50),
    hidden=False
)
coordinates_text = rendering.GuiText(
    center=(coordinates_text_bg.rect.left+10, coordinates_text_bg.rect.centery),
    text="[0, 0]",
    font_size=10,
    color=(255, 255, 255),
    hidden=False
)