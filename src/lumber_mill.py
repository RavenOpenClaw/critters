"""
LumberMill: A hub for automated wood gathering.
"""
from building import Building
from inventory import Inventory
from entity import Player
from tree import Tree
from constants import MSG_ASSIGN_GATHERING, PROMPT_WITHDRAW, ITEM_WOOD, ITEM_SAPLING, BUILDING_LUMBER_MILL_COST

class LumberMill(Building):
    """Lumber Mill building (3x3) with storage and critter assignment for wood."""
    cost = BUILDING_LUMBER_MILL_COST # Costs only wood

    def __init__(self, gx, gy, cell_size):
        super().__init__(gx, gy, width=3, height=3, cell_size=cell_size, cost=self.cost)
        self.storage = Inventory()
        self.assigned_critters = []
        # Large radius for forestry (double the old default)
        self.gathering_radius = 20.0 * cell_size

    def assign_critter(self, critter):
        """Always stop following and transition to RETURN when assigned."""
        critter.stop_follow()
        if critter in self.assigned_critters:
            return
        if critter.assigned_hut is not None and critter.assigned_hut is not self:
            critter.assigned_hut.unassign_critter(critter)
        
        self.assigned_critters.append(critter)
        critter.assigned_hut = self
        critter.start_return()

    def find_resource_in_radius(self, world, critter):
        """Find non-depleted Trees within radius."""
        hut_cx, hut_cy = self.x + (self.width*self.cell_size)/2, self.y + (self.height*self.cell_size)/2
        radius_sq = self.gathering_radius ** 2
        
        candidates = []
        for obj in world.objects:
            if isinstance(obj, Tree):
                # Distance to tree center
                dx, dy = (obj.x + self.cell_size/2) - hut_cx, (obj.y + self.cell_size/2) - hut_cy
                if dx*dx + dy*dy <= radius_sq:
                    candidates.append(obj)
        
        if not candidates:
            return None
        import random
        return random.choice(candidates)

    def get_interaction_text(self):
        """Withdraw prompt."""
        if self.storage.items:
            return PROMPT_WITHDRAW
        return None

    def interact(self, player):
        """Assign follower or withdraw storage (wood and saplings)."""
        if not isinstance(player, Player):
            return
            
        if player.following_critters:
            critter = player.following_critters[0]
            self.assign_critter(critter)
            if hasattr(self, 'world') and self.world:
                self.world.set_message("Critter assigned to Lumber Mill.", 3.0)
            return

        # Always Withdraw via interact (E)
        for item, qty in list(self.storage.items.items()):
            player.inventory.add(item, qty)
            del self.storage.items[item]
        if hasattr(self, 'world') and self.world:
            self.world.set_message("Withdrew all wood and saplings.", 2.0)

    def deposit(self, player):
        """Explicit deposit logic via F key."""
        from constants import ITEM_WOOD, ITEM_SAPLING
        # Transfer all wood and saplings from player to storage
        deposited = False
        for res in [ITEM_WOOD, ITEM_SAPLING]:
            qty = player.inventory.get_item_count(res)
            if qty > 0:
                player.inventory.remove(res, qty)
                self.storage.add(res, qty)
                deposited = True
        
        if deposited:
            if hasattr(self, 'world') and self.world:
                self.world.set_message("Deposited resources.", 2.0)
        else:
            if hasattr(self, 'world') and self.world:
                self.world.set_message("Nothing to deposit (Wood/Saplings).", 2.0)

    def can_gather(self):
        """Supports automated gathering."""
        return True

    def render(self, screen, camera=None):
        """Render a wood-colored rectangle."""
        import pygame
        draw_x, draw_y = self.x, self.y
        if camera:
            draw_x, draw_y = camera.apply(self.x, self.y)
        rect = pygame.Rect(draw_x, draw_y, self.width*self.cell_size, self.height*self.cell_size)
        pygame.draw.rect(screen, (101, 67, 33), rect) # Dark Brown
        pygame.draw.rect(screen, (0,0,0), rect, 2)
