"""
MultiSelectInspector: UI for managing groups of selected critters.
"""
import pygame
from critter import CritterState

class MultiSelectInspector:
    """Displays aggregated stats and mass actions for multiple selected critters."""
    def __init__(self, cell_size, font, screen_width, screen_height):
        self.cell_size = cell_size
        self.font = font
        self.visible = False
        self.selected_critters = []
        
        # Panel dimensions (same as CritterInspector for consistency)
        self.panel_width = 220
        self.panel_height = 300
        self.panel_margin = 10
        self.reposition(screen_width, screen_height)
        
        # Button rects
        self.follow_all_button_rect = None
        self.release_all_button_rect = None

    def reposition(self, screen_width, screen_height):
        """Update panel position to stay anchored to the top-right corner."""
        self.panel_rect = pygame.Rect(
            screen_width - self.panel_width - self.panel_margin,
            self.panel_margin,
            self.panel_width,
            self.panel_height
        )
        self.close_button_size = 20
        self.close_button_rect = pygame.Rect(
            self.panel_rect.right - self.close_button_size - 5,
            self.panel_rect.top + 5,
            self.close_button_size,
            self.close_button_size
        )

    def toggle(self, critters=None):
        """Toggle visibility. If critters list provided, show their stats."""
        if critters:
            self.selected_critters = critters
            self.visible = True
        else:
            self.visible = not self.visible

    def hide(self):
        self.visible = False
        self.selected_critters = []

    def handle_mouse_click(self, pos, player=None, world=None):
        """Handle clicks on the multi-select panel."""
        if not self.visible:
            return False
        
        if self.panel_rect.collidepoint(pos):
            if self.close_button_rect.collidepoint(pos):
                self.hide()
            elif self.follow_all_button_rect and self.follow_all_button_rect.collidepoint(pos):
                if player and world:
                    self.mass_follow(player, world)
            return True
        return False

    def mass_follow(self, player, world):
        """Make all selected critters follow the player."""
        for c in self.selected_critters:
            if c.state != CritterState.FOLLOW:
                c.start_follow(player)
        world.set_message("Group follow command issued.", 2.0)

    def draw(self, screen):
        if not self.visible or not self.selected_critters:
            return
        
        # Draw background
        pygame.draw.rect(screen, (240, 240, 240), self.panel_rect)
        pygame.draw.rect(screen, (0, 0, 0), self.panel_rect, 2)
        
        # Draw close button
        pygame.draw.rect(screen, (200, 200, 200), self.close_button_rect)
        pygame.draw.rect(screen, (100, 100, 100), self.close_button_rect, 1)
        x, y, s = self.close_button_rect.x, self.close_button_rect.y, self.close_button_size
        pygame.draw.line(screen, (0, 0, 0), (x+4, y+4), (x+s-4, y+s-4), 2)
        pygame.draw.line(screen, (0, 0, 0), (x+s-4, y+4), (x+4, y+s-4), 2)

        # Header
        x0 = self.panel_rect.x + 10
        y0 = self.panel_rect.y + 10
        line_spacing = self.font.get_linesize()
        
        count_text = self.font.render(f"Selected: {len(self.selected_critters)}", True, (0, 0, 0))
        screen.blit(count_text, (x0, y0))
        y_curr = y0 + line_spacing * 2

        # Averages
        if self.selected_critters:
            avg_str = sum(c.strength for c in self.selected_critters) / len(self.selected_critters)
            avg_spd = sum(c.speed_stat for c in self.selected_critters) / len(self.selected_critters)
            avg_end = sum(c.endurance for c in self.selected_critters) / len(self.selected_critters)
            avg_total = avg_str + avg_spd + avg_end

            stats = [
                ("Avg Strength", avg_str, (200, 50, 50)),
                ("Avg Speed", avg_spd, (50, 150, 50)),
                ("Avg Endurance", avg_end, (50, 50, 200)),
                ("Avg Total", avg_total, (0, 0, 0))
            ]

            for label, val, color in stats:
                text = self.font.render(f"{label}: {val:.1f}", True, color)
                screen.blit(text, (x0, y_curr))
                y_curr += line_spacing

        # Mass Actions
        y_curr += 10
        btn_text = "All Follow"
        surf = self.font.render(btn_text, True, (255, 255, 255))
        rect = pygame.Rect(x0, y_curr, surf.get_width() + 16, line_spacing + 6)
        self.follow_all_button_rect = rect
        pygame.draw.rect(screen, (100, 100, 200), rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 1)
        screen.blit(surf, (rect.centerx - surf.get_width() // 2, rect.centery - surf.get_height() // 2))
