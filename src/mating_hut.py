"""
MatingHut: A 2x2 building where critters can be assigned for breeding.
"""
from building import Building
from critter import Critter, CritterState
from constants import PROMPT_BREED, MSG_ASSIGN_MATING, MSG_BREED_NEED_TWO, MSG_BREED_NEED_FOOD, MSG_BREED_SUCCESS, ITEM_FOOD, ITEM_WOOD, ITEM_STONE

class MatingHut(Building):
    """Mating Hut building (2x2) for critter building."""
    cost = {ITEM_WOOD: 15, ITEM_STONE: 10}  # class attribute for UI display
    BREED_FOOD_COST = 5  # food cost per breeding

    def __init__(self, gx, gy, cell_size):
        super().__init__(gx, gy, width=2, height=2, cell_size=cell_size, cost=self.cost)
        self.assigned_critters = []

    def assign_critter(self, critter):
        """Assign a critter to this hut. Enforces a maximum of 2 critters.
        
        If the hut already has 2 critters, the earliest assigned critter is unassigned.
        If the critter is already assigned to another hut, unassign it first.
        """
        # Always stop following when assigned/re-assigned
        critter.stop_follow()

        # If already assigned to this hut, just ensure state is correct and return
        if critter in self.assigned_critters:
            if critter.state != CritterState.BREED:
                critter.start_breed()
            return

        # Enforce 2-critter limit: FIFO queue
        if len(self.assigned_critters) >= 2:
            oldest = self.assigned_critters[0]
            self.unassign_critter(oldest)
            oldest.start_rest() # Return to wandering

        # Unassign from previous hut if needed
        if critter.assigned_hut is not None and critter.assigned_hut is not self:
            critter.assigned_hut.unassign_critter(critter)
            
        self.assigned_critters.append(critter)
        critter.assigned_hut = self
        critter.start_return() # Travel back to hut first thing
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
                self.world.set_message(MSG_ASSIGN_MATING, 3.0)
            return

        # Breeding mode
        if len(self.assigned_critters) < 2:
            if hasattr(self, 'world') and self.world is not None:
                self.world.set_message(MSG_BREED_NEED_TWO, 2.0)
            return

        if not player.inventory.has(ITEM_FOOD, self.BREED_FOOD_COST):
            if hasattr(self, 'world') and self.world is not None:
                self.world.set_message(MSG_BREED_NEED_FOOD.format(self.BREED_FOOD_COST), 2.0)
            return

        player.inventory.remove(ITEM_FOOD, self.BREED_FOOD_COST)
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
        """Internal method to produce offspring using advanced genetic inheritance."""
        import random
        from constants import (
            BREED_INHERIT_A, BREED_INHERIT_B, BREED_WILDCARD,
            BREED_WILDCARD_LOG_WEIGHT, BREED_WILDCARD_UNIFORM_WEIGHT,
            BREED_WILDCARD_LOG_MU, BREED_WILDCARD_LOG_SIGMA,
            BREED_MUTATION_MIN, BREED_MUTATION_MAX
        )

        def roll_wildcard():
            """Roll a random stat base value using the wildcard distribution."""
            r_type = random.random()
            if r_type < BREED_WILDCARD_UNIFORM_WEIGHT:
                # 20% Uniform (Chaos)
                return random.randint(1, 100)
            else:
                # 80% Log-Normal (Skewed around mode)
                val = random.lognormvariate(BREED_WILDCARD_LOG_MU, BREED_WILDCARD_LOG_SIGMA)
                return max(1, min(100, int(val)))

        def determine_stat(val1, val2):
            """Determine a single stat value based on inheritance and mutation."""
            r = random.random()
            if r < BREED_INHERIT_A:
                base = val1
            elif r < BREED_INHERIT_A + BREED_INHERIT_B:
                base = val2
            else:
                base = roll_wildcard()
            
            # Apply ±10% mutation
            mutation = random.uniform(BREED_MUTATION_MIN, BREED_MUTATION_MAX)
            return max(1, min(100, int(base * mutation)))

        # Determine core stats
        strength = determine_stat(parent1.strength, parent2.strength)
        speed_stat = determine_stat(parent1.speed_stat, parent2.speed_stat)
        endurance = determine_stat(parent1.endurance, parent2.endurance)

        # Position: Find an empty adjacent cell to avoid spawning stuck inside collision
        spawn_x, spawn_y = self.x + (self.width * self.cell_size) / 2, self.y + (self.height * self.cell_size) / 2

        # Look for free adjacent cells
        grid = world.grid
        candidates = []
        for dy in range(-1, self.height + 1):
            for dx in range(-1, self.width + 1):
                # Only check perimeter
                if dx == -1 or dx == self.width or dy == -1 or dy == self.height:
                    gx, gy = self.gx + dx, self.gy + dy
                    if grid.is_within_bounds(gx, gy) and not grid.is_occupied(gx, gy):
                        candidates.append((gx, gy))

        if candidates:
            # Pick a random free neighbor
            gx, gy = random.choice(candidates)
            spawn_x = gx * self.cell_size + self.cell_size / 2
            spawn_y = gy * self.cell_size + self.cell_size / 2

        # Create offspring Critter
        offspring = Critter(spawn_x, spawn_y, cell_size=self.cell_size,
                            strength=strength, speed_stat=speed_stat, endurance=endurance)
        offspring.state = CritterState.REST
        offspring.assigned_hut = None # Start unassigned

        # Add to world
        world.add_object(offspring)

        return offspring

    def render(self, screen, camera=None):
        """Render the MatingHut as a pink rectangle."""
        import pygame
        draw_x, draw_y = self.x, self.y
        if camera:
            draw_x, draw_y = camera.apply(self.x, self.y)
            
        rect = pygame.Rect(
            draw_x,
            draw_y,
            self.width * self.cell_size,
            self.height * self.cell_size
        )
        pygame.draw.rect(screen, (255, 105, 180), rect)  # Hot pink
