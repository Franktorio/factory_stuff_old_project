"""
This module contains everything the game needs outside of logic and rendering

It includes:
- Every machine object (e.g. conveyor belts, furnaces, etc.)
- Every entity object (e.g. player, enemies, etc.)
- Every world object (e.g. trees, rocks, etc.)
- Every item object (e.g. resources, tools, etc.)

The logic or parent class for these objects should be in the entities module, this module only
shapes the objects like:
- Crafting recipes
- Images of objects
- Dimensions of objects
- Other properties (stack size, crafting speed, etc.)
"""

from . import player
from . import guis
from . import conveyor
from . import items
from . import drill
from . import assembler
from . import furnace