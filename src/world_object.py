"""
WorldObject base class: Extends Entity with grid-aligned placement, inventory, and occupancy.
"""
from entity import Entity
from inventory import Inventory

class WorldObject(Entity):
    def __init__(self, gx, gy, width, height, cell_size, inventory=None):
        # Convert grid top-left to world coordinates
        world_x = gx * cell_size
        world_y = gy * cell_size
        super().__init__(world_x, world_y, radius=0)  # radius unused for grid objects
        self.gx = gx
        self.gy = gy
        self.width = width   # in grid cells
        self.height = height # in grid cells
        self.cell_size = cell_size
        if inventory is None:
            self.inventory = Inventory()
        else:
            self.inventory = inventory
        # By default, objects block movement. Override in subclasses (e.g., Grass) to disable.
        self.blocks_movement = True

    def get_occupied_cells(self):
        """Return list of grid cells occupied by this object."""
        cells = []
        for i in range(self.width):
            for j in range(self.height):
                cells.append((self.gx + i, self.gy + j))
        return cells

    def get_center(self):
        """Return the world coordinate of the object's center."""
        center_x = self.x + (self.width * self.cell_size) / 2.0
        center_y = self.y + (self.height * self.cell_size) / 2.0
        return (center_x, center_y)

    def interact(self, other):
        """To be overridden by subclasses."""
        raise NotImplementedError

    def get_interaction_text(self):
        """
        Return text to display when a player is within interaction range,
        or None if no prompt.
        """
        return None
