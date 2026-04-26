"""
BerryBush: A 1x1 world object with berries that can be harvested.
"""
import pygame
from world_object import WorldObject
from inventory import Inventory

class BerryBush(WorldObject):
    def __init__(self, gx, gy, cell_size, berries=3, respawn_duration=10.0):
        inventory = Inventory()
        inventory.add('food', berries)
        super().__init__(gx, gy, width=1, height=1, cell_size=cell_size, inventory=inventory)
        self.max_food = berries
        self.respawn_duration = respawn_duration
        self.depleted = False
        self.time_depleted = 0.0

    def update(self, dt):
        """Update regeneration timer and regrow food when not at max."""
        current = self.inventory.get_item_count('food')
        if current < self.max_food:
            self.time_depleted += dt
            if self.time_depleted >= self.respawn_duration:
                # Replenish food to max
                self.inventory.add('food', self.max_food - current)
                self.time_depleted = 0.0
        else:
            self.time_depleted = 0.0
        # Depleted flag indicates whether bush is empty (zero food)
        self.depleted = (self.inventory.get_item_count('food') == 0)

    def render(self, screen, camera=None):
        # Draw a green square at the bush's grid-aligned position
        draw_x, draw_y = self.x, self.y
        if camera:
            draw_x, draw_y = camera.apply(self.x, self.y)
            
        rect = pygame.Rect(
            draw_x,
            draw_y,
            self.width * self.cell_size,
            self.height * self.cell_size
        )
        pygame.draw.rect(screen, (0, 200, 0), rect)  # Green

        # Draw berries as small red circles if present
        food_count = self.inventory.get_item_count('food')
        if food_count > 0:
            # Determine positions: up to 5 berries arranged in a small pattern within the cell
            cell_size = self.cell_size
            # Offsets for up to 5 berries (relative to bush top-left)
            offsets = [
                (0.25, 0.25), (0.75, 0.25),
                (0.5, 0.5),
                (0.25, 0.75), (0.75, 0.75)
            ]
            radius = max(2, cell_size // 8)
            for i in range(min(food_count, len(offsets))):
                ox, oy = offsets[i]
                cx = draw_x + ox * cell_size
                cy = draw_y + oy * cell_size
                pygame.draw.circle(screen, (200, 0, 0), (int(cx), int(cy)), radius)

    def interact(self, player):
        """Transfer berries from this bush to the player's inventory, affected by gather buffs."""
        if self.inventory.has('food', 1):
            # Determine quantity based on player's gather multiplier
            mult = player.get_gather_multiplier()
            qty = max(1, int(round(mult)))
            available = self.inventory.get_item_count('food')
            taken = min(qty, available)
            self.inventory.remove('food', taken)
            player.inventory.add('food', taken)

    def get_interaction_text(self):
        """Return prompt for interaction."""
        return "Gather: E"
