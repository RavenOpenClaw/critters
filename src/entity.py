"""
Entity base class and Player class.
"""
from inventory import Inventory

class Entity:
    """Base entity with position and radius."""
    def __init__(self, x, y, radius=20):
        self.x = x
        self.y = y
        self.radius = radius

class Player(Entity):
    """Player entity with movement speed, world bounds, and interaction capabilities."""
    def __init__(self, x, y, radius=20, speed=200):
        super().__init__(x, y, radius)
        self.speed = speed  # pixels per second
        self.world_rect = None  # pygame.Rect for clamping; set externally
        self.inventory = Inventory()

    @property
    def interaction_radius(self):
        """Distance within which the player can interact with objects (2 × radius)."""
        return 2 * self.radius

    def move(self, dx, dy, dt, grid=None):
        """Move the player with collision detection and boundary clamping.

        If a GridSystem is provided, movement that would cause the player's circular
        boundary to overlap any occupied grid cell is blocked per-axis, allowing
        sliding along obstacles.
        """
        # X axis movement
        new_x = self.x + dx * self.speed * dt
        if grid is not None:
            if self._would_collide(new_x, self.y, grid):
                new_x = self.x  # Block X movement

        # Y axis movement
        new_y = self.y + dy * self.speed * dt
        if grid is not None:
            if self._would_collide(new_x, new_y, grid):
                new_y = self.y  # Block Y movement

        self.x = new_x
        self.y = new_y

        if self.world_rect:
            self.x = max(self.radius, min(self.x, self.world_rect.width - self.radius))
            self.y = max(self.radius, min(self.y, self.world_rect.height - self.radius))

    def _would_collide(self, x, y, grid):
        """Check if player at (x,y) would collide with any occupied grid cell."""
        left = x - self.radius
        right = x + self.radius
        top = y - self.radius
        bottom = y + self.radius
        gx_min, gy_min = grid.world_to_grid(left, top)
        gx_max, gy_max = grid.world_to_grid(right, bottom)
        for gx in range(gx_min, gx_max + 1):
            for gy in range(gy_min, gy_max + 1):
                if grid.is_occupied(gx, gy):
                    return True
        return False

    def interact(self, world):
        """Interact with the nearest world object within interaction_radius.

        Finds the closest object in world.objects whose center is within
        self.interaction_radius, and calls its interact(player) method.
        """
        nearest = None
        min_dist_sq = float('inf')
        for obj in getattr(world, 'objects', []):
            # Use object's center for distance
            if hasattr(obj, 'get_center'):
                ox, oy = obj.get_center()
            else:
                ox, oy = obj.x, obj.y
            dx = ox - self.x
            dy = oy - self.y
            dist_sq = dx*dx + dy*dy
            radius_sq = self.interaction_radius ** 2
            if dist_sq <= radius_sq and dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                nearest = obj
        if nearest is not None:
            nearest.interact(self)
