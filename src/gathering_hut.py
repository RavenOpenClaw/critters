"""
GatheringHut: A 3x3 building that serves as a base for critter gathering assignments.
"""
from building import Building
from inventory import Inventory

class GatheringHut(Building):
    """Gathering Hut building (3x3) with storage and critter assignment."""
    def __init__(self, gx, gy, cell_size):
        """
        Initialize a Gathering Hut.

        Args:
            gx, gy: grid coordinates for placement
            cell_size: size of a grid cell in world units
        """
        # Cost: not specified in Task 9; will be defined later when costs are balanced
        cost = {}  # Placeholder; likely will require wood, stone, etc.
        super().__init__(gx, gy, width=3, height=3, cell_size=cell_size, cost=cost)
        # Storage inventory for gathered resources
        self.storage = Inventory()
        # List of assigned critter references (to be defined later when Critter exists)
        self.assigned_critters = []
        # Gathering radius in world units (10 grid cells)
        self.gathering_radius = 10.0 * cell_size

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
