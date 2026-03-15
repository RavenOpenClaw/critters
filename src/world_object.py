"""
WorldObject base class: Extends Entity with grid-aligned placement, inventory, and occupancy.
"""
from entity import Entity

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
        self.inventory = inventory if inventory is not None else {}

    def get_occupied_cells(self):
        """Return list of grid cells occupied by this object."""
        cells = []
        for i in range(self.width):
            for j in range(self.height):
                cells.append((self.gx + i, self.gy + j))
        return cells

    def interact(self, other):
        """To be overridden by subclasses."""
        raise NotImplementedError
