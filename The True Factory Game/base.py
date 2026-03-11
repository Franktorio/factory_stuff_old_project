# Factory game [entity constructors]
# Author: Frank MR
# May 26th 2025

import math

# Custom imports
from state import game
import rendering



class Placeable(rendering.OnWorldObject):
    """
    Parent class of anything that is placed on the grid.
    """
    def __init__(self, rotation, position, dimensions, has_input=False, has_output=False, is_conveyor=False, in_capacity=0, out_capacity=0, ghost=True):
        super().__init__(rotation, position, dimensions)

        self.MAX_UNIQUE_ITEMS = 5

        self.has_input = has_input
        self.has_output = has_output
        self.is_conveyor = is_conveyor

        if has_input:
            self.input_inv = {}
            self.in_capacity = in_capacity
        if has_output:
            self.output_inv = []
            self.out_capacity = out_capacity
        
        if is_conveyor:
            self.CONVEYOR_SPEED = 2
            self.conv_inventory = None # Conveyors can only hold 1 item

        self.world_pos = (position[0] // game.TILESIZE, position[1] // game.TILESIZE)
        if not ghost:
            self.standing_on = []
        self.output_tile = None


    def update(self):
        """PLACEHOLDER, MUST BE OVERWRITTEN"""
        pass

    def place(self, pos):
        """Places the building centered on the grid at the given position"""
        self.tiles = []

        # Get where the top-left tile should go
        topleft_tile_x = (pos[0] // game.TILESIZE) - self.dimensions[0] // 2
        topleft_tile_y = (pos[1] // game.TILESIZE) - self.dimensions[1] // 2

        for x in range(self.dimensions[0]):
            for y in range(self.dimensions[1]):
                current_tile = (topleft_tile_x + x, topleft_tile_y + y)
                chunk_tile = (current_tile[0] // game.CHUNKSIZE, current_tile[1] // game.CHUNKSIZE)
                inchunk_tile = (current_tile[0] % game.CHUNKSIZE, current_tile[1] % game.CHUNKSIZE)

                tile = game.terr_chunks[chunk_tile].tiles[inchunk_tile]

                self.standing_on.append(tile)

                # Check if there is something placed down or if the block is water
                if current_tile in game.world_array or tile.tile == "water":
                    self.list.remove(self)
                    return False
                self.tiles.append(current_tile)

        for tile in self.tiles:
            game.world_array[tile] = self
        
        # Place placeable's center in the snapped mouse position (not the same as tile world position)
        self.rect.center = pos
        try:
            if not self.has_output and not self.is_conveyor:
                print("no output tile")
                return
            

            center_tile = (topleft_tile_x + self.dimensions[0] // 2, topleft_tile_y + self.dimensions[1] // 2)
            self.world_pos = center_tile
            match self.rotation:
                case "n":
                    self.output_tile = (center_tile[0], center_tile[1] - (self.dimensions[1]//2 + 1))
                case "e":
                    self.output_tile = (center_tile[0] + (self.dimensions[0]//2 + 1), center_tile[1])
                case "s":
                    self.output_tile = (center_tile[0], center_tile[1] + (self.dimensions[1]//2 + 1))
                case "w":
                    self.output_tile = (center_tile[0] - (self.dimensions[0]//2 + 1), center_tile[1])
        except Exception as e:
            print("Exception:", e)


        return True

    """
    Inventory handling and item creation
    """
    def add_input(self, item):
        """
        Add an item to the building's input inventory.
        """
        if item in self.input_inv:
            if self.input_inv[item] < self.in_capacity:
                self.input_inv[item] += 1
        else:
            if len(self.input_inv) < self.MAX_UNIQUE_ITEMS:
                self.input_inv[item] = 1
    
    def add_output(self, item):
        """
        Add an item to the building's output inventory.
        """
        if len(self.output_inv) < self.out_capacity:
            self.output_inv.append(item)

    def update_building(self):
        """
        Update the building's output inventory based on the target's input inventory.
        """

        # Remove any items in input inv if they are 0
        if self.has_input:
            for item in self.input_inv.copy():
                if self.input_inv[item] == 0:
                    del self.input_inv[item]

        # Try to move output inventory items outside
        if len(self.output_inv) > 0 and self.output_tile in game.world_array:
            target_tile = game.world_array[self.output_tile]

            if target_tile.has_input:
                for item in self.output_inv:
                    if item in target_tile.input_inv:
                        
                        if target_tile.input_inv[item] < target_tile.in_capacity:
                            target_tile.input_inv[item] += 1
                            self.output_inv.remove(item)
                    else:
                        if len(target_tile.input_inv) < target_tile.MAX_UNIQUE_ITEMS:
                            target_tile.input_inv[item] = 1
                            self.output_inv.remove(item)

            elif target_tile.is_conveyor and target_tile.conv_inventory == None:
                x_off, y_off = game.OFFSETS[self.rotation]
                item_orign = (self.output_tile[0]+x_off)*game.TILESIZE, (self.output_tile[1]+y_off)*game.TILESIZE
                item_class = self.output_inv.pop(0)
                item = item_class(rotation=self.rotation, position=item_orign)
                target_tile.conv_inventory = item
                
    def update_conveyor(self):
        """
        Update the conveyor.
        """
        if self.conv_inventory == None:
            return
        
        item = self.conv_inventory

        # Align item to the middle of conveyor first
        if self.rotation in ["n", "s"] and item.rect.centerx != self.rect.centerx:
            if item.rect.centerx < self.rect.centerx:
                item.rect.move_ip(self.CONVEYOR_SPEED, 0)
            else:
                item.rect.move_ip(-self.CONVEYOR_SPEED, 0)

            if abs(item.rect.centerx - self.rect.centerx) <= self.CONVEYOR_SPEED:
                item.rect.centerx = self.rect.centerx
            return

        elif self.rotation in ["e", "w"] and item.rect.centery != self.rect.centery:
            if item.rect.centery < self.rect.centery:
                item.rect.move_ip(0, self.CONVEYOR_SPEED)
            else:
                item.rect.move_ip(0, -self.CONVEYOR_SPEED)

            if abs(item.rect.centery - self.rect.centery) <= self.CONVEYOR_SPEED:
                item.rect.centery = self.rect.centery
            return

        needs_to_pass = False

        if self.rotation == "n":
            if item.rect.top > self.rect.top:
                item.rect.move_ip(0, -self.CONVEYOR_SPEED)
            else:
                needs_to_pass = True

        elif self.rotation == "e":
            if item.rect.right < self.rect.right:
                item.rect.move_ip(self.CONVEYOR_SPEED, 0)
            else:
                needs_to_pass = True

        elif self.rotation == "s":
            if item.rect.bottom < self.rect.bottom:
                item.rect.move_ip(0, self.CONVEYOR_SPEED)
            else:
                needs_to_pass = True

        elif self.rotation == "w":
            if item.rect.left > self.rect.left:
                item.rect.move_ip(-self.CONVEYOR_SPEED, 0)
            else:
                needs_to_pass = True
        
        if needs_to_pass and self.output_tile in game.world_array:
            target_tile = game.world_array[self.output_tile]

            if target_tile.is_conveyor:
                if target_tile.conv_inventory == None:
                    target_tile.conv_inventory = item
                    self.conv_inventory = None

            elif len(target_tile.input_inv) < target_tile.MAX_UNIQUE_ITEMS:
                item_class = type(self.conv_inventory)

                if item_class in target_tile.input_inv:
                    if target_tile.input_inv[item_class] < target_tile.in_capacity:
                        target_tile.input_inv[item_class] += 1
                        self.conv_inventory.destroy()
                        self.conv_inventory = None
                elif len(target_tile.input_inv) < target_tile.MAX_UNIQUE_ITEMS:
                    target_tile.input_inv[item_class] = 1
                    self.conv_inventory.destroy()
                    self.conv_inventory = None

class Item(rendering.OnWorldObject):
    """
    Parent class of anything that is an item.
    """
    def __init__(self, rotation, position, dimensions=(0.5, 0.5)):
        super().__init__(rotation, position, dimensions)
        rendering.OnWorldObject.items.append(self)
        self.list = rendering.OnWorldObject.items


class Living(rendering.OnWorldObject):
    """
    Parent class of anything that is a living entity.
    """
    def __init__(self, rotation, position, speed, max_health=100, dimensions=(1, 1)):
        super().__init__(rotation, position, dimensions)
        rendering.OnWorldObject.entities.append(self)
        self.list = rendering.OnWorldObject.entities
        self.rect.center = position

        self.speed = speed
        self.max_health = max_health
        self.health = max_health

        self.max_inventory = 2
        self.inventory = []

        self.standing_on = None
    
    def damage(self, damage):
        """Damages or kills self if it loses all of its health"""
        self.health -= damage
        if self.health <= 0:
            self.destroy()
    
    def heal(self, heal):
        """Heals"""
        self.health += heal
        if self.health > self.max_health:
            self.health = self.max_health
    
    def add_inv(self, item_class):
        """
        Adds an item to inventory

        Returns True if it was added succesfully, false if not
        """
        if len(self.inventory) < self.max_inventory:
            self.inventory.append(item_class)
            return True
        return False
    
    def towards(self, tile_coord, speed):
        pass

    def update(self):
        """PLACEHOLDER, MUST BE OVERWRITTEN"""
        pass


class Building(Placeable):
    """
    Parent class of anything that is a building.
    """
    def __init__(self, rotation, position, dimensions, has_input=False, has_output=False, is_conveyor=False, in_capacity=0, out_capacity=0, ghost=True):
        super().__init__(rotation, position, dimensions, has_input, has_output, is_conveyor, in_capacity, out_capacity, ghost)
        if not ghost:
            rendering.OnWorldObject.buildings.append(self)
            self.list = rendering.OnWorldObject.buildings

class Entity(Placeable):
    """
    Parent class of anything that is an entity.
    """
    def __init__(self, rotation, position, dimensions, has_input=False, has_output=False, is_conveyor=False, in_capacity=0, out_capacity=0, ghost=True):
        super().__init__(rotation, position, dimensions, has_input, has_output, is_conveyor, in_capacity, out_capacity, ghost)
        if not ghost:
            rendering.OnWorldObject.entities.append(self)
            self.list = rendering.OnWorldObject.entities
