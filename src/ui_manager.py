"""
UIManager: Orchestrates all UI components (HUD, Build Menu, Crafting Menu, Inspector).
Handles UI-level input consumption and unified rendering.
"""
import pygame
import math
from constants import (
    HUD_BUILD_BUTTON, HUD_CRAFT_BUTTON, HUD_BUFFS_TITLE, HUD_BUFFS_NONE,
    DECONSTRUCTION_MODE_LABEL
)

class UIManager:
    def __init__(self, window_width, window_height, font, build_menu, crafting_menu, critter_inspector):
        self.width = window_width
        self.height = window_height
        self.font = font
        self.build_menu = build_menu
        self.crafting_menu = crafting_menu
        self.critter_inspector = critter_inspector
        
        # HUD Button Rects
        self.hud_save_rect = pygame.Rect(10, window_height - 40, 80, 30)
        self.hud_build_rect = pygame.Rect(100, window_height - 40, 80, 30)
        self.hud_craft_rect = pygame.Rect(190, window_height - 40, 80, 30)

    def handle_mouse_click(self, pos, world, player, camera):
        """
        Unified UI click handling. UI elements consume clicks before they reach the world.
        Returns True if the click was consumed by a UI element.
        """
        mx, my = pos

        # 1. Critter Inspector (Top Layer)
        if self.critter_inspector.visible:
            if self.critter_inspector.handle_mouse_click(pos, player, world):
                return True
            # Click outside inspector closes it
            if not self.critter_inspector.panel_rect.collidepoint(pos):
                self.critter_inspector.hide()
                return True

        # 2. Build Menu
        if self.build_menu.visible:
            if self.build_menu.handle_mouse_click(pos):
                return True

        # 3. Crafting Menu
        if self.crafting_menu.visible:
            # Crafting menu doesn't have a specific click handler yet, but we check slots in main
            # For now, let main handle slot selection but we consume the click area
            if self.crafting_menu.panel_rect.collidepoint(pos):
                return True

        # 4. HUD Buttons
        if self.hud_save_rect.collidepoint(pos):
            from save_system import save_game
            try:
                save_game(world, player, "saves/save.json")
                world.set_message("Game Saved!", 2.0)
            except Exception as e:
                world.set_message(f"Save Failed: {e}", 3.0)
            # Close other menus when saving from HUD if desired
            self.build_menu.visible = False
            self.crafting_menu.visible = False
            return True

        if self.hud_build_rect.collidepoint(pos):
            self.build_menu.toggle()
            if self.build_menu.visible:
                self.crafting_menu.visible = False
            return True
            
        if self.hud_craft_rect.collidepoint(pos):
            self.crafting_menu.toggle()
            if self.crafting_menu.visible:
                self.build_menu.visible = False
            return True

        return False

    def update(self, dt):
        """Update UI timers and animations."""
        self.crafting_menu.update(dt)

    def draw(self, screen, world, player, camera):
        """Unified rendering of all UI overlays."""
        # 1. HUD Buttons
        self._draw_hud_button(screen, self.hud_save_rect, "Save", (200, 200, 200))
        self._draw_hud_button(screen, self.hud_build_rect, HUD_BUILD_BUTTON, (100, 100, 250))
        self._draw_hud_button(screen, self.hud_craft_rect, HUD_CRAFT_BUTTON, (100, 250, 100))

        # 2. Resource List (Top Left)
        self._draw_resource_list(screen, player)

        # 3. Active Buffs (Top Right)
        self._draw_buffs(screen, player)

        # 4. Interaction Progress
        if player.interaction_progress > 0 and player.active_target:
            self._draw_progress_circle(screen, player, camera)

        # 5. Modes (Deconstruction)
        # Note: This requires access to input_handler state, handled in GameEngine rendering pass
        
        # 6. Menus (Build / Craft / Inspector)
        self.build_menu.render(screen, self.font)
        self.crafting_menu.render(screen, self.font)
        self.critter_inspector.draw(screen, player=player)

    def _draw_hud_button(self, screen, rect, text, color):
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)
        surf = self.font.render(text, True, (0, 0, 0))
        screen.blit(surf, (rect.x + (rect.width - surf.get_width()) // 2, 
                           rect.y + (rect.height - surf.get_height()) // 2))

    def _draw_resource_list(self, screen, player):
        from main import RESOURCE_COLORS
        y_offset = 10
        for item, count in player.inventory.items.items():
            color = RESOURCE_COLORS.get(item, (200, 200, 200))
            pygame.draw.rect(screen, color, (10, y_offset, 15, 15))
            text = self.font.render(f"{item}: {count}", True, (0, 0, 0))
            screen.blit(text, (30, y_offset))
            y_offset += 25

    def _draw_buffs(self, screen, player):
        x = self.width - 150
        y = 10
        title = self.font.render(HUD_BUFFS_TITLE, True, (0, 0, 0))
        screen.blit(title, (x, y))
        y += 20
        if not player.active_buffs:
            none_surface = self.font.render(HUD_BUFFS_NONE, True, (80, 80, 80))
            screen.blit(none_surface, (x, y))
        else:
            for buff in player.active_buffs:
                buff_text = f"{buff.name}: {buff.remaining:.1f}s"
                surf = self.font.render(buff_text, True, (0, 100, 0))
                screen.blit(surf, (x, y))
                y += 20

    def _draw_progress_circle(self, screen, player, camera):
        # Progress circle: fills clockwise from the top (12 o'clock)
        spx, spy = camera.apply(player.x, player.y)
        radius = player.radius + 10
        rect = pygame.Rect(int(spx - radius), int(spy - radius), int(radius * 2), int(radius * 2))
        
        # Pygame draws arcs CCW. To make it LOOK clockwise filling from top (-pi/2):
        # We start at (-pi/2 - sweep) and end at -pi/2.
        sweep = 2 * math.pi * player.interaction_progress
        start_angle = -math.pi / 2 - sweep
        stop_angle = -math.pi / 2
        
        pygame.draw.arc(screen, (0, 255, 0), rect, start_angle, stop_angle, 4)
