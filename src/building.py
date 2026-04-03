"""
Building base class: extends WorldObject with build cost and placement validation.
"""
import math
from world_object import WorldObject

class Building(WorldObject):
    """Base class for buildings. Extends WorldObject with cost and placement validation."""
    def __init__(self, gx, gy, width, height, cell_size, cost=None, inventory=None):
        """
        Initialize a building.

        Args:
            gx, gy: grid coordinates for top-left placement
            width, height: dimensions in grid cells
            cell_size: size of a grid cell in world units
            cost: dict mapping resource types to quantities required to build
            inventory: optional Inventory instance for building storage; if None, creates empty Inventory
        """
        super().__init__(gx, gy, width, height, cell_size, inventory=inventory)
        self.cost = cost if cost is not None else {}

    def can_place(self, player_inventory):
        """
        Check if the player has sufficient resources to place this building.

        Args:
            player_inventory: Inventory instance representing player's resources

        Returns:
            True if all required resources are present in sufficient quantity; False otherwise.
        """
        for resource, required in self.cost.items():
            if not player_inventory.has(resource, required):
                return False
        return True

    def deconstruct(self, world, player):
        """
        Deconstruct this building, refunding half the cost to the player and removing the building.

        Args:
            world: World instance containing this building
            player: Player instance to receive refunded resources
        """
        # Refund half of each resource cost, rounded up
        for resource, amount in self.cost.items():
            refund = math.ceil(amount * 0.5)
            if refund > 0:
                player.inventory.add(resource, refund)

        # Unassign any critters that were assigned to this building (if applicable)
        if hasattr(self, 'assigned_critters'):
            for critter in list(self.assigned_critters):
                critter.assigned_hut = None
            self.assigned_critters.clear()

        # Remove building from the world
        world.remove_object(self)
