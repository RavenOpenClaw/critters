"""
MatingHut: A 2x2 building where critters can be assigned for breeding.
"""
from building import Building
from critter import Critter, CritterState
import random

class MatingHut(Building):
    """Mating Hut building (2x2) for critter building."""
    cost = {"wood": 15, "stone": 10}  # class attribute for UI display

    def __init__(self, gx, gy, cell_size):
        super().__init__(gx, gy, width=2, height=2, cell_size=cell_size, cost=self.cost)
        self.assigned_critters = []

    def assign_critter(self, critter):
        """Assign a critter to this hut.

        Adds critter to the assigned_critters list and sets its assigned_hut reference.
        """
        self.assigned_critters.append(critter)
        critter.assigned_hut = self

    def get_interaction_text(self):
        """Return prompt if breeding is possible (at least 2 assigned critters)."""
        if len(self.assigned_critters) >= 2:
            return "Press E to breed critters"
        return None

    def interact(self, other):
        """Trigger breeding when player interacts, if at least two critters are assigned."""
        from player import Player  # Avoid circular import at module level
        if not isinstance(other, Player):
            return
        # Breeding requires at least two assigned critters
        if len(self.assigned_critters) < 2:
            return
        # Breed using the first two assigned critters (deterministic for now)
        parent1, parent2 = self.assigned_critters[:2]
        offspring = self._breed(parent1, parent2)
        if offspring:
            # Add offspring to the world; we need a reference to the world.
            # The player has a reference to world in typical usage.
            # However, interact signature in other buildings doesn't pass world.
            # In main.py, Player.interact calls obj.interact(self), and obj can access player.world?
            # Let's check: Player has a reference to world? Not currently. We'll need to adjust.
            # For now, assume the world is globally accessible or we pass via building later.
            # But to keep consistency with other buildings (GatheringHut.interact takes other and updates inventory),
            # we might need to handle differently. The design is not yet finalized.
            # For testability, I'll implement _breed to return offspring and let caller add to world.
            # The interact method currently cannot add to world because it lacks world reference.
            # I could store world reference in the building when placed? That would be a good design.
            # Building class currently doesn't store world. I could modify Building to accept world reference on placement.
            # But that might be bigger change than needed.
            # Alternatively, I could have breed method just create offspring and not add to world; the caller (main) adds it.
            # But then interact shouldn't handle adding. I'll separate: breed(parent1, parent2) returns offspring, and interact does not add.
            # Then in main, when player interacts with MatingHut, we call breed and then add offspring to world.
            # That would require changes in main.py.
            # Since we're early in implementation, I'll have breed just compute and return offspring; interact does nothing besides maybe a sound later.
            # For now, interact will do nothing; the breeding will be triggered via main.update maybe?
            # But the task says "Implement MatingHut.breed() method", not necessarily interact.
            # I'll implement breed as a method that creates offspring and returns it. The main loop or another system will call it.
            # So interact can remain unimplemented for now, or could call breed and then we need world.
            pass

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
