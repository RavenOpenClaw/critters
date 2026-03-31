"""
Equipment system: Items that can be unlocked and equipped to provide stat bonuses.
"""
# Global registry of equipment by ID. Tests and game can populate this.
EQUIPMENT_REGISTRY = {}

class Equipment:
    """Equipment item that provides bonuses when equipped.

    Attributes:
        id: Unique identifier (string)
        name: Human-readable name
        gather_multiplier: Multiplier applied to gathering speed (1.0 = no bonus)
    """
    def __init__(self, id, name, gather_multiplier=1.0):
        self.id = id
        self.name = name
        self.gather_multiplier = gather_multiplier
        # Auto-register on creation
        EQUIPMENT_REGISTRY[id] = self

# Define some basic gathering equipment
Equipment("wooden_gatherer", "Wooden Gatherer", gather_multiplier=1.5)
Equipment("steel_gatherer", "Steel Gatherer", gather_multiplier=2.0)
Equipment("magic_gatherer", "Magic Gatherer", gather_multiplier=3.0)
