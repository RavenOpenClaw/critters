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

    def draw(self, screen):
        if not self.visible or self.selected_critter is None:
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
        # Render lines
        x0 = self.panel_rect.x + 10
        y0 = self.panel_rect.y + 10
        line_spacing = self.font.get_linesize()
        for i, line in enumerate(lines):
            text = self.font.render(line, True, (0, 0, 0))
            screen.blit(text, (x0, y0 + i * line_spacing))
