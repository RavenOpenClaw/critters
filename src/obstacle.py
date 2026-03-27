"""
Obstacle: A world object that blocks movement until cleared by work.
"""
import pygame
from world_object import WorldObject

class Obstacle(WorldObject):
    def __init__(self, gx, gy, width, height, cell_size, work_units=10):
        super().__init__(gx, gy, width=width, height=height, cell_size=cell_size, inventory=None)
        self.work_units = work_units
        self.max_work_units = work_units

    def render(self, screen):
        # Draw a dark gray rectangle
        rect = pygame.Rect(
            self.x,
            self.y,
            self.width * self.cell_size,
            self.height * self.cell_size
        )
        pygame.draw.rect(screen, (80, 80, 80), rect)
        # Show work units remaining above obstacle
        font = pygame.font.SysFont(None, 20)
        text = font.render(str(self.work_units), True, (0, 0, 0))
        screen.blit(text, (self.x + 5, self.y + 5))

    def get_interaction_text(self):
        """Work required to clear."""
        if self.work_units > 0:
            return f"Work: {self.work_units}"
        return None

    def apply_work(self, amount):
        """Apply work to the obstacle, reducing work_units. Returns True if cleared."""
        self.work_units -= amount
        if self.work_units <= 0:
            self.work_units = 0
            # Auto-remove from world when cleared
            if hasattr(self, 'world'):
                self.world.remove_object(self)
            return True
        return False

    def interact(self, other):
        """Critter interacts with obstacle to apply work based on critter strength."""
        # Import Critter locally to avoid circular if needed
        from critter import Critter
        if isinstance(other, Critter):
            # Use effective strength (consider well-fed buff)
            strength = other._effective_stat(other.strength)
            # Work per interaction: use strength directly (or maybe strength // 2?). Let's use strength.
            return self.apply_work(strength)
        return False
