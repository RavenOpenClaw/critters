"""
Grid system for spatial organization of world objects.
Uses a dictionary to map grid coordinates to occupied objects for fast lookup.
"""

class GridSystem:
    def __init__(self, cell_size=1.0):
        self.cell_size = cell_size
        self.occupied = {}  # (gx, gy) -> object

    def world_to_grid(self, x, y):
        """Convert world coordinates to grid cell indices."""
        gx = int(x // self.cell_size)
        gy = int(y // self.cell_size)
        return (gx, gy)

    def grid_to_world(self, gx, gy):
        """Convert grid cell indices to world coordinates (top-left corner of cell)."""
        return (gx * self.cell_size, gy * self.cell_size)

    def is_occupied(self, gx, gy):
        """Check if a grid cell is occupied."""
        return (gx, gy) in self.occupied

    def is_occupied_at(self, world_x, world_y):
        """Check if the grid cell containing the given world coordinate is occupied."""
        gx, gy = self.world_to_grid(world_x, world_y)
        return self.is_occupied(gx, gy)

    def get_neighbors(self, gx, gy):
        """Return the 4-directional adjacent grid cells."""
        return [
            (gx + 1, gy),
            (gx - 1, gy),
            (gx, gy + 1),
            (gx, gy - 1)
        ]

    def register(self, obj):
        """Register an object. Raises ValueError if any cell is already occupied."""
        cells = obj.get_occupied_cells()
        # Check for any existing occupation
        for cell in cells:
            if cell in self.occupied:
                raise ValueError(f"Cell {cell} is already occupied by another object")
        for cell in cells:
            self.occupied[cell] = obj

    def unregister(self, obj):
        """Unregister an object from all cells it occupies."""
        for cell in obj.get_occupied_cells():
            self.occupied.pop(cell, None)
