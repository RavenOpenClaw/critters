"""
BerryBush: A 1x1 world object with berries that can be harvested.
"""
import pygame
from world_object import WorldObject

class BerryBush(WorldObject):
    def __init__(self, gx, gy, cell_size, berries=3):
        inventory = {'berry': berries}
        super().__init__(gx, gy, width=1, height=1, cell_size=cell_size, inventory=inventory)

    def render(self, screen):
        # Draw a green square at the bush's grid-aligned position
        rect = pygame.Rect(
            self.x,
            self.y,
            self.width * self.cell_size,
            self.height * self.cell_size
        )
        pygame.draw.rect(screen, (0, 200, 0), rect)  # Green

    def interact(self, player):
        """Transfer one berry from this bush to the player's inventory."""
        if self.inventory.get('berry', 0) > 0:
            self.inventory['berry'] -= 1
            player.inventory['berry'] = player.inventory.get('berry', 0) + 1
