"""
World: Container for all world entities, manages grid registration and rendering.
"""
class World:
    def __init__(self, grid):
        self.grid = grid
        self.objects = []
        # Trampled cells tracking: (gx, gy) -> remaining time (seconds)
        self.trampled = {}
        self.trample_duration = 5.0  # seconds before trampled status decays

    def add_object(self, obj):
        """Add a world object, ensuring it uses the grid's cell_size and registering it."""
        if not hasattr(obj, 'cell_size') or obj.cell_size != self.grid.cell_size:
            obj.cell_size = self.grid.cell_size
        # Register with grid first; may raise ValueError if overlapping
        self.grid.register(obj)
        self.objects.append(obj)
        # Set back-reference to world for objects that need it (e.g., Grass)
        obj.world = self

    def remove_object(self, obj):
        """Remove an object from the world and unregister from the grid."""
        if obj in self.objects:
            self.objects.remove(obj)
            self.grid.unregister(obj)

    def mark_trampled(self, gx, gy):
        """Mark a grid cell as trampled, resetting its decay timer."""
        self.trampled[(gx, gy)] = self.trample_duration

    def is_trampled(self, gx, gy):
        """Check if a grid cell is currently trampled."""
        return (gx, gy) in self.trampled

    def update_trampled(self, dt):
        """Update trampled status: decay timers and remove expired entries."""
        # Use list of keys to avoid modifying dict during iteration
        expired = []
        for cell, remaining in self.trampled.items():
            remaining -= dt
            if remaining <= 0:
                expired.append(cell)
            else:
                self.trampled[cell] = remaining
        for cell in expired:
            self.trampled.pop(cell, None)

    def draw(self, screen):
        """Render all world objects."""
        for obj in self.objects:
            if hasattr(obj, 'render'):
                obj.render(screen)
