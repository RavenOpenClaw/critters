"""
Tree: A 2x2 world object with wood that can be harvested and regenerates over time.
"""
import pygame
from world_object import WorldObject
from inventory import Inventory

class Tree(WorldObject):
    def __init__(self, gx, gy, cell_size, wood=10, respawn_duration=30.0):
        inventory = Inventory()
        inventory.add('wood', wood)
        super().__init__(gx, gy, width=2, height=2, cell_size=cell_size, inventory=inventory)
        self.max_wood = wood
        self.respawn_duration = respawn_duration
        self.depleted = False
        self.time_depleted = 0.0

    def update(self, dt):
        """Update regeneration timer and respawn if depleted."""
        if self.depleted:
            self.time_depleted += dt
            if self.time_depleted >= self.respawn_duration:
                # Respawn: replenish wood to max if wood can be replenished (max_wood not None)
                if self.max_wood is not None:
                    self.inventory.add('wood', self.max_wood)
                self.depleted = False
                self.time_depleted = 0.0
        else:
            # Check for depletion: if wood count reaches zero, mark as depleted
            if self.inventory.get_item_count('wood') == 0:
                self.depleted = True
                self.time_depleted = 0.0

    def render(self, screen, camera=None):
        # Draw trunk: a brown rectangle covering the whole 2x2 area
        draw_x, draw_y = self.x, self.y
        if camera:
            draw_x, draw_y = camera.apply(self.x, self.y)
            
        rect = pygame.Rect(
            draw_x,
            draw_y,
            self.width * self.cell_size,
            self.height * self.cell_size
        )
        pygame.draw.rect(screen, (101, 67, 33), rect)  # Brown trunk

    def interact(self, player):
        """Transfer wood from this tree to the player's inventory, affected by gather buffs."""
        if self.inventory.has('wood', 1):
            mult = player.get_gather_multiplier()
            qty = max(1, int(round(mult)))
            available = self.inventory.get_item_count('wood')
            taken = min(qty, available)
            self.inventory.remove('wood', taken)
            player.inventory.add('wood', taken)

    def get_interaction_text(self):
        """Return prompt for interaction."""
        return "Chop: E"
