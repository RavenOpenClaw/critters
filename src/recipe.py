"""
Recipe class: defines a craftable item and its costs.
"""
from dataclasses import dataclass

@dataclass
class Recipe:
    """A recipe that can be crafted by the player.

    Attributes:
        name: Human-readable recipe name.
        result: Identifier of the item produced (e.g., equipment ID).
        cost: Dictionary mapping resource types to required quantities.
        unlocks_equipment: If True, crafting unlocks the equipment in the player's equipment system.
    """
    name: str
    result: str
    cost: dict
    unlocks_equipment: bool = False
