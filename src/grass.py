"""
Grass: A 1x1 world object that spreads to adjacent empty cells over time.
"""
import random
from world_object import WorldObject

class Grass(WorldObject):
    def __init__(self, gx, gy, cell_size, spread_threshold=5.0):
        # Grass has no inventory
        super().__init__(gx, gy, width=1, height=1, cell_size=cell_size, inventory=None)
        self.spread_threshold = spread_threshold
        self.time_accumulator = 0.0
        # Note: world reference will be set by World.add_object

    def interact(self, player):
        """Do nothing when player interacts"""

    def update(self, dt):
        """
        Accumulate time; when threshold reached, attempt to spread to a random empty adjacent cell.
        Returns a new Grass object if spreading occurs, otherwise None.
        """
        self.time_accumulator += dt
        if self.time_accumulator >= self.spread_threshold:
            # Access world via back-reference
            world = getattr(self, 'world', None)
            if world is None:
                return None
            grid = world.grid
            # Find all adjacent (including diagonals?) Design says "adjacent grid cell". Usually adjacent means 4-directional. But could be 8. Let's use 4-directional for simplicity (N, S, E, W). However, the property says "at least one empty adjacent grid cell" - adjacent could be 4. I'll use 4.
            neighbors = []
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx = self.gx + dx
                ny = self.gy + dy
                # Check grid bounds if defined
                if grid.width is not None and grid.height is not None:
                    if not (0 <= nx < grid.width and 0 <= ny < grid.height):
                        continue
                # Check if cell is free: not occupied and not trampled
                if not grid.is_occupied(nx, ny) and not self.world.is_trampled(nx, ny):
                    neighbors.append((nx, ny))
            if neighbors:
                ngx, ngy = random.choice(neighbors)
                new_grass = Grass(ngx, ngy, self.cell_size, spread_threshold=self.spread_threshold)
                # Reset accumulator after spreading
                self.time_accumulator = 0.0
                return new_grass
        return None
