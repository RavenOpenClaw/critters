"""
ReleaseBuilding: A 2x2 building that formalizes critter-to-candy conversion.
"""
import pygame
import random
from building import Building
from constants import ITEM_CANDY_STR, ITEM_CANDY_SPD, ITEM_CANDY_END, ITEM_WOOD, ITEM_STONE, MESSAGE_RELEASE_SUCCESS

class ReleaseBuilding(Building):
    """A 2x2 altar where critters can be released for candies."""
    def __init__(self, gx, gy, cell_size):
        # Cost: 10 wood, 10 stone (placeholder/standard for 2x2)
        cost = {ITEM_WOOD: 10, ITEM_STONE: 10}
        super().__init__(gx, gy, width=2, height=2, cell_size=cell_size, cost=cost)
        self.assigned_critters = [] # Not really used for long-term, but standard for assignment

    def assign_critter(self, critter):
        """Immediately release the critter upon assignment to the altar."""
        # Standard follow stop
        critter.stop_follow()
        
        # Determine candy type
        stats = {
            ITEM_CANDY_STR: critter.strength,
            ITEM_CANDY_SPD: critter.speed_stat,
            ITEM_CANDY_END: critter.endurance
        }
        max_val = max(stats.values())
        tied_candies = [name for name, val in stats.items() if val == max_val]
        chosen_candy = random.choice(tied_candies)

        # Award candy to player
        if hasattr(self, 'world') and self.world is not None:
            # We assume for now player is the recipient. 
            # In a real world check, we'd find the player reference.
            # For now, world message is the feedback.
            self.world.set_message(f"Critter released at Altar. Received {chosen_candy}.", 3.0)
            
            # Find player to add to inventory
            # This is a bit hacky until we have a central player ref in world, 
            # but world.current_map usually has a way to find entities.
            # In this engine, main loop usually handles inventory, 
            # but we'll try to find player in objects.
            for obj in self.world.current_map.objects:
                from entity import Player
                if isinstance(obj, Player):
                    obj.inventory.add(chosen_candy, 1)
                    break

            # Properly remove critter
            if getattr(critter, 'assigned_hut', None):
                critter.assigned_hut.unassign_critter(critter)
            self.world.remove_object(critter)

    def interact(self, player):
        """Allow player to assign current follower if interacting."""
        if player.following_critters:
            critter = player.following_critters[0]
            self.assign_critter(critter)
            return True
        return False

    def get_interaction_text(self):
        """Prompt to release if following."""
        return "Release Critter (E)"

    def render(self, screen, camera=None):
        """Draw a black square."""
        draw_x, draw_y = self.x, self.y
        if camera:
            draw_x, draw_y = camera.apply(self.x, self.y)
            
        rect = pygame.Rect(
            draw_x,
            draw_y,
            self.width * self.cell_size,
            self.height * self.cell_size
        )
        pygame.draw.rect(screen, (20, 20, 20), rect) # Very dark gray/black
        pygame.draw.rect(screen, (0, 0, 0), rect, 2) # Outline
