



import engine
import os
import content.items as items
from state import game

class Iron:
    images = engine.load_image_transformations([os.path.join(game.IMAGES_DIR, "iron.png") for _ in range(15)], dimensions=(2, 2))
    name = "Iron"
    item = items.RawIron