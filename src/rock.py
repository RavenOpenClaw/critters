"""
Rock: A 1x1 world object with stone that can be harvested (non-renewable).
"""
import pygame
from world_object import WorldObject
from inventory import Inventory

class Rock(WorldObject):
    def __init__(self, gx, gy, cell_size, stone=3):
        inventory = Inventory()
        inventory.add('stone', stone)
        super().__init__(gx, gy, width=1, height=1, cell_size=cell_size, inventory=inventory)
        self.initial_stone = stone

    def render(self, screen):
        # Draw as a gray square/rectangle
        rect = pygame.Rect(
            self.x,
            self.y,
            self.width * self.cell_size,
            self.height * self.cell_size
        )
        pygame.draw.rect(screen, (128, 128, 128), rect)  # Gray

    def interact(self, player):
        """Transfer stone from this rock to the player's inventory, affected by gather buffs."""
        if self.inventory.has('stone', 1):
            mult = player.get_gather_multiplier()
            qty = max(1, int(round(mult)))
            available = self.inventory.get_item_count('stone')
            taken = min(qty, available)
            self.inventory.remove('stone', taken)
            player.inventory.add('stone', taken)

    def get_interaction_text(self):
        """Return prompt for interaction."""
        return "Mine: E"
