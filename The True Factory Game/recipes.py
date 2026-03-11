# Factory game [recipes]
# Author: Franco MR
# May 26th 2025

"""
The recipes dictionary works as following:
- "ingredients": dictonary of items needed. 
- "product": dictionary of what the recipe outputs
- "time": the ticks its going to take for the item to craft (60 = 1s)

Ingredient and Product dictionaries need the item class as the key and the value as the amount needed
Make sure your recipe does use more items that what the crafter can carry (self.capacity)
"""

from content import items
from state import game

assembler_recipes = {
    items.RawIron: {
        "ingredients": {
            items.IronPlate: 5,
        },
        "product": (items.RawIron, 1),
        "time": 60
    }
}

furnace_recipes = {
    items.RawIron: {
        "output": (items.IronPlate, 3),
        "time": 60
    }
}