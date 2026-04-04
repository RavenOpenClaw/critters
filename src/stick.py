"""
Stick: A small 1x1 world object that can be collected (non-renewable).
"""
import pygame
from world_object import WorldObject
from inventory import Inventory

class Stick(WorldObject):
    def __init__(self, gx, gy, cell_size, sticks=2):
        inventory = Inventory()
        inventory.add('wood', sticks)
        super().__init__(gx, gy, width=1, height=1, cell_size=cell_size, inventory=inventory)
        self.initial_wood = sticks

    def render(self, screen):
        # Draw as a small tan rectangle
        rect = pygame.Rect(
            self.x,
            self.y,
            self.width * self.cell_size,
            self.height * self.cell_size
        )
        pygame.draw.rect(screen, (210, 180, 140), rect)  # Tan/Light brown

    def interact(self, player):
        """Transfer wood from this object to the player's inventory, affected by gather buffs."""
        if self.inventory.has('wood', 1):
            mult = player.get_gather_multiplier()
            qty = max(1, int(round(mult)))
            available = self.inventory.get_item_count('wood')
            taken = min(qty, available)
            self.inventory.remove('wood', taken)
            player.inventory.add('wood', taken)

    def get_interaction_text(self):
        """Return prompt for interaction."""
        return "Pick up: E"
