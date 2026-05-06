"""
MatingHutInspector: UI for displaying parent stats and breeding comparisons.
"""
import pygame

class MatingHutInspector:
    """Displays a two-column comparison of assigned parent stats and their averages."""
    def __init__(self, x, y, width, height, font):
        self.font = font
        self.width = width
        self.height = height
        self.panel_margin = x # Use initial x as margin
        self.visible = False
        self.selected_hut = None
        self.reposition(800, 600) # Default setup

    def reposition(self, screen_width, screen_height):
        """Update panel position. Anchored to top-left with fixed margin."""
        self.panel_rect = pygame.Rect(self.panel_margin, self.panel_margin, self.width, self.height)
        self.close_button_size = 20
        self.close_button_rect = pygame.Rect(
            self.panel_rect.right - self.close_button_size - 5,
            self.panel_rect.top + 5,
            self.close_button_size,
            self.close_button_size
        )

    def toggle(self, hut=None):
        """Toggle visibility. If a hut is provided, show that hut's assigned critters."""
        if hut is not None:
            self.selected_hut = hut
            self.visible = True
        else:
            self.visible = not self.visible

    def hide(self):
        self.visible = False
        self.selected_hut = None

    def handle_mouse_click(self, pos):
        """Consume clicks within the panel. Hide if close button clicked."""
        if not self.visible:
            return False
        if self.panel_rect.collidepoint(pos):
            if self.close_button_rect.collidepoint(pos):
                self.hide()
            return True
        return False

    def draw(self, screen):
        if not self.visible or self.selected_hut is None:
            return
        
        # Background
        pygame.draw.rect(screen, (245, 230, 245), self.panel_rect) # Light lavender/pink
        pygame.draw.rect(screen, (0, 0, 0), self.panel_rect, 2)
        
        # Close button
        pygame.draw.rect(screen, (200, 200, 200), self.close_button_rect)
        pygame.draw.rect(screen, (100, 100, 100), self.close_button_rect, 1)
        x, y, s = self.close_button_rect.x, self.close_button_rect.y, self.close_button_size
        pygame.draw.line(screen, (0, 0, 0), (x+4, y+4), (x+s-4, y+s-4), 2)
        pygame.draw.line(screen, (0, 0, 0), (x+s-4, y+4), (x+4, y+s-4), 2)

        # Title
        title = self.font.render("Breeding Comparison", True, (0, 0, 0))
        screen.blit(title, (self.panel_rect.x + 10, self.panel_rect.y + 10))

        hut = self.selected_hut
        parents = hut.assigned_critters
        
        # Column setup
        col1_x = self.panel_rect.x + 20
        col2_x = self.panel_rect.x + (self.panel_rect.width // 2) + 10
        y_start = self.panel_rect.y + 60 # Increased from 45 to avoid title overlap
        line_spacing = self.font.get_linesize() + 4

        labels = ["Strength", "Speed", "Endurance", "Total"]
        colors = [(200, 50, 50), (50, 150, 50), (50, 50, 200), (0, 0, 0)]

        # Header for columns
        h1 = self.font.render("Parent A", True, (80, 80, 80))
        h2 = self.font.render("Parent B", True, (80, 80, 80))
        screen.blit(h1, (col1_x, y_start - 25))
        screen.blit(h2, (col2_x, y_start - 25))

        for i in range(2):
            curr_x = col1_x if i == 0 else col2_x
            if i < len(parents):
                p = parents[i]
                stats = [p.strength, p.speed_stat, p.endurance, (p.strength + p.speed_stat + p.endurance)]
                for j, (label, val, color) in enumerate(zip(labels, stats, colors)):
                    text = self.font.render(f"{label}: {val}", True, color)
                    screen.blit(text, (curr_x, y_start + j * line_spacing))
            else:
                empty_text = self.font.render("(empty)", True, (150, 150, 150))
                screen.blit(empty_text, (curr_x, y_start))

        # Averages Row
        if len(parents) == 2:
            p1, p2 = parents[0], parents[1]
            avg_y = y_start + len(labels) * line_spacing + 15
            pygame.draw.line(screen, (0, 0, 0), (self.panel_rect.x + 10, avg_y - 5), 
                             (self.panel_rect.x + self.panel_rect.width - 10, avg_y - 5), 1)
            
            avg_title = self.font.render("Offspring Averages:", True, (0, 0, 0))
            screen.blit(avg_title, (self.panel_rect.x + 20, avg_y))
            
            avgs = [
                (p1.strength + p2.strength) / 2,
                (p1.speed_stat + p2.speed_stat) / 2,
                (p1.endurance + p2.endurance) / 2,
                ((p1.strength + p2.strength) / 2 + (p1.speed_stat + p2.speed_stat) / 2 + (p1.endurance + p2.endurance) / 2)
            ]
            
            for j, (label, val, color) in enumerate(zip(labels, avgs, colors)):
                avg_text = self.font.render(f"Avg {label}: {val:.1f}", True, color)
                screen.blit(avg_text, (self.panel_rect.x + 20, avg_y + 25 + j * line_spacing))
        elif len(parents) < 2:
            avg_y = y_start + len(labels) * line_spacing + 15
            missing_text = self.font.render("Assign 2 critters to see averages", True, (100, 100, 100))
            screen.blit(missing_text, (self.panel_rect.x + 20, avg_y))
