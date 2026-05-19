"""
Sapling: A 1x1 world object that grows into a Tree over time.
Requires 8 empty surrounding cells to be placed.
"""
import random
import pygame
from world_object import WorldObject
from constants import ITEM_SAPLING

class Sapling(WorldObject):
    cost = {ITEM_SAPLING: 1} # Built from Build Menu

    def __init__(self, gx, gy, cell_size, growth_timer=None):
        super().__init__(gx, gy, width=1, height=1, cell_size=cell_size, inventory=None)
        # Random growth time between 2-3 minutes (120-180 seconds)
        if growth_timer is None:
            growth_timer = random.uniform(120.0, 180.0)
        self.growth_timer = growth_timer
        self.blocks_movement = True

    def update(self, dt):
        """Accumulate growth time and transform into a Tree when ready."""
        self.growth_timer -= dt
        if self.growth_timer <= 0:
            world = getattr(self, 'world', None)
            if world:
                from tree import Tree
                # Replace self with a fully grown Tree
                new_tree = Tree(self.gx, self.gy, self.cell_size)
                # Ensure the tree is added to the world
                world.remove_object(self)
                world.add_object(new_tree)
                return new_tree
        return None

    def can_place(self, inventory, cost_override=None):
        """Check if inventory has enough saplings to place this seedling."""
        check_cost = cost_override if cost_override is not None else self.cost
        for resource, amount in check_cost.items():
            if not inventory.has(resource, amount):
                return False
        return True

    @classmethod
    def can_place_at(cls, world, gx, gy):
        """
        Custom placement check: 
        1. Must have 8 empty surrounding cells.
        2. Cannot be within 2 radius of any player (prevents trapping).
        """
        grid = world.grid
        
        # 1. Check surrounding cells (standard 3x3 clearance)
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = gx + dx, gy + dy
                if not grid.is_within_bounds(nx, ny) or grid.is_occupied(nx, ny):
                    return False
        
        # 2. Check for player proximity (2 cells)
        from entity import Player
        # Use world.players if available, otherwise fallback to finding in objects
        players = []
        if hasattr(world, 'players'):
            players = world.players
        else:
            players = [obj for obj in world.objects if isinstance(obj, Player)]
            
        for p in players:
            pgx, pgy = grid.world_to_grid(p.x, p.y)
            # Distance check in grid cells (Euclidean or Manhattan? 2 cells is small enough)
            if abs(gx - pgx) <= 2 and abs(gy - pgy) <= 2:
                return False

        return True

    def render(self, screen, camera=None):
        """Render sapling as a small green seedling."""
        draw_x, draw_y = self.x, self.y
        if camera:
            draw_x, draw_y = camera.apply(self.x, self.y)
            
        # Draw small green circle or rectangle
        size = self.cell_size * 0.4
        rect = pygame.Rect(
            draw_x + (self.cell_size - size) // 2,
            draw_y + (self.cell_size - size) // 2,
            size,
            size
        )
        pygame.draw.rect(screen, (34, 139, 34), rect) # Forest Green
        pygame.draw.rect(screen, (0, 0, 0), rect, 1)
