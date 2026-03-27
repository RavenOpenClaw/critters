"""
BerryBush: A 1x1 world object with berries that can be harvested.
"""
import pygame
from world_object import WorldObject
from inventory import Inventory

class BerryBush(WorldObject):
    def __init__(self, gx, gy, cell_size, berries=3, respawn_duration=10.0):
        inventory = Inventory()
        inventory.add('berry', berries)
        super().__init__(gx, gy, width=1, height=1, cell_size=cell_size, inventory=inventory)
        self.max_berries = berries
        self.respawn_duration = respawn_duration
        self.depleted = False
        self.time_depleted = 0.0

    def update(self, dt):
        """Update regeneration timer and respawn if depleted."""
        if self.depleted:
            self.time_depleted += dt
            if self.time_depleted >= self.respawn_duration:
                # Respawn: replenish berries to max
                self.inventory.add('berry', self.max_berries)
                self.depleted = False
                self.time_depleted = 0.0
        else:
            # Check for depletion: if berry count reaches zero, mark as depleted
            if self.inventory.get_item_count('berry') == 0:
                self.depleted = True
                self.time_depleted = 0.0

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
        if self.inventory.has('berry', 1):
            self.inventory.remove('berry', 1)
            player.inventory.add('berry', 1)

    def get_interaction_text(self):
        """Return prompt for interaction."""
        return "Gather: E"
