"""
ForesterHut: A building for automated sapling planting.
"""
from building import Building
from inventory import Inventory
from entity import Player
from constants import PROMPT_WITHDRAW, ITEM_SAPLING, BUILDING_FORESTER_HUT_COST

class ForesterHut(Building):
    """Forester's Hut (3x3) with storage for saplings and critter assignment."""
    cost = BUILDING_FORESTER_HUT_COST

    def __init__(self, gx, gy, cell_size):
        super().__init__(gx, gy, width=3, height=3, cell_size=cell_size, cost=self.cost)
        self.storage = Inventory()
        self.assigned_critters = []
        # Radius for planting
        self.gathering_radius = 20.0 * cell_size

    def assign_critter(self, critter):
        """Standard assignment logic."""
        critter.stop_follow()
        if critter in self.assigned_critters:
            return
        if critter.assigned_hut is not None and critter.assigned_hut is not self:
            critter.assigned_hut.unassign_critter(critter)
        
        self.assigned_critters.append(critter)
        critter.assigned_hut = self
        critter.start_return()

    def get_interaction_text(self):
        """Prompt for withdrawal or depositing saplings."""
        if self.storage.items:
            return "Manage Saplings: E"
        return "Deposit Saplings: E"

    def interact(self, player):
        """Handle sapling transfer."""
        if not isinstance(player, Player):
            return
            
        if player.following_critters:
            critter = player.following_critters[0]
            self.assign_critter(critter)
            if hasattr(self, 'world') and self.world:
                self.world.set_message("Critter assigned to Forester Hut.", 3.0)
            return

        # Withdraw saplings if any, otherwise deposit from player
        if self.storage.get_item_count(ITEM_SAPLING) > 0:
            qty = self.storage.get_item_count(ITEM_SAPLING)
            player.inventory.add(ITEM_SAPLING, qty)
            self.storage.remove(ITEM_SAPLING, qty)
            if hasattr(self, 'world') and self.world:
                self.world.set_message(f"Withdrew {qty} saplings.", 2.0)
        else:
            p_qty = player.inventory.get_item_count(ITEM_SAPLING)
            if p_qty > 0:
                player.inventory.remove(ITEM_SAPLING, p_qty)
                self.storage.add(ITEM_SAPLING, p_qty)
                if hasattr(self, 'world') and self.world:
                    self.world.set_message(f"Deposited {p_qty} saplings.", 2.0)
            else:
                if hasattr(self, 'world') and self.world:
                    self.world.set_message("No saplings to deposit.", 2.0)

    def can_gather(self):
        """Returns True so critters know they have work logic here."""
        return True

    def render(self, screen, camera=None):
        """Render a dark green building."""
        import pygame
        draw_x, draw_y = self.x, self.y
        if camera:
            draw_x, draw_y = camera.apply(self.x, self.y)
        rect = pygame.Rect(draw_x, draw_y, self.width*self.cell_size, self.height*self.cell_size)
        pygame.draw.rect(screen, (0, 100, 0), rect) # Dark Green
        pygame.draw.rect(screen, (0,0,0), rect, 2)
