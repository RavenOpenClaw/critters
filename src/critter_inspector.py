"""
Critter Inspector UI: displays stats of a selected critter.
"""
import pygame
from critter import Critter

class CritterInspector:
    """Shows detailed stats for a selected critter in a fixed side panel."""
    def __init__(self, cell_size, font, screen_width, screen_height):
        self.cell_size = cell_size
        self.font = font
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.visible = False
        self.selected_critter = None
        # Panel dimensions
        self.panel_width = 220
        self.panel_height = 320
        self.panel_margin = 10
        # Position: top-right corner
        self.panel_rect = pygame.Rect(
            screen_width - self.panel_width - self.panel_margin,
            self.panel_margin,
            self.panel_width,
            self.panel_height
        )
        # Close button rect (small X at top-right of panel)
        self.close_button_size = 20
        self.close_button_rect = pygame.Rect(
            self.panel_rect.right - self.close_button_size - 5,
            self.panel_rect.top + 5,
            self.close_button_size,
            self.close_button_size
        )

    def toggle(self, critter=None):
        """Toggle visibility. If a critter is provided, show that critter's stats."""
        if critter is not None:
            self.selected_critter = critter
            self.visible = True
        else:
            self.visible = not self.visible

    def hide(self):
        self.visible = False
        self.selected_critter = None

    def handle_mouse_click(self, pos):
        """Check if click is within the inspector panel; consume it. If on close button, hide panel.
        Returns True if click was consumed (panel visible and click inside panel), False otherwise."""
        if not self.visible:
            return False
        # If click inside panel rect, consume
        if self.panel_rect.collidepoint(pos):
            # If on close button, hide panel
            if self.close_button_rect.collidepoint(pos):
                self.hide()
            return True
        return False

    def handle_assign(self, player, world):
        """Assign the selected critter to the nearest hut (GatheringHut or MatingHut) within player's interaction radius.
        Shows feedback message on success or failure.
        """
        if self.selected_critter is None:
            return
        from gathering_hut import GatheringHut
        from mating_hut import MatingHut
        # Find candidate huts
        huts = [obj for obj in world.current_map.objects if isinstance(obj, (GatheringHut, MatingHut))]
        if not huts:
            world.set_message("No huts built.", 2.0)
            return
        # Find nearest hut within interaction radius
        nearest_hut = None
        min_dist_sq = float('inf')
        for hut in huts:
            hx, hy = hut.get_center()
            dx = player.x - hx
            dy = player.y - hy
            dist_sq = dx*dx + dy*dy
            if dist_sq <= player.interaction_radius**2 and dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                nearest_hut = hut
        if nearest_hut is None:
            world.set_message("No hut in range.", 2.0)
            return
        # Perform assignment (handles unassign from previous)
        nearest_hut.assign_critter(self.selected_critter)
        hut_name = type(nearest_hut).__name__
        world.set_message(f"Critter assigned to {hut_name}.", 2.0)

    def draw(self, screen):
        if not self.visible or self.selected_critter is None:
            self.assign_button_rect = None
            return
        # Draw panel background
        pygame.draw.rect(screen, (240, 240, 240), self.panel_rect)
        pygame.draw.rect(screen, (0, 0, 0), self.panel_rect, 2)
        # Draw close button (X)
        pygame.draw.rect(screen, (200, 200, 200), self.close_button_rect)
        pygame.draw.rect(screen, (100, 100, 100), self.close_button_rect, 1)
        # X lines
        x, y, s = self.close_button_rect.x, self.close_button_rect.y, self.close_button_size
        pygame.draw.line(screen, (0, 0, 0), (x+4, y+4), (x+s-4, y+s-4), 2)
        pygame.draw.line(screen, (0, 0, 0), (x+s-4, y+4), (x+4, y+s-4), 2)
        # Prepare stats text
        c = self.selected_critter
        lines = [
            f"Critter Stats",
            f"State: {c.state.name}",
            f"Strength: {c.strength}",
            f"Speed: {c.speed_stat}",
            f"Endurance: {c.endurance}",
            f"Carry Capacity: {c.carry_capacity}",
            f"Held: {c.held_resource} x{c.held_quantity}",
            f"Gather Speed: {c.get_gather_speed():.2f}/s",
            f"Move Speed: {c.get_movement_speed():.1f}",
        ]
        # Active buffs
        if c.active_buffs:
            lines.append("Buffs:")
            for b in c.active_buffs:
                lines.append(f"  {b.name} ({b.remaining:.1f}s)")
        else:
            lines.append("Buffs: None")
        # Assignment status line
        assigned_hut = getattr(c, 'assigned_hut', None)
        if assigned_hut is not None:
            hut_name = type(assigned_hut).__name__
            lines.append(f"Assigned: {hut_name}")
        else:
            lines.append("Assigned: None")
        # Render lines
        x0 = self.panel_rect.x + 10
        y0 = self.panel_rect.y + 10
        line_spacing = self.font.get_linesize()
        for i, line in enumerate(lines):
            text = self.font.render(line, True, (0, 0, 0))
            screen.blit(text, (x0, y0 + i * line_spacing))
        # Draw "Assign" button below stats
        btn_y = y0 + len(lines) * line_spacing + 8
        btn_text = "Assign to Nearest Hut"
        text_surf = self.font.render(btn_text, True, (255, 255, 255))
        text_rect = text_surf.get_rect()
        btn_rect = pygame.Rect(
            x0,
            btn_y,
            text_rect.width + 16,
            line_spacing + 6
        )
        self.assign_button_rect = btn_rect
        pygame.draw.rect(screen, (100, 100, 200), btn_rect)
        pygame.draw.rect(screen, (0, 0, 0), btn_rect, 1)
        text_rect.center = btn_rect.center
        screen.blit(text_surf, text_rect)
