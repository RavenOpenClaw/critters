"""
Grass: A 1x1 world object that spreads to adjacent empty cells over time.
Grass has a condition (health) that degrades with trampling and recovers when undisturbed.
"""
import random
import pygame
from world_object import WorldObject

class Grass(WorldObject):
    def __init__(self, gx, gy, cell_size, spread_threshold=None):
        # Grass has no inventory
        super().__init__(gx, gy, width=1, height=1, cell_size=cell_size, inventory=None)
        # Use provided threshold or randomize between 30-120 seconds for natural variation
        if spread_threshold is None:
            spread_threshold = random.uniform(30.0, 120.0)
        self.spread_threshold = spread_threshold
        self.time_accumulator = 0.0
        # Grass does not block movement; critters can walk over it
        self.blocks_movement = False
        # Condition system: 0-100, starts full
        self.condition = 100.0
        self.max_condition = 100.0
        # Recovery rate (per second) when not trampled
        self.recovery_rate = 2.0
        # Note: world reference will be set by World.add_object

    def get_occupied_cells(self):
        """Grass does not block movement; return empty list."""
        return []

    def interact(self, player):
        """Do nothing when player interacts."""
        pass

    def update(self, dt):
        """
        Accumulate time; when threshold reached, attempt to spread to a random empty adjacent cell.
        Also handle condition recovery if not currently trampled, and removal if condition <= 0.
        Returns a new Grass object if spreading occurs, otherwise None.
        """
        world = getattr(self, 'world', None)
        if world is None:
            return None

        # Condition recovery: if not trampled this frame, slowly regain health
        if not world.is_trampled(self.gx, self.gy):
            self.condition = min(self.max_condition, self.condition + self.recovery_rate * dt)

        # Removal check
        if self.condition <= 0.0:
            # Remove self from world (if still present)
            if self in world.current_map.objects:
                world.remove_object(self)
            return None

        # Spreading logic
        self.time_accumulator += dt
        if self.time_accumulator >= self.spread_threshold:
            grid = world.grid
            # Find all adjacent (4-directional) empty cells not grass and not trampled
            neighbors = []
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx = self.gx + dx
                ny = self.gy + dy
                if grid.width is not None and grid.height is not None:
                    if not (0 <= nx < grid.width and 0 <= ny < grid.height):
                        continue
                if not grid.is_occupied(nx, ny) and (nx, ny) not in world.grass_cells and not world.is_trampled(nx, ny):
                    neighbors.append((nx, ny))
            if neighbors:
                ngx, ngy = random.choice(neighbors)
                new_grass = Grass(ngx, ngy, self.cell_size, spread_threshold=self.spread_threshold)
                # Reset accumulator after spreading
                self.time_accumulator = 0.0
                return new_grass
        return None

    def render(self, screen, camera=None):
        """Render grass as a green square, color varies with condition."""
        factor = max(0.0, self.condition / self.max_condition)
        r = int(144 * factor)
        g = int(238 * factor)
        b = int(144 * factor)
        
        draw_x, draw_y = self.x, self.y
        if camera:
            draw_x, draw_y = camera.apply(self.x, self.y)
            
        rect = pygame.Rect(
            draw_x,
            draw_y,
            self.width * self.cell_size,
            self.height * self.cell_size
        )
        pygame.draw.rect(screen, (r, g, b), rect)
