"""
Crafting recipes for equipment.
"""
from recipe import Recipe
from constants import ITEM_FOOD

# Define available recipes. Each recipe should correspond to an equipment item already registered in EQUIPMENT_REGISTRY.
RECIPES = [
    Recipe(
        name="Wooden Gatherer",
        result="wooden_gatherer",
        cost={ITEM_FOOD: 10},
        unlocks_equipment=True
    ),
    Recipe(
        name="Steel Gatherer",
        result="steel_gatherer",
        cost={ITEM_FOOD: 50},
        unlocks_equipment=True
    ),
    Recipe(
        name="Magic Gatherer",
        result="magic_gatherer",
        cost={ITEM_FOOD: 200},
        unlocks_equipment=True
    ),
]
