"""
World: Container for all world entities, manages grid registration and rendering.
"""
class World:
    def __init__(self, grid):
        self.grid = grid
        self.objects = []

    def add_object(self, obj):
        """Add a world object, ensuring it uses the grid's cell_size and registering it."""
        if not hasattr(obj, 'cell_size') or obj.cell_size != self.grid.cell_size:
            obj.cell_size = self.grid.cell_size
        # Register with grid first; may raise ValueError if overlapping
        self.grid.register(obj)
        self.objects.append(obj)

    def remove_object(self, obj):
        """Remove an object from the world and unregister from the grid."""
        if obj in self.objects:
            self.objects.remove(obj)
            self.grid.unregister(obj)

    def draw(self, screen):
        """Render all world objects."""
        for obj in self.objects:
            if hasattr(obj, 'render'):
                obj.render(screen)
