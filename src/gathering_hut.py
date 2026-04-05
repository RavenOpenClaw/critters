"""
GatheringHut: A 3x3 building that serves as a base for critter gathering assignments.
"""
from building import Building
from inventory import Inventory
from entity import Player
from berry_bush import BerryBush

class GatheringHut(Building):
    """Gathering Hut building (3x3) with storage and critter assignment."""
    cost = {"wood": 10, "stone": 5}  # class attribute for UI display

    def __init__(self, gx, gy, cell_size):
        """
        Initialize a Gathering Hut.

        Args:
            gx, gy: grid coordinates for placement
            cell_size: size of a grid cell in world units
        """
        super().__init__(gx, gy, width=3, height=3, cell_size=cell_size, cost=self.cost)
        # Storage inventory for gathered resources
        self.storage = Inventory()
        # List of assigned critter references (to be defined later when Critter exists)
        self.assigned_critters = []
        # Gathering radius in world units (10 grid cells)
        self.gathering_radius = 10.0 * cell_size

    def assign_critter(self, critter):
        """Assign a critter to this hut.

        Adds critter to the assigned_critters list and sets its assigned_hut reference.
        """
        self.assigned_critters.append(critter)
        critter.assigned_hut = self

    def find_resource_in_radius(self, world, critter):
        """
        Find a random resource-bearing world object within gathering radius of the hut.
        Resources are world objects with a non-empty inventory.

        Args:
            world: World instance containing objects.
            critter: The critter requesting (used for distance check relative to critter's current position?).

        Returns:
            A random resource object, or None if none found.
        """
        # Gather all resource objects within radius of hut center
        hut_cx = self.x + (self.width * self.cell_size) / 2
        hut_cy = self.y + (self.height * self.cell_size) / 2
        radius_sq = self.gathering_radius ** 2

        candidates = []
        for obj in world.objects:
            # Only berry bushes are gatherable by the Gathering Hut at this time.
            if isinstance(obj, BerryBush):
                # Compute distance from hut center to object center
                obj_cx = obj.x + (getattr(obj, 'width', 0) * getattr(obj, 'cell_size', 0)) / 2
                obj_cy = obj.y + (getattr(obj, 'height', 0) * getattr(obj, 'cell_size', 0)) / 2
                dx = obj_cx - hut_cx
                dy = obj_cy - hut_cy
                if dx*dx + dy*dy <= radius_sq:
                    candidates.append(obj)

        if not candidates:
            return None
        # Return a random choice
        import random
        return random.choice(candidates)

    def get_interaction_text(self):
        """Return prompt text if hut has resources to collect."""
        if self.storage.items:
            return "Press E to collect resources"
        return None

    def interact(self, other):
        """Transfer all storage contents to the interacting entity's inventory."""
        if not isinstance(other, Player):
            return  # Only player can withdraw
        # Transfer all items from hut storage to player inventory
        for item_name, count in list(self.storage.items.items()):
            other.inventory.add(item_name, count)
            # Remove from storage
            del self.storage.items[item_name]

    def render(self, screen):
        """Render the Gathering Hut as a brown rectangle."""
        import pygame
        rect = pygame.Rect(
            self.x,
            self.y,
            self.width * self.cell_size,
            self.height * self.cell_size
        )
        pygame.draw.rect(screen, (139, 69, 19), rect)  # Brown
