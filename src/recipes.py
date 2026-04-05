"""
Crafting recipes for equipment.
"""
from recipe import Recipe

# Define available recipes. Each recipe should correspond to an equipment item already registered in EQUIPMENT_REGISTRY.
RECIPES = [
    Recipe(
        name="Wooden Gatherer",
        result="wooden_gatherer",
        cost={"food": 10},
        unlocks_equipment=True
    ),
    Recipe(
        name="Steel Gatherer",
        result="steel_gatherer",
        cost={"food": 50},
        unlocks_equipment=True
    ),
    Recipe(
        name="Magic Gatherer",
        result="magic_gatherer",
        cost={"food": 200},
        unlocks_equipment=True
    ),
]
