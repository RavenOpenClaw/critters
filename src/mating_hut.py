"""
MatingHut: A 2x2 building where critters can be assigned for breeding.
"""
from building import Building

class MatingHut(Building):
    """Mating Hut building (2x2) for critter breeding."""
    def __init__(self, gx, gy, cell_size):
        """
        Initialize a Mating Hut.

        Args:
            gx, gy: grid coordinates for placement
            cell_size: size of a grid cell in world units
        """
        # Cost to be defined later when balancing; free for now
        cost = {}
        super().__init__(gx, gy, width=2, height=2, cell_size=cell_size, cost=cost)
        # List of assigned critters
        self.assigned_critters = []

    def assign_critter(self, critter):
        """Assign a critter to this hut.

        Adds critter to the assigned_critters list and sets its assigned_hut reference.
        """
        self.assigned_critters.append(critter)
        critter.assigned_hut = self
