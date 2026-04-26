"""
Campfire: A building that provides a Strength buff (increased gathering) when interacted with.
"""
from building import Building
from buff import Buff
from constants import BUFF_NAME_WARM

class Campfire(Building):
    """Campfire building (2x2) that grants the Strength gather buff."""
    cost = {"wood": 5, "stone": 2}  # class attribute for UI display

    def __init__(self, gx, gy, cell_size):
        super().__init__(gx, gy, width=2, height=2, cell_size=cell_size, cost=self.cost)

    def get_interaction_text(self):
        """Return None: campfire now provides automatic aura buff, no manual interaction needed."""
        return None

    def interact(self, other):
        """Optional: still allow manual buff for compatibility, but aura handles automatically."""
        from entity import Player
        if isinstance(other, Player):
            buff = Buff(BUFF_NAME_WARM, {'gather': 2.0}, duration=30.0)
            other.apply_buff(buff)

    def render(self, screen, camera=None):
        """Render the Campfire as a red rectangle."""
        import pygame
        draw_x, draw_y = self.x, self.y
        if camera:
            draw_x, draw_y = camera.apply(self.x, self.y)
            
        rect = pygame.Rect(
            draw_x,
            draw_y,
            self.width * self.cell_size,
            self.height * self.cell_size
        )
        pygame.draw.rect(screen, (255, 0, 0), rect)  # Red
