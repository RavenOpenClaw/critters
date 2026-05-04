"""
Obstacle: A world object that blocks movement until cleared by work.
"""
import pygame
from world_object import WorldObject

class Obstacle(WorldObject):
    def __init__(self, gx, gy, width, height, cell_size, work_units=10, min_strength=0):
        super().__init__(gx, gy, width=width, height=height, cell_size=cell_size, inventory=None)
        self.work_units = work_units
        self.max_work_units = work_units
        self.min_strength = min_strength
        self.assigned_critters = []

    def assign_critter(self, critter):
        """Assign a critter to this obstacle.

        If the critter is already assigned to another hut/obstacle, unassign it first.
        If the critter is already assigned to this obstacle, ensure it stops following and works.
        """
        # Always stop following when assigned/re-assigned
        critter.stop_follow()

        # If already assigned to this obstacle, ensure state is correct and return
        if critter in self.assigned_critters:
            if not critter.gathering or critter.target_resource != self:
                critter.start_gather(self)
            return

        # Unassign from previous hut/obstacle if needed
        if critter.assigned_hut is not None and critter.assigned_hut is not self:
            critter.assigned_hut.unassign_critter(critter)
            
        self.assigned_critters.append(critter)
        critter.assigned_hut = self
        critter.start_gather(self) # Start working immediately

    def unassign_critter(self, critter):
        """Remove a critter from this obstacle's assignment and clear its assigned_hut reference."""
        if critter in self.assigned_critters:
            self.assigned_critters.remove(critter)
            if getattr(critter, 'assigned_hut', None) is self:
                critter.assigned_hut = None

    def get_collective_strength(self):
        """Sum the effective strength of all assigned critters."""
        total = 0
        for critter in self.assigned_critters:
            total += critter._effective_stat(critter.strength)
        return total

    def render(self, screen, camera=None):
        # Draw a dark gray rectangle
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
        pygame.draw.rect(screen, (80, 80, 80), rect)
        
        # Show work units remaining as a progress bar
        bar_width = self.width * self.cell_size - 10
        bar_height = 5
        fill_width = (self.work_units / self.max_work_units) * bar_width
        
        # Background bar (darker)
        pygame.draw.rect(screen, (40, 40, 40), (draw_x + 5, draw_y + 5, bar_width, bar_height))
        # Fill bar (orange-ish for work)
        pygame.draw.rect(screen, (255, 165, 0), (draw_x + 5, draw_y + 5, fill_width, bar_height))

        # Show min strength requirement if present
        font = pygame.font.SysFont(None, 18)
        if self.min_strength > 0:
            current_str = self.get_collective_strength()
            color = (100, 255, 100) if current_str >= self.min_strength else (255, 100, 100)
            str_text = font.render(f"STR: {current_str}/{self.min_strength}", True, color)
            screen.blit(str_text, (draw_x + 5, draw_y + 15))
        
        # Show work units count
        text = font.render(f"Work: {self.work_units}", True, (255, 255, 255))
        screen.blit(text, (draw_x + 5, draw_y + 30))

    def get_interaction_text(self):
        """Work required to clear."""
        if self.work_units > 0:
            current_str = self.get_collective_strength()
            text = f"Work: {self.work_units}"
            if self.min_strength > 0:
                text += f" (STR: {current_str}/{self.min_strength})"
            return text
        return None

    def apply_work(self, amount):
        """Apply work to the obstacle, reducing work_units. Returns True if cleared."""
        self.work_units -= amount
        if self.work_units <= 0:
            self.work_units = 0
            # Unassign all critters before removal
            for critter in list(self.assigned_critters):
                self.unassign_critter(critter)
            # Auto-remove from world when cleared
            if hasattr(self, 'world') and self.world is not None:
                self.world.remove_object(self)
            return True
        return False

    def interact(self, other):
        """Handle player or critter interaction with the obstacle."""
        from entity import Player
        from critter import Critter
        
        if isinstance(other, Player):
            # If player has a following critter, assign it to this obstacle
            if other.following_critters:
                critter = other.following_critters[0]
                critter.stop_follow()
                self.assign_critter(critter)
                if hasattr(self, 'world') and self.world is not None:
                    self.world.set_message(f"Critter assigned to Obstacle", 2.0)
                return True
            return False

        if isinstance(other, Critter):
            # Task 57: Progress only if collective strength >= min_strength
            if self.get_collective_strength() < self.min_strength:
                return False
                
            # Use effective strength (consider well-fed buff)
            strength = other._effective_stat(other.strength)
            return self.apply_work(strength)
        return False
