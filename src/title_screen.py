"""
Title screen for Critters game.

Provides a simple menu with New Game and Continue options, plus confirmation for overwrite.
"""
import pygame
from pathlib import Path


class TitleScreen:
    """Manage title screen state, rendering, and input."""
    def __init__(self, screen_width, screen_height, save_path="saves/save.json"):
        self.width = screen_width
        self.height = screen_height
        self.save_path = Path(save_path)
        self.state = "menu"  # "menu" or "confirm_new"
        self.selected_action = None  # "new_game", "continue", "quit"

        # Colors
        self.bg_color = (200, 200, 200)  # Light gray, matches game background
        self.text_color = (0, 0, 0)
        self.button_color = (100, 100, 200)
        self.button_hover_color = (120, 120, 220)
        self.confirm_overlay_color = (0, 0, 0, 180)

        self._init_fonts()
        self._compute_rects()

    def _init_fonts(self):
        pygame.font.init()
        self.title_font = pygame.font.SysFont(None, 72)
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)

    def _compute_rects(self):
        # Precompute button positions
        cx = self.width // 2
        cy = self.height // 2
        self.new_game_rect = pygame.Rect(cx - 100, cy, 200, 50)
        self.continue_rect = pygame.Rect(cx - 100, cy + 70, 200, 50) if self.check_save_exists() else None
        # Confirmation dialog
        self.confirm_box_rect = pygame.Rect(cx - 200, cy - 80, 400, 160)
        self.yes_rect = pygame.Rect(cx - 150, cy + 40, 120, 40)
        self.no_rect = pygame.Rect(cx + 30, cy + 40, 120, 40)

    def check_save_exists(self):
        return self.save_path.exists()

    def handle_event(self, event):
        if self.state == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if self.new_game_rect.collidepoint(mx, my):
                    if self.check_save_exists():
                        self.state = "confirm_new"
                    else:
                        self.selected_action = "new_game"
                if self.continue_rect and self.continue_rect.collidepoint(mx, my):
                    self.selected_action = "continue"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    if self.check_save_exists():
                        self.state = "confirm_new"
                    else:
                        self.selected_action = "new_game"
                if event.key == pygame.K_c and self.check_save_exists():
                    self.selected_action = "continue"
                if event.key == pygame.K_ESCAPE:
                    self.selected_action = "quit"
        elif self.state == "confirm_new":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if self.yes_rect.collidepoint(mx, my):
                    self.selected_action = "new_game"
                elif self.no_rect.collidepoint(mx, my):
                    self.state = "menu"
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_y, pygame.K_RETURN, pygame.K_SPACE):
                    self.selected_action = "new_game"
                if event.key in (pygame.K_n, pygame.K_ESCAPE):
                    self.state = "menu"

    def update(self, dt):
        pass  # No dynamic updates needed

    def render(self, screen):
        screen.fill(self.bg_color)
        # Title
        title_surf = self.title_font.render("CRITTERS", True, self.text_color)
        title_rect = title_surf.get_rect(center=(self.width // 2, self.height // 3))
        screen.blit(title_surf, title_rect)

        if self.state == "menu":
            # New Game button
            pygame.draw.rect(screen, self.button_color, self.new_game_rect)
            new_text = self.font.render("New Game", True, (255, 255, 255))
            screen.blit(new_text, new_text.get_rect(center=self.new_game_rect.center))
            # Continue button (only if save exists)
            if self.continue_rect:
                pygame.draw.rect(screen, self.button_color, self.continue_rect)
                cont_text = self.font.render("Continue", True, (255, 255, 255))
                screen.blit(cont_text, cont_text.get_rect(center=self.continue_rect.center))
            # Instructions
            instr = self.small_font.render("N: New, C: Continue, Esc: Quit", True, self.text_color)
            screen.blit(instr, instr.get_rect(center=(self.width // 2, self.height - 50)))
        elif self.state == "confirm_new":
            # Dark overlay
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill(self.confirm_overlay_color)
            screen.blit(overlay, (0, 0))
            # Confirmation box
            pygame.draw.rect(screen, (255, 255, 255), self.confirm_box_rect)
            pygame.draw.rect(screen, (0, 0, 0), self.confirm_box_rect, 2)
            msg1 = self.font.render("New Game will overwrite the saved game.", True, self.text_color)
            msg2 = self.font.render("Proceed?", True, self.text_color)
            screen.blit(msg1, msg1.get_rect(center=(self.width // 2, self.height // 2 - 30)))
            screen.blit(msg2, msg2.get_rect(center=(self.width // 2, self.height // 2 + 10)))
            # Yes/No buttons
            pygame.draw.rect(screen, (200, 50, 50), self.yes_rect)
            pygame.draw.rect(screen, self.button_color, self.no_rect)
            yes_text = self.font.render("Yes", True, (255, 255, 255))
            no_text = self.font.render("No", True, (255, 255, 255))
            screen.blit(yes_text, yes_text.get_rect(center=self.yes_rect.center))
            screen.blit(no_text, no_text.get_rect(center=self.no_rect.center))
