# Factory game [player constructors]
# Author: Frank MR
# May 26th 2025

import pygame
import os

# Custom imports
import rendering
import engine
from state import game


e_pressed = False
class Player(rendering.OnWorldObject):
    image_paths = []
    for _ in range(5):
        image_paths.append(os.path.join(game.IMAGES_DIR, "player_idle1.png"))
    for _ in range(5):
        image_paths.append(os.path.join(game.IMAGES_DIR, "player_idle2.png"))
    for _ in range(5):
        image_paths.append(os.path.join(game.IMAGES_DIR, "player_idle3.png"))
    images = engine.load_image_transformations(image_paths)

    def __init__(self, rotation="n", dimensions=(1, 1)):
        super().__init__(rotation=rotation, dimensions=dimensions, position=(0, 0))
        self.rect.center = (game.SCREEN_WIDTH / 2, game.SCREEN_HEIGHT / 2)
        self.speed = game.PLAYER_SPEED
        self.images = Player.images
        rendering.OnWorldObject.player.append(self)

        # Create the player inventory
        self.inventory_open = False
        self._make_inventory()

        self.selected = self.inventory_slots[0]["item"]
        self.curr_slot = self.inventory_slots[0]
        self.curr_slot["button"].selected = True

        self.interact_cd = 0
        self.last_pressed = []
    
    def _make_inventory(self):

        self.inventory_gui = []
        self.inventory_slots = {}

        slot_size_y = 12

        for i in range(40):
            self.inventory_slots[i] = {
                "text": rendering.GuiText(
                    text=f"#{None} | {0}",
                    screen_pos=(game.SCREEN_WIDTH - 180, (i * slot_size_y)+10+(10*i)+2),
                    font_size=slot_size_y,
                    color=(0, 0, 0),
                    hidden=True
                ),
                "button": rendering.GuiButton(
                    screen_pos=(game.SCREEN_WIDTH - 190, (i * slot_size_y)+10+(10*i)),
                    width_px=180,
                    height_px=slot_size_y+4,
                    color=(100, 100, 100),
                    hidden=True,
                    target_func= lambda x=i: self.select_item(self.inventory_slots[x])
                ),
                "item": [None, 0]
            }

        self.inventory_gui.append(rendering.GuiBackground(
            screen_pos=(game.SCREEN_WIDTH - 200, 0),
            width_px=200,
            height_px=game.SCREEN_HEIGHT,
            color=(48, 48, 48),
            hidden=True
        ))
        for slot in self.inventory_slots:
            self.inventory_gui.append(self.inventory_slots[slot]["text"])
            self.inventory_gui.append(self.inventory_slots[slot]["button"])
    
    def select_item(self, inv_slot):
        self.curr_slot["button"].selected = False
        self.selected = inv_slot["item"]
        self.curr_slot = inv_slot
        inv_slot["button"].selected = True
        
    def inventory_trigger(self):
        global e_pressed

        if not e_pressed:
            e_pressed = True
            if self.inventory_open:
                self.inventory_open = False
                for gui in self.inventory_gui:
                    gui.hidden = True
            else:
                self.inventory_open = True
                for gui in self.inventory_gui:
                    gui.hidden = False
    
    def add_to_inventory(self, item, amount):
        # Try to add to an existing stack first
        for slot in self.inventory_slots.values():
            slot_item = slot["item"]
            if slot_item[0] == item:
                slot_item[1] += amount
                return

        # Otherwise, add to the first empty slot
        for slot in self.inventory_slots.values():
            slot_item = slot["item"]
            if slot_item[0] is None:
                slot["item"] = [item, amount]
                if slot["button"].selected:
                    self.selected = slot["item"]
                return

    
    def remove_from_inventory(self, item, amount):
        """Removes an item from the players inventory"""
        for slot in self.inventory_slots.values():
            if slot["item"][0] == item:
                slot["item"][1] -= amount
                if slot["item"][1] <= 0:
                    slot["item"] = [None, 0]
                return
            
    def can_use(self, item, amount):
        """Checks if the player has enough of an item to use"""
        for slot in self.inventory_slots.values():
            if slot["item"][0] == item:
                if slot["item"][1] >= amount:
                    return True
        return False



    def update_inventory(self):
        for slot in self.inventory_slots:
            if self.inventory_slots[slot]["item"][1] == 0:
                self.inventory_slots[slot]["item"] = [None, 0]
                if self.curr_slot == self.inventory_slots[slot]:
                    self.selected = self.inventory_slots[slot]["item"]
            self.inventory_slots[slot]["text"].update_text(f"{self.inventory_slots[slot]['item'][0].name if self.inventory_slots[slot]['item'][0] else None} | {self.inventory_slots[slot]['item'][1] if self.inventory_slots[slot]['item'][1] else 'NA'}")

    def update(self):
        global e_pressed
        keys = game.keys_pressed

        self.update_inventory()

        if keys[pygame.K_e]:
            self.inventory_trigger()
        else:
            e_pressed = False

        if self.interact_cd > 0:
            self.interact_cd -= 1


        # Move the player based on key inputs
        if keys[pygame.K_w]:
            self.rect.y -= self.speed
            if "n" not in self.last_pressed:
                self.last_pressed.append("n")
        elif "n" in self.last_pressed:
            self.last_pressed.remove("n")
        
        if keys[pygame.K_s]:
            self.rect.y += self.speed
            if "s" not in self.last_pressed:
                self.last_pressed.append("s")
        elif "s" in self.last_pressed:
            self.last_pressed.remove("s")

        if keys[pygame.K_a]:
            self.rect.x -= self.speed
            if "w" not in self.last_pressed:
                self.last_pressed.append("w")
        elif "w" in self.last_pressed:
            self.last_pressed.remove("w")

        if keys[pygame.K_d]:
            self.rect.x += self.speed
            if "e" not in self.last_pressed:
                self.last_pressed.append("e")
        elif  "e" in self.last_pressed:
            self.last_pressed.remove("e")

        if self.last_pressed:
            self.rotation = self.last_pressed[-1]
        else:
            self.rotation = "n"

        
        

