# Recursive minigames [objects]
# Frank MR
# April 04 2025

# Built-in
import pygame
import math

from global_values import *

# Independent objects
class Camera():
    """
    An invisible rect that starts at the middle of the screen
    It follows whatever its target is. Meaning, the camera is not bound to the player.
    """
    def __init__(self, target_rect):
        self.rect = pygame.Rect(game.SCREEN_WIDTH/2, game.SCREEN_HEIGHT/2, 1, 1)
        self.x_off = 0
        self.y_off = 0
        self.target_rect = target_rect
    
    def update(self):
        """
        Update the camera position to follow the target.
        """
        if self.target_rect != None:
            x_distance = self.rect.centerx - self.target_rect.centerx
            y_distance = self.rect.centery - self.target_rect.centery

            self.x_off -= x_distance
            self.y_off -= y_distance

            self.rect.center = self.target_rect.center

class GraphicalUserInterface(pygame.sprite.Sprite):
    """
    Makes things on the screen that don't affect the game.
    Always stays on screen.

    Any text will be placed in the center of the rect.
    """
    def __init__(self, topleft, text, text_size=12, text_font="Arial"):
        pygame.sprite.Sprite.__init__(self, game.gui)
        self.text = text
        self.font = pygame.font.SysFont(text_font, text_size)
        self.image = self.font.render(text, True, (0, 0, 0))  # Black text
        self.rect = self.image.get_rect(topleft=topleft)
    
    def update(self):
        """
        Puts the image on the screen
        """
        game.SCREEN.blit(self.image, self.rect.topleft)

    def update_text(self, new_text):
        """
        Update the text displayed by this GUI element.
        """
        self.text = new_text
        self.image = self.font.render(new_text, True, (255, 255, 255))
        self.rect = self.image.get_rect(center=self.rect.center)

class Room():
    """
    Generates a Room object that stores a dictionary containing room info.
    
    Properties of the rooms:
    "W" = Wall, generates obstacle
    "-" = Air, generates nothing
    "O" = Origin, generates a wall and defines where the room attaches with the directional marker of the last room.
    "D" = Door, generates a door object that can trigger a function when the player collides with it.

    ("1", "2", "3", "4") - Directional markers.
        1 - North
        2 - East
        3 - South
        4 - West
    The directional marker defines where around the marker the origin of the next room is placed

    """
    def __init__(self, room_dict):
        # Assigns name and array to the room
        print(room_dict["name"])
        self.array = room_dict["array"]

        # Filled when the room is generated, used to check collisions and unloading
        self.sprites = pygame.sprite.Group()
        self.doors = pygame.sprite.Group()
        self.entrances = []

        # Store data to validate next room that generates
        self.entrance_orientation = room_dict["entrance_orientation"]
        self.exit_orientation = room_dict["exit_orientation"]

        # The plug is used for connecting new room to previous room's socket
        # if room has no socket, it means the room can't generate more rooms. (e.g. end of game)
        self.plug = (0, 0)
        self.socket = (0, 0) # adjusted later on
        self.socket_dir = game.NO_SOCKET

        # From which
        orientation = room_dict["entrance_orientation"]

    
    def make_obstacle(self, center_pos, hidden=False):
        """
        Makes and obstacle at given position
        """
        # Create and add obstacle to the room's sprites
        new_obstacle = Obstacle(1,1,center_pos)
        new_obstacle.add(self.sprites)

        # Remove the obstacle from spritegroups to prevent obstacle from rendering
        if hidden:
            game.drawables.remove(new_obstacle)
            game.obstacles.remove(new_obstacle)

    def make_door(self, center_pos):
        """
        Makes a door at given position
        """
        new_door = Door(1, 1, center_pos)
        new_door.add(self.sprites)
        new_door.add(self.doors)

    def make_entrance(self, center_pos):
        """
        Makes an obstacle the is removed from rendering groups
        """
        new_entrance = Obstacle(1, 1, center_pos, (167, 50, 20))

        # Add to self's spritegroup and entrances
        self.entrances.append(new_entrance)
        self.sprites.add(new_entrance)

        # Remove from groups the obstacle is in
        game.drawables.remove(new_entrance)
        game.obstacles.remove(new_entrance)
    
    def close_entrance(self):
        """
        Adds the entrance blocks to the needed groups to be rendered and collided with
        """
        for entrance in self.entrances:
            game.drawables.add(entrance)
            game.obstacles.add(entrance)
    
    def kill_doors(self):
        """
        Destroys the door sprites in the spritegroup
        """
        for sprite in self.doors:
            sprite.kill()
    
    def unload(self):
        """
        Unloads the room, destroying everything that was generated.
        """

        # Kill every sprite the room created
        for sprite in self.sprites:
            sprite.kill()
        
        # Remove referance to the class
        game.loaded_rooms.remove(self)

    def generate_room(self, position=(-5*game.TILESIZE,-5*game.TILESIZE)):
        """
        Places the array on the screen creating every OnScreenObject necessary.

        <position> is the pos 1 tile away of previous room's socket (adjusted for direction).
        """
        # Go through room array
        for y in range(len(self.array)):
            for x in range(len(self.array[0])):
                
                # Match every letter in the array with an object
                block = self.array[y][x]
                match block:

                    # Make a wall for each of these cases
                    case game.WALL:
                        self.make_obstacle((x*game.TILESIZE,y*game.TILESIZE))

                    case game.PLUG:
                        self.plug = (x*game.TILESIZE, y*game.TILESIZE)
                        self.make_obstacle((x*game.TILESIZE,y*game.TILESIZE))
                    
                    case game.INV_PLUG:
                        self.plug = (x*game.TILESIZE, y*game.TILESIZE)
                        self.make_obstacle((x*game.TILESIZE,y*game.TILESIZE), True)

                    case game.NORTH_SOCKET:
                        self.socket = (x * game.TILESIZE, y * game.TILESIZE)
                        self.socket_dir = block
                        self.make_obstacle((x * game.TILESIZE, y * game.TILESIZE))

                    case game.EAST_SOCKET:
                        self.socket = (x * game.TILESIZE, y * game.TILESIZE)
                        self.socket_dir = block
                        self.make_obstacle((x * game.TILESIZE, y * game.TILESIZE))

                    case game.SOUTH_SOCKET:
                        self.socket = (x * game.TILESIZE, y * game.TILESIZE)
                        self.socket_dir = block
                        self.make_obstacle((x * game.TILESIZE, y * game.TILESIZE))

                    case game.WEST_SOCKET:
                        self.socket = (x * game.TILESIZE, y * game.TILESIZE)
                        self.socket_dir = block
                        self.make_obstacle((x * game.TILESIZE, y * game.TILESIZE))

                    # Other things
                    case game.DOOR:
                        self.make_door((x * game.TILESIZE, y * game.TILESIZE))
                    
                    case game.ENTRANCE:
                        self.make_entrance((x * game.TILESIZE, y * game.TILESIZE))
                        

        # Get distance where the whole room has to be moved to
        x_off, y_off = (
            self.plug[0] - position[0],
            self.plug[1] - position[1]
        )

        # Move socket
        self.socket = (self.socket[0]-x_off, self.socket[1]-y_off)

        # Adjust socket
        match self.socket_dir:
            case game.NORTH_SOCKET:
                self.socket = (self.socket[0], self.socket[1] - game.TILESIZE)
            case game.EAST_SOCKET:
                self.socket = (self.socket[0] + game.TILESIZE, self.socket[1])
            case game.SOUTH_SOCKET:
                self.socket = (self.socket[0], self.socket[1] + game.TILESIZE)
            case game.WEST_SOCKET:
                self.socket = (self.socket[0] - game.TILESIZE, self.socket[1])

        # Move entire room to designated position
        for sprite in self.sprites:
            sprite_rect = sprite.rect

            sprite_rect.centerx -= x_off
            sprite_rect.centery -= y_off
                
        # Add room to loaded room's list
        game.loaded_rooms.append(self)
    

# Parent classes of everything.
class OnWorldObject(pygame.sprite.Sprite):
    """
    Base for everything being placed on the screen.
    Only purpose is passing down the render function.
    """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, game.drawables)

    
    def render(self, cam_values):
        """
        Returns a rect that is adapted for camera offset and zoom level.

        Used this video to do this: https://www.youtube.com/watch?v=0fS5LaXiQ-Q&t=674s
        """
        # Get values from cam_values
        cam_offset, zoom_level = cam_values

        # Adjust for camera offset
        offset_rect = self.rect.move(cam_offset)

        # Create a temporal rect that will be adapted to zoom and offset levels
        new_rect = pygame.Rect(
            math.ceil(offset_rect.centerx - self.rect.height // 2),
            math.ceil(offset_rect.centery - self.rect.height // 2),
            math.ceil(self.rect.width * zoom_level),
            math.ceil(self.rect.height * zoom_level)
        )
        
        # Adjust the position
        new_rect.center = (
            self.rect.centerx*zoom_level - cam_offset[0]*zoom_level - game.SCREEN_WIDTH/2 * zoom_level + game.SCREEN_WIDTH/2,
            self.rect.centery*zoom_level - cam_offset[1]*zoom_level - game.SCREEN_WIDTH/2 * zoom_level + game.SCREEN_WIDTH/2
        )

        pygame.draw.rect(game.SCREEN, self.color, new_rect)
    
    def update(self, cam_values):
        """
        Passes this method down which must not be overriden.
        Only purpose is to render the object on the screen.
        """
        self.render(cam_values)

class Background(OnWorldObject):
    """
    Makes a block used just for the background.
    Does not interact with anything.
    """
    def __init__(self, base, height, position, color):

        self.image = pygame.Surface((base*game.TILESIZE, height*game.TILESIZE))
        self.image.fill(color)
        self.color = color
        self.rect = self.image.get_rect()
        self.rect.center = position

class Obstacle(OnWorldObject):
    """
    Makes an obstacle other entities can't move into.
    Father class to everything solid in the game.
    """
    def __init__(self, base, height, position, color=(50,50,50)):
        pygame.sprite.Sprite.__init__(self, game.obstacles)

        self.image = pygame.Surface((base*game.TILESIZE, height*game.TILESIZE))
        self.image.fill(color)
        self.color = color
        self.rect = self.image.get_rect()
        self.rect.center = position

class Entity(OnWorldObject):
    """
    Makes an entity that is non-collide but, can't move through obstacles.
    Father class to everything non-collideable or interactable.
    """
    def __init__(self, base, height, position, color):
        pygame.sprite.Sprite.__init__(self, game.entities)

        self.image = pygame.Surface((base*game.TILESIZE, height*game.TILESIZE))
        self.image.fill(color)
        self.color = color

        self.rect = self.image.get_rect()
        self.rect.center = position

    def get_dir_ratio(self, given_pos):
        """
        Returns an X and Y ratio from the rect to the given position.

        tuple of (int, int) -> tuple of (int, int)
        """
        x0, y0 = self.rect.center
        x1, y1 = given_pos

        x_dist = x0 - x1
        y_dist = y0 - y1

        A = max(y_dist, x_dist)
        B = min(y_dist, x_dist)
        C = math.sqrt((A ** 2) + (B ** 2))

        # Return 0 if there is no distane between some points
        if x_dist == 0 or y_dist == 0:
            return (0, 0)
        
        return(-(x_dist / C), -(y_dist / C))


# Children of the parent clases

class Door(Entity):
    """
    Entity that is destroyed when the player collides with it.
    """
    
    def __init__(self, base, height, position):
        super().__init__(base, height, position, color=(167, 50, 20))

class Player(Entity):
    """
    The entity the player controls.
    """

    def __init__(self, health):
        super().__init__(base=1, height=1, position=(0,0), color=(70,150,70))
        pygame.sprite.Sprite.__init__(self, game.player_group)

    
    def check_movement(self, inputs, mouse_pos):
        """
        Return a rect in position of where the player wants to move.
        """

        x_movmnt, y_movmnt = (0, 0)

        if inputs[pygame.K_w]:
            y_movmnt -= game.PLAYER_SPEED
        if inputs[pygame.K_a]:
            x_movmnt -= game.PLAYER_SPEED
        if inputs[pygame.K_s]:
            y_movmnt += game.PLAYER_SPEED
        if inputs[pygame.K_d]:
            x_movmnt += game.PLAYER_SPEED
        
        return (x_movmnt, y_movmnt)