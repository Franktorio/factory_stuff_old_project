# Factory game [rendering system]
# Author: Frank MR
# May 26th 2025

import pygame
import os


# Custom imports
from state import game


class Camera():
    """
    An invisible rect that starts at the middle of the screen.
    It follows whatever its target is. Meaning, the camera is not bound to the player.
    """
    def __init__(self, target_rect):
        self.rect = pygame.Rect(0, 0, game.SCREEN_WIDTH*1.8, game.SCREEN_HEIGHT*1.8)
        self.rect.center = (game.SCREEN_WIDTH // 2, game.SCREEN_HEIGHT // 2)
        self.x_off = 0
        self.y_off = 0
        self.target_rect = target_rect


    def update(self):
        """
        Update the camera position to follow the target in smooth increments.
        """
        if self.target_rect is not None:
            x_distance = (self.target_rect.centerx - self.rect.centerx + game.SCREEN_WIDTH//2) * 0.2
            y_distance = (self.target_rect.centery - self.rect.centery + game.SCREEN_HEIGHT//2) * 0.2

            self.rect.centerx += x_distance
            self.rect.centery += y_distance

            self.x_off = self.rect.centerx - game.SCREEN_WIDTH
            self.y_off = self.rect.centery - game.SCREEN_HEIGHT

            self.scaled_rect = self.rect.scale_by(1 / game.zoom)
            self.scaled_rect.center = self.target_rect.center



camera = Camera(None) # Global camera instance, initially with no target as it needs be passed down to OnWorldObject instances.
game.camera = camera

class OnWorldObject(pygame.sprite.Sprite):
    """
    Base for everything being placed on the screen.
    Only purpose is passing down the render function.
    It is not meant to be instantiated directly. Use this as a parent class for any object that should be rendered on the screen.

    rotation: str
        n = 0, e = 90, s = 180, w = 270
    
    dimensions: tuple
        The dimensions of the object in tiles, e.g. (2, 1) for a 2x1 tile object (make sure to have an image that fits).
        Defaults to (1, 1) if not specified.
    """
    entities = []
    items = []
    buildings = []
    player = []

    def __init__(self, rotation, position, dimensions=(1, 1)):
        super().__init__()
        self.rect = pygame.Rect(0, 0, game.TILESIZE * dimensions[0], game.TILESIZE * dimensions[1])
        self.rect.center = position
        self.dimensions = dimensions
        
        self.last_zoom = game.zoom
        self.rotation = rotation
    
    def is_on_screen(self):
        """
        Check if the object is on the screen.
        """
        return (
            camera.scaled_rect.left <= self.rect.centerx <= camera.scaled_rect.right and
            camera.scaled_rect.top <= self.rect.centery <= camera.scaled_rect.bottom
        )


    def render(self, camera=camera, alpha=255):
        """
        Render the object on the screen.
        """
        if not self.is_on_screen():
            return 0
        zoom = game.zoom
        cam_offset = (camera.x_off, camera.y_off)

        # Get the current image
        self.image = self.images[self.rotation][game.global_anim_frame][game.zoom]
        self.image.set_alpha(alpha)

        # Calculate world position relative to camera
        world_x = int(self.rect.centerx * zoom - cam_offset[0] * zoom)
        world_y = int(self.rect.centery * zoom - cam_offset[1] * zoom)

        # Position accordingly after scaling offset
        screen_x = int(world_x - game.SCREEN_WIDTH / 2 * zoom + game.SCREEN_WIDTH / 2)
        screen_y = int(world_y - game.SCREEN_HEIGHT / 2 * zoom + game.SCREEN_HEIGHT / 2)

        # Draw to screen
        blit_rect = self.image.get_rect(center=(screen_x, screen_y))
        game.SCREEN.blit(self.image, blit_rect)

        return 1
    
    def interact(self):
        """
        Called when the player interacts with this object.

        MUST BE OVERWRITTEN
        """
        pass

    def destroy(self):
        """Destroy itself and anything that was stored inside"""
        if self in self.list:
            self.list.remove(self)
        if hasattr(self, "tiles"):
            for tile in self.tiles:
                del game.world_array[tile]
        
        if hasattr(self, "conv_inventory"):
            if self.conv_inventory is not None:
                self.conv_inventory.destroy()

    
    @staticmethod
    def render_update():
        """
        Render every object on the screen with appropriate hierarchy.
        The final product will always have the player on top of everything else.
        Then any other entity, then buildings, and finally the terrain.
        """
        

        # Render entities
        for obj in OnWorldObject.entities:
            obj.update()
            obj.render()

        # Render items
        for obj in OnWorldObject.items:
            obj.render()

        # Render buildings
        for obj in OnWorldObject.buildings:
            obj.update()
            obj.render()

        # Render player
        for obj in OnWorldObject.player:
            obj.update()
            obj.render()
    
    @staticmethod
    def object_count():
        """
        Returns the total number of objects on the screen.
        """
        return len(OnWorldObject.terrain_blocks) + len(OnWorldObject.buildings) + len(OnWorldObject.entities) + len(OnWorldObject.items) + len(OnWorldObject.player)




class GraphicalUserInterface(pygame.sprite.Sprite):
    """
    Renders GUI menus fixed to the screen (HUD style).
    Positions are in screen space, not world space.
    """

    default_font_path = os.path.join(game.IMAGES_DIR, "Monocraft.ttf")

    all_guis = {} # Only used to check if mouse clicks this, not used for rendering

    gui_backgrounds = []
    gui_boxes = []
    gui_buttons = []
    gui_text = []

    def __init__(self, screen_pos=(0, 0), width_px=200, height_px=100, color=(0, 150, 255), hidden=True, border_radius=5):
        super().__init__()
        self.screen_pos = screen_pos
        self.width_px = width_px
        self.height_px = height_px
        self.color = color
        self.hidden = hidden
        self.border_radius = border_radius
        
        GraphicalUserInterface.all_guis[self] = self
    
    def update(self):
        if self in GraphicalUserInterface.all_guis:
            if self.hidden:
                GraphicalUserInterface.all_guis.pop(self)
        elif self not in GraphicalUserInterface.all_guis:
            if not self.hidden:
                GraphicalUserInterface.all_guis[self] = self
    
    def render(self):
        if self.hidden:
            return

        if type(self) != GuiText:
            pygame.draw.rect(game.SCREEN, self.color, (self.screen_pos[0], self.screen_pos[1], self.width_px, self.height_px), border_radius=self.border_radius)
        else:
            game.SCREEN.blit(self.image, self.rect)
    
    @staticmethod
    def render_update():
        for bgs in GraphicalUserInterface.gui_backgrounds:
            bgs.update()
            bgs.render()
        
        for box in GraphicalUserInterface.gui_boxes:
            box.update()
            box.render()
        
        for btn in GraphicalUserInterface.gui_buttons:
            btn.update()
            btn.render()
        
        for txt in GraphicalUserInterface.gui_text:
            txt.update()
            txt.render()

class GuiBackground(GraphicalUserInterface):
    """
    A background for a GUI element.
    """
    def __init__(self, screen_pos=(0, 0), width_px=200, height_px=100, color=(0, 150, 255), hidden=True, center=None, border_radius=5):
        super().__init__(screen_pos, width_px, height_px, color, hidden, border_radius)
        self.image = pygame.Surface((width_px, height_px))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        GraphicalUserInterface.gui_backgrounds.append(self)

        if center:
            self.rect.center = center
            self.screen_pos = self.rect.topleft
        else:
            self.rect.topleft = screen_pos


class GuiBox(GraphicalUserInterface):
    """
    A box for a GUI element, same thing as a background but this renders ontop of backgrounds and below buttons and text
    """
    def __init__(self, screen_pos=(0, 0), width_px=200, height_px=100, color=(0, 150, 255), hidden=True, center=None, border_radius=5):
        super().__init__(screen_pos, width_px, height_px, color, hidden, border_radius)
        self.image = pygame.Surface((width_px, height_px))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        GraphicalUserInterface.gui_backgrounds.append(self)

        if center:
            self.rect.center = center
            self.screen_pos = self.rect.topleft
        else:
            self.rect.topleft = screen_pos

class GuiButton(GraphicalUserInterface):
    """
    A button for a GUI element.
    """
    def __init__(self, screen_pos=(0, 0), width_px=200, height_px=100, color=(0, 150, 255), hidden=True, target_func=None, center=None, border_radius=5):
        super().__init__(screen_pos, width_px, height_px, color, hidden, border_radius)
        self.original_color = color
        self.image = pygame.Surface((width_px, height_px))
        self.color = self.original_color
        self.rect = self.image.get_rect()
        self.selected = False # Incase you want your button to be darker if it was pressed
        self.target_func = target_func
        GraphicalUserInterface.gui_buttons.append(self)

        if center:
            self.rect.center = center
            self.screen_pos = self.rect.topleft
        else:
            self.rect.topleft = screen_pos

    def _clamp_colors(self, r, g, b):
        """
        Clamp the color values to valid range.
        """
        return (max(0, min(r, 255)), max(0, min(g, 255)), max(0, min(b, 255)))
    
    def update(self):
        if self.selected:
            self.color = (self._clamp_colors(self.original_color[0] - 30, self.original_color[1] - 30, self.original_color[2] - 30))
        elif self.rect.collidepoint(game.mouse_screen_pos):
            self.hover()
        else:
            self.color = (self.original_color)
        
        super().update()

    def hover(self):
        """
        Called when the mouse is hovering over the button.
        """
        self.color = (self._clamp_colors(self.original_color[0] + 50, self.original_color[1] + 50, self.original_color[2] + 50))
    
    def interact(self):
        """
        Called when the button is clicked.
        """
        self.color = (self._clamp_colors(self.original_color[0] - 50, self.original_color[1] - 50, self.original_color[2] - 50))

        if self.target_func is not None:
            self.target_func()

class GuiText(GraphicalUserInterface):
    """
    Text for a GUI element.
    """
    def __init__(self, screen_pos=(0, 0), text="Placeholder", font_size=20, color=(255, 255, 255), hidden=True, center=None):
        super().__init__(screen_pos, 0, 0, color, hidden)
        self.text = text
        self.font_size = font_size
        self.font = pygame.font.Font(GraphicalUserInterface.default_font_path, font_size)
        self.image = self.font.render(text, True, color)
        self.rect = self.image.get_rect()
        GraphicalUserInterface.gui_text.append(self)

        if center:
            self.rect.center = center
            self.screen_pos = self.rect.topleft
        else:
            self.rect.topleft = screen_pos

    def update_text(self, new_text):
        self.text = new_text
        self.image = self.font.render(self.text, True, self.color)
