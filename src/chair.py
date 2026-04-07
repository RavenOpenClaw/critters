"""
Chair: A building that provides a Rested buff (movement speed increase) when interacted with.
"""
from building import Building
from buff import Buff
from constants import PROMPT_REST, BUFF_NAME_RESTED

class Chair(Building):
    """Chair building (1x1) that grants the Rested speed buff."""
    cost = {"wood": 2}  # class attribute for UI display

    def __init__(self, gx, gy, cell_size):
        super().__init__(gx, gy, width=1, height=1, cell_size=cell_size, cost=self.cost)

    def get_interaction_text(self):
        """Return prompt to interact."""
        return PROMPT_REST

    def interact(self, other):
        """Apply Rested buff to the player."""
        from entity import Player  # Import Player from entity module
        if isinstance(other, Player):
            # Rested: 1.5x speed for 30 seconds
            buff = Buff(BUFF_NAME_RESTED, {'speed': 1.5}, duration=30.0)
            other.apply_buff(buff)

    def render(self, screen):
        """Render the Chair as a brown rectangle."""
        import pygame
        rect = pygame.Rect(
            self.x,
            self.y,
            self.width * self.cell_size,
            self.height * self.cell_size
        )
        pygame.draw.rect(screen, (210, 105, 30), rect)  # Chocolate brown
