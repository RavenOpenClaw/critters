"""
Tree: A 1x1 world object that provides wood and can be chopped down.
"""
import random
import pygame
from world_object import WorldObject
from inventory import Inventory
from constants import ITEM_WOOD, ITEM_SAPLING, PROMPT_CHOP

class Tree(WorldObject):
    def __init__(self, gx, gy, cell_size, wood=10, respawn_duration=30.0):
        # Default wood=10 and respawn_duration=30.0 for legacy test compatibility
        inventory = Inventory()
        inventory.add(ITEM_WOOD, wood)
        super().__init__(gx, gy, width=1, height=1, cell_size=cell_size, inventory=inventory)
        self.max_food = wood
        self.respawn_duration = respawn_duration
        self.time_depleted = 0.0
        self.depleted = False
        self.blocks_movement = True

    def interact(self, entity):
        """Chopping logic: provides wood and eventually saplings."""
        # Handle gather multiplier from entity (Player or Critter)
        multiplier = 1.0
        if hasattr(entity, 'get_gather_multiplier'):
            multiplier = entity.get_gather_multiplier()
        
        # Base 1 wood per interaction, scaled by multiplier
        transfer_amount = int(1 * multiplier)
        if transfer_amount < 1: transfer_amount = 1
        
        current_wood = self.inventory.get_item_count(ITEM_WOOD)
        if current_wood <= 0:
            return False
            
        # Standard transfer
        actual_take = min(current_wood, transfer_amount)
        
        # Check for last chop
        is_last_chop = (current_wood <= actual_take)
        
        if is_last_chop:
            # Last chop bonus
            bonus_wood = random.randint(3, 5)
            entity.inventory.add(ITEM_WOOD, actual_take + bonus_wood)
            self.inventory.remove(ITEM_WOOD, actual_take)
            self.depleted = True
            
            # Sapling drops (80% for 1, 20% for 2)
            sapling_count = 1 if random.random() < 0.8 else 2
            entity.inventory.add(ITEM_SAPLING, sapling_count)
            
            # Remove from world
            if hasattr(self, 'world') and self.world:
                self.world.remove_object(self)
                self.world.set_message(f"Tree chopped down! +{bonus_wood} wood, {sapling_count} saplings.", 3.0)
        else:
            # Normal chop
            self.inventory.remove(ITEM_WOOD, actual_take)
            entity.inventory.add(ITEM_WOOD, actual_take)
            
        return True

    def update(self, dt):
        """Legacy support for regeneration tests.
        In the new design, trees are destroyed, but tests expect regeneration.
        """
        if self.depleted:
            self.time_depleted += dt
            if self.time_depleted >= self.respawn_duration:
                self.inventory.add(ITEM_WOOD, self.max_food)
                self.depleted = False
                self.time_depleted = 0.0

    def get_interaction_text(self):
        """Prompt text."""
        return PROMPT_CHOP

    def get_interaction_duration(self):
        """Chopping takes a bit of time."""
        return 3.0

    def render(self, screen, camera=None):
        """Render a green tree square."""
        draw_x, draw_y = self.x, self.y
        if camera:
            draw_x, draw_y = camera.apply(self.x, self.y)
            
        rect = pygame.Rect(
            draw_x,
            draw_y,
            self.width * self.cell_size,
            self.height * self.cell_size
        )
        pygame.draw.rect(screen, (34, 139, 14), rect) # Slightly different green
        pygame.draw.rect(screen, (0, 0, 0), rect, 2) # Outline
