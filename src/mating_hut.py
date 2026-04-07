"""
MatingHut: A 2x2 building where critters can be assigned for breeding.
"""
from building import Building
from critter import Critter, CritterState
from constants import PROMPT_BREED, MSG_ASSIGN_MATING, MSG_BREED_NEED_TWO, MSG_BREED_NEED_FOOD, MSG_BREED_SUCCESS

class MatingHut(Building):
    """Mating Hut building (2x2) for critter building."""
    cost = {"wood": 15, "stone": 10}  # class attribute for UI display
    BREED_FOOD_COST = 5  # food cost per breeding

    def __init__(self, gx, gy, cell_size):
        super().__init__(gx, gy, width=2, height=2, cell_size=cell_size, cost=self.cost)
        self.assigned_critters = []

    def assign_critter(self, critter):
        """Assign a critter to this hut.

        If the critter is already assigned to another hut, unassign it first.
        If the critter is already assigned to this hut, do nothing.
        """
        # If already assigned to this hut, nothing to do
        if critter in self.assigned_critters:
            return
        # Unassign from previous hut if needed
        if critter.assigned_hut is not None and critter.assigned_hut is not self:
            critter.assigned_hut.unassign_critter(critter)
        self.assigned_critters.append(critter)
        critter.assigned_hut = self

    def get_interaction_text(self):
        """Return prompt if breeding is possible (at least 2 assigned critters)."""
        if len(self.assigned_critters) >= 2:
            return PROMPT_BREED
        return None

    def interact(self, player):
        """Handle player interaction: assign following critter or breed.

        - If player has a following critter, assign it to this hut and stop following.
        - Otherwise, if hut has ≥2 assigned critters and player has 5 food, breed.
        """
        from entity import Player
        if not isinstance(player, Player):
            return

        # Assignment mode: if player has any following critters, assign the first one
        if player.following_critters:
            critter = player.following_critters[0]
            # Stop following behavior and clear reference (stop_follow removes from list)
            critter.stop_follow()
            self.assign_critter(critter)
            # No need to clear player.following_critter; stop_follow already removed
            if hasattr(self, 'world') and self.world is not None:
                self.world.set_message(MSG_ASSIGN_MATING, 2.0)
            return

        # Breeding mode
        if len(self.assigned_critters) < 2:
            if hasattr(self, 'world') and self.world is not None:
                self.world.set_message(MSG_BREED_NEED_TWO, 2.0)
            return

        if not player.inventory.has("food", self.BREED_FOOD_COST):
            if hasattr(self, 'world') and self.world is not None:
                self.world.set_message(MSG_BREED_NEED_FOOD.format(self.BREED_FOOD_COST), 2.0)
            return

        player.inventory.remove("food", self.BREED_FOOD_COST)
        if not hasattr(self, 'world') or self.world is None:
            return
        offspring = self.breed(self.world)
        if offspring:
            self.world.set_message(MSG_BREED_SUCCESS, 3.0)

    def breed(self, world):
        """Breed two assigned critters to produce offspring.

        Requires at least two assigned critters.
        Offspring stats follow discrete tiers: weak (25/25/25), average (50/50/50), strong (75/75/75).
        Offspring is placed at the hut location and added to the given world.
        Returns the new Critter instance, or None if insufficient critters.
        """
        if len(self.assigned_critters) < 2:
            return None
        parent1, parent2 = self.assigned_critters[:2]
        return self._breed(parent1, parent2, world)

    def _breed(self, parent1, parent2, world):
        """Internal method to produce offspring from two parents.

        Offspring stats follow the discrete tier system:
        - weak: (25, 25, 25)
        - average: (50, 50, 50)
        - strong: (75, 75, 75)

        Tier determination:
        - If both parents have the same tier, offspring inherits that tier.
        - If parents have different tiers, offspring is average (50).
        """
        # Helper: determine a critter's tier based on average of its three stats
        def get_tier(c):
            avg = (c.strength + c.speed_stat + c.endurance) / 3
            if avg < 37.5:
                return 25
            elif avg < 62.5:
                return 50
            else:
                return 75

        tier1 = get_tier(parent1)
        tier2 = get_tier(parent2)
        offspring_tier = tier1 if tier1 == tier2 else 50

        # Assign uniform stats based on offspring tier
        strength = speed_stat = endurance = offspring_tier

        # Position: center of the hut's area in world coordinates
        world_x = self.x + (self.width * self.cell_size) / 2
        world_y = self.y + (self.height * self.cell_size) / 2

        # Create offspring Critter
        offspring = Critter(world_x, world_y, cell_size=self.cell_size,
                            strength=strength, speed_stat=speed_stat, endurance=endurance)
        offspring.state = CritterState.IDLE
        offspring.assigned_hut = self

        # Add to world
        world.add_object(offspring)

        return offspring

    def render(self, screen):
        """Render the MatingHut as a pink rectangle."""
        import pygame
        rect = pygame.Rect(
            self.x,
            self.y,
            self.width * self.cell_size,
            self.height * self.cell_size
        )
        pygame.draw.rect(screen, (255, 105, 180), rect)  # Hot pink
