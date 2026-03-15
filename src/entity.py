"""
Entity base class and Player class.
"""

class Entity:
    """Base entity with position and radius."""
    def __init__(self, x, y, radius=20):
        self.x = x
        self.y = y
        self.radius = radius

class Player(Entity):
    """Player entity with movement speed and world bounds."""
    def __init__(self, x, y, radius=20, speed=200):
        super().__init__(x, y, radius)
        self.speed = speed  # pixels per second
        self.world_rect = None  # pygame.Rect for clamping; set externally

    def move(self, dx, dy, dt, grid=None):
        """Move the player with collision detection and boundary clamping.

        If a GridSystem is provided, movement that would cause the player's circular
        boundary to overlap any occupied grid cell is blocked.
        """
        new_x = self.x + dx * self.speed * dt
        new_y = self.y + dy * self.speed * dt

        if grid is not None:
            # Determine grid cells overlapped by the player's circle at the new position
            left = new_x - self.radius
            right = new_x + self.radius
            top = new_y - self.radius
            bottom = new_y + self.radius
            gx_min, gy_min = grid.world_to_grid(left, top)
            gx_max, gy_max = grid.world_to_grid(right, bottom)
            # Check all cells the circle may cover
            for gx in range(gx_min, gx_max + 1):
                for gy in range(gy_min, gy_max + 1):
                    if grid.is_occupied(gx, gy):
                        return  # Collision detected; block movement

        self.x = new_x
        self.y = new_y

        if self.world_rect:
            self.x = max(self.radius, min(self.x, self.world_rect.width - self.radius))
            self.y = max(self.radius, min(self.y, self.world_rect.height - self.radius))
