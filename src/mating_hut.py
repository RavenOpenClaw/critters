"""
MatingHut: A 2x2 building where critters can be assigned for breeding.
"""
from building import Building
from critter import Critter, CritterState
import random

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
            return "Press E to breed critters"
        return None

    def interact(self, player):
        """Handle player interaction: assign following critter or breed.

        - If player has a following critter, assign it to this hut and stop following.
        - Otherwise, if hut has ≥2 assigned critters and player has 5 food, breed.
        """
        from entity import Player
        if not isinstance(player, Player):
            return

        # Assignment mode: if player has a following critter, assign it
        if player.following_critter is not None:
            critter = player.following_critter
            # Stop following behavior and clear reference
            critter.stop_follow()
            self.assign_critter(critter)
            player.following_critter = None
            if hasattr(self, 'world') and self.world is not None:
                self.world.set_message("Critter assigned to Mating Hut.", 2.0)
            return

        # Breeding mode
        if len(self.assigned_critters) < 2:
            if hasattr(self, 'world') and self.world is not None:
                self.world.set_message("Need at least 2 critters to breed!", 2.0)
            return

        if not player.inventory.has("food", self.BREED_FOOD_COST):
            if hasattr(self, 'world') and self.world is not None:
                self.world.set_message(f"Need {self.BREED_FOOD_COST} food to breed!", 2.0)
            return

        player.inventory.remove("food", self.BREED_FOOD_COST)
        if not hasattr(self, 'world') or self.world is None:
            return
        offspring = self.breed(self.world)
        if offspring:
            self.world.set_message("Breeding produced a new critter!", 3.0)

    def breed(self, world):
        """Breed two assigned critters to produce offspring.

        Requires at least two assigned critters.
        Offspring stats are the average of parents' stats, with a random mutation of ±5.
        Offspring is placed at the hut location and added to the given world.
        Returns the new Critter instance, or None if insufficient critters.
        """
        if len(self.assigned_critters) < 2:
            return None
        parent1, parent2 = self.assigned_critters[:2]
        return self._breed(parent1, parent2, world)

    def _breed(self, parent1, parent2, world):
        """Internal method to produce offspring from two parents."""
        # Compute average stats
        strength = (parent1.strength + parent2.strength) / 2
        speed_stat = (parent1.speed_stat + parent2.speed_stat) / 2
        endurance = (parent1.endurance + parent2.endurance) / 2

        # Apply random mutation: each stat ±5 (integer)
        mutation = random.randint(-5, 5)
        strength = int(round(strength)) + mutation
        speed_stat = int(round(speed_stat)) + mutation
        endurance = int(round(endurance)) + mutation

        # Clamp to [1, 100]
        strength = max(1, min(100, strength))
        speed_stat = max(1, min(100, speed_stat))
        endurance = max(1, min(100, endurance))

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
