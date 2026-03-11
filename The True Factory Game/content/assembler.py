# Factory game [assembler constructor]
# Author: Frank MR
# May 26th 2025

import base
import engine
import os
import recipes
import rendering
import time
from state import game


class Assembler(base.Building):
    image_paths = []
    for i in range(15):
        image_paths.append(os.path.join(game.IMAGES_DIR, "assembler_1.png"))

    images = engine.load_image_transformations(image_paths, dimensions=(5, 5))

    name = "Assembler"

    def __init__(self, position, ghost, rotation):
        super().__init__(position=position, rotation=rotation, ghost=ghost, dimensions=(5, 5), has_input=True, has_output=True, in_capacity=10, out_capacity=10)
        self.recipe = None
        self.crafting = False
        self.curr_selected = 0
        self.progress = 0
        self.interacted = False

        if not ghost:
            self._make_gui()


    def _make_gui(self):
        self.gui = []
        gui_background = rendering.GuiBackground(
            center=(game.SCREEN_WIDTH//2, game.SCREEN_HEIGHT//2),
            width_px=700,
            height_px=500,
            color=(38, 38, 38)
        )
        
        recipe_container = rendering.GuiBox(
            center=(gui_background.rect.left+255, gui_background.rect.centery+20),
            width_px=500,
            height_px=450,
            color=(50, 50, 50)
        )
        info_container = rendering.GuiBox(
            center=(gui_background.rect.right-95, gui_background.rect.centery+20),
            width_px=180,
            height_px=450,
            color=(50, 50, 50)
        )
        
        self.gui.append(
            rendering.GuiButton(
                center=(gui_background.rect.right-30, gui_background.rect.top+25),
                width_px=20,
                height_px=20,
                color=(50, 50, 50),
                target_func=lambda: self._close_gui()
            )
        )
        self.gui.append(
            rendering.GuiText(
                center=self.gui[0].rect.center,
                text="X",
                color=(0, 0, 0),
                font_size=20
            )
        )
        self.gui.append(
            rendering.GuiText(
                center=(gui_background.rect.centerx, gui_background.rect.top+25),
                text="Assembler",
                color=(255, 255, 255),
                font_size=20
            )
        )
        self.gui.append(info_container)
        self.gui.append(recipe_container)
        self.gui.append(gui_background)

        self.buttons = []
        for i in range(len(game.unlocked_recipes)):
            recipe = game.unlocked_recipes[i]
            self.buttons.append(
                rendering.GuiButton(
                    center=(recipe_container.rect.centerx, (recipe_container.rect.top + 40 * i)+15),
                    width_px=450,
                    height_px=20,
                    color=(60, 60, 60),
                    target_func=lambda recipe=recipe, x=i: self._set_recipe(recipe, x)
                )
            )
            self.buttons.append(
                rendering.GuiText(
                    center=self.buttons[-1].rect.center,
                    text=recipe.name,
                    color=(255, 255, 255),
                    font_size=8
                )
            )
        for btn in self.buttons:
            self.gui.append(btn)

        self.info_text = {}
        self.info_text["header"] = rendering.GuiText(
                center=(info_container.rect.centerx, info_container.rect.top+20),
                text="Assembler Info",
                color=(255, 255, 255),
                font_size=15
            )
        self.info_text["header"].rect.left = info_container.rect.left+10
        
        self.info_text["recipe"] = rendering.GuiText(
                center=(info_container.rect.centerx, info_container.rect.top+40),
                text="Recipe: N/A",
                color=(255, 255, 255),
                font_size=10
            )
        self.info_text["recipe"].rect.left = info_container.rect.left+10
        
        self.info_text["progress"] = rendering.GuiText(
                center=(info_container.rect.centerx, info_container.rect.top+60),
                text="Progress: 0",
                color=(255, 255, 255),
                font_size=10
            )
        self.info_text["progress"].rect.left = info_container.rect.left+10
        
        self.info_text["OutInvLen"] = rendering.GuiText(
                center=(info_container.rect.centerx, info_container.rect.top+80),
                text=f"Output Capacity: {len(self.output_inv)}",
                color=(255, 255, 255),
                font_size=10
            )
        self.info_text["OutInvLen"].rect.left = info_container.rect.left+10

        self.info_text["InpInv"] = rendering.GuiText(
                center=(info_container.rect.centerx, info_container.rect.top+100),
                text="Input Inventory:",
                color=(255, 255, 255),
                font_size=10
            )
        self.info_text["InpInv"].rect.left = info_container.rect.left+10
        
        self.info_text["In#1"] = rendering.GuiText(
                center=(info_container.rect.centerx, info_container.rect.top+120),
                text="",
                color=(255, 255, 255),
                font_size=10
            )
        self.info_text["In#1"].rect.left = info_container.rect.left+10

        self.info_text["In#2"] = rendering.GuiText(
                center=(info_container.rect.centerx, info_container.rect.top+140),
                text="",
                color=(255, 255, 255),
                font_size=10
            )
        self.info_text["In#2"].rect.left = info_container.rect.left+10
        
        self.info_text["In#3"] = rendering.GuiText(
                center=(info_container.rect.centerx, info_container.rect.top+160),
                text="",
                color=(255, 255, 255),
                font_size=10
            )
        self.info_text["In#3"].rect.left = info_container.rect.left+10
        
        self.info_text["In#4"] = rendering.GuiText(
                center=(info_container.rect.centerx, info_container.rect.top+180),
                text="",
                color=(255, 255, 255),
                font_size=10
            )
        self.info_text["In#4"].rect.left = info_container.rect.left+10
        
        self.info_text["In#5"] = rendering.GuiText(
                center=(info_container.rect.centerx, info_container.rect.top+200),
                text="",
                color=(255, 255, 255),
                font_size=10
            )
        self.info_text["In#5"].rect.left = info_container.rect.left+10
        
        for text in self.info_text:
            self.gui.append(self.info_text[text])

        self.recipe_info = {}

        self.recipe_info["header"] = rendering.GuiText(
                center=(info_container.rect.centerx, info_container.rect.top+240),
                text="Recipe Info",
                color=(255, 255, 255),
                font_size=15
            )
        self.recipe_info["time"] = rendering.GuiText(
                center=(info_container.rect.centerx, info_container.rect.top+260),
                text="Craft Time: N/A",
                color=(255, 255, 255),
                font_size=10
            )
        self.recipe_info["time"].rect.left = info_container.rect.left+10

        self.recipe_info["subtitle"] = rendering.GuiText(
                center=(info_container.rect.centerx, info_container.rect.top+280),
                text="Ingredients:",
                color=(255, 255, 255),
                font_size=12
            )
        self.recipe_info["subtitle"].rect.left = info_container.rect.left+10

        self.recipe_info["ingr_1"] = rendering.GuiText(
                center=(info_container.rect.centerx, info_container.rect.top+300),
                text="",
                color=(255, 255, 255),
                font_size=10
            )
        self.recipe_info["ingr_1"].rect.left = info_container.rect.left+10

        self.recipe_info["ingr_2"] = rendering.GuiText(
                center=(info_container.rect.centerx, info_container.rect.top+320),
                text="",
                color=(255, 255, 255),
                font_size=10
            )
        self.recipe_info["ingr_2"].rect.left = info_container.rect.left+10

        self.recipe_info["ingr_3"] = rendering.GuiText(
                center=(info_container.rect.centerx, info_container.rect.top+340),
                text="",
                color=(255, 255, 255),
                font_size=10
            )
        self.recipe_info["ingr_3"].rect.left = info_container.rect.left+10

        self.recipe_info["ingr_4"] = rendering.GuiText(
                center=(info_container.rect.centerx, info_container.rect.top+360),
                text="",
                color=(255, 255, 255),
                font_size=10
            )
        self.recipe_info["ingr_4"].rect.left = info_container.rect.left+10

        self.recipe_info["ingr_5"] = rendering.GuiText(
                center=(info_container.rect.centerx, info_container.rect.top+380),
                text="",
                color=(255, 255, 255),
                font_size=10
            )
        self.recipe_info["ingr_5"].rect.left = info_container.rect.left+10

        for text in self.recipe_info:
            self.gui.append(self.recipe_info[text])
        
    def _set_recipe(self, recipe, btn):

        if recipe not in game.unlocked_recipes:
            return

        if self.recipe == recipes.assembler_recipes[recipe]:
            self.recipe = None
            self.buttons[self.curr_selected].selected = False
            self.info_text["recipe"].update_text("Recipe: N/A")
            return

        # Unselected the previous button
        self.buttons[self.curr_selected].selected = False
        self.curr_selected = btn

        # Select the new button
        self.buttons[btn].selected = True
        self.recipe = recipes.assembler_recipes[recipe]
        self.info_text["recipe"].update_text(f"Recipe: {recipe.name}")


    def _close_gui(self):
        for gui in self.gui:
            gui.hidden = True
    
    def interact(self):
        for gui in self.gui:
            gui.hidden = False
        

    def update(self):
        self.update_building()
    

        if self.recipe != None and not self.crafting:
            recipe_fulfilled = True
            ingredients = self.recipe["ingredients"]
            for ingredient in ingredients:

                if not (ingredient in self.input_inv and self.input_inv[ingredient] >= ingredients[ingredient]):
                    recipe_fulfilled = False
            

            if recipe_fulfilled and len(self.output_inv) < self.out_capacity:
                self.crafting = True
                for _ in range(self.recipe["product"][1]):
                    self.add_output(self.recipe["product"][0])
                for ingredient in ingredients:
                    self.input_inv[ingredient] -= ingredients[ingredient]

        elif self.crafting and self.recipe != None:
            self.progress += 1
            if self.progress >= self.recipe["time"]:
                self.progress = 0
                self.crafting = False
        
        self.info_text["progress"].update_text(f"Progress: {int((self.progress / (self.recipe['time'] if self.recipe else 100))*100)}%")
        self.info_text["OutInvLen"].update_text(f"Output Capacity: {self.out_capacity-len(self.output_inv)}")

        for i in range(5):
            if i < len(self.input_inv):
                self.info_text[f"In#{i+1}"].update_text(f"- {list(self.input_inv.keys())[i].name}: {self.input_inv[list(self.input_inv.keys())[i]]}")
            else:
                self.info_text[f"In#{i+1}"].update_text("")
            
            if self.recipe != None:
                if i < len(self.recipe["ingredients"]):
                    self.recipe_info[f"ingr_{i+1}"].update_text(f"- {list(self.recipe['ingredients'].keys())[i].name}: {self.recipe['ingredients'][list(self.recipe['ingredients'].keys())[i]]}")
            else:
                self.recipe_info[f"ingr_{i+1}"].update_text("")
        
