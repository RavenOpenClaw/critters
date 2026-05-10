"""
UIManager: Orchestrates all UI components (HUD, Build Menu, Crafting Menu, Inspector, Mating Hut Inspector).
Handles UI-level input consumption and unified rendering.
"""
import pygame
import math
from constants import (
    HUD_BUILD_BUTTON, HUD_CRAFT_BUTTON, HUD_BUFFS_TITLE, HUD_BUFFS_NONE,
    DECONSTRUCTION_MODE_LABEL
)
from mating_hut_inspector import MatingHutInspector
from multi_select_inspector import MultiSelectInspector

class UIManager:
    def __init__(self, window_width, window_height, font, build_menu, crafting_menu, critter_inspector):
        self.font = font
        self.build_menu = build_menu
        self.crafting_menu = crafting_menu
        self.critter_inspector = critter_inspector
        self.mating_hut_inspector = MatingHutInspector(10, 10, 320, 300, self.font)
        self.multi_select_inspector = MultiSelectInspector(24, self.font, window_width, window_height)

    def _get_hud_rects(self, screen_w, screen_h):
        """Calculate HUD button rectangles based on current screen size."""
        y = screen_h - 40
        return {
            'save': pygame.Rect(10, y, 80, 30),
            'build': pygame.Rect(100, y, 80, 30),
            'craft': pygame.Rect(190, y, 80, 30)
        }

    def handle_mouse_click(self, pos, world, player, camera):
        """
        Unified UI click handling. UI elements consume clicks before they reach the world.
        Returns True if the click was consumed by a UI element.
        """
        mx, my = pos
        screen_w, screen_h = pygame.display.get_surface().get_size()
        hud_rects = self._get_hud_rects(screen_w, screen_h)

        # 1. Critter Inspector (Top Layer)
        critter_handled = False
        if self.critter_inspector.visible:
            if self.critter_inspector.handle_mouse_click(pos, player, world):
                return True
            if self.critter_inspector.panel_rect.collidepoint(pos):
                critter_handled = True

        # 2. Multi-Select Inspector
        multi_handled = False
        if self.multi_select_inspector.visible:
            if self.multi_select_inspector.handle_mouse_click(pos, player, world):
                return True
            if self.multi_select_inspector.panel_rect.collidepoint(pos):
                multi_handled = True

        # 3. Mating Hut Inspector
        mating_handled = False
        if self.mating_hut_inspector.visible:
            if self.mating_hut_inspector.handle_mouse_click(pos):
                return True
            if self.mating_hut_inspector.panel_rect.collidepoint(pos):
                mating_handled = True

        # 4. Build Menu
        if self.build_menu.visible:
            if self.build_menu.handle_mouse_click(pos):
                return True

        # 4. Crafting Menu
        if self.crafting_menu.visible:
            if self.crafting_menu.panel_rect.collidepoint(pos):
                return True

        # 5. HUD Buttons
        if hud_rects['save'].collidepoint(pos):
            from save_system import save_game
            try:
                save_game(world, player, "saves/save.json")
                world.set_message("Game Saved!", 2.0)
            except Exception as e:
                world.set_message(f"Save Failed: {e}", 3.0)
            self.build_menu.visible = False
            self.crafting_menu.visible = False
            return True

        if hud_rects['build'].collidepoint(pos):
            self.build_menu.toggle()
            if self.build_menu.visible:
                self.crafting_menu.visible = False
            return True
            
        if hud_rects['craft'].collidepoint(pos):
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
        sw, sh = screen.get_size()
        hud_rects = self._get_hud_rects(sw, sh)

        # 1. HUD Buttons
        self._draw_hud_button(screen, hud_rects['save'], "Save", (200, 200, 200))
        self._draw_hud_button(screen, hud_rects['build'], HUD_BUILD_BUTTON, (100, 100, 250))
        self._draw_hud_button(screen, hud_rects['craft'], HUD_CRAFT_BUTTON, (100, 250, 100))

        # 2. Resource List (Top Left)
        self._draw_resource_list(screen, player)

        # 3. Active Buffs (Top Right)
        self._draw_buffs(screen, player, sw)

        # 4. Interaction Progress
        if player.interaction_progress > 0 and player.active_target:
            self._draw_progress_circle(screen, player, camera)

        # 5. Modes (Deconstruction)
        
        # 6. Menus (Build / Craft / Inspector / Mating Hut)
        # Ensure menus and inspectors update their internal positioning
        if hasattr(self.build_menu, 'reposition'):
            self.build_menu.reposition(sw, sh)
        if hasattr(self.crafting_menu, 'reposition'):
            self.crafting_menu.reposition(sw, sh)
        if hasattr(self.critter_inspector, 'reposition'):
            self.critter_inspector.reposition(sw, sh)
        if hasattr(self.mating_hut_inspector, 'reposition'):
            self.mating_hut_inspector.reposition(sw, sh)
        if hasattr(self.multi_select_inspector, 'reposition'):
            self.multi_select_inspector.reposition(sw, sh)

        self.build_menu.render(screen, self.font)
        self.crafting_menu.render(screen, self.font)
        self.critter_inspector.draw(screen, player=player)
        self.mating_hut_inspector.draw(screen)
        self.multi_select_inspector.draw(screen)

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

    def _draw_buffs(self, screen, player, screen_w):
        x = screen_w - 150
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
        
        # Pygame draws arcs CCW. To make it LOOK clockwise filling from top (pi/2):
        # We start at (pi/2 - sweep) and end at pi/2.
        sweep = 2 * math.pi * player.interaction_progress
        start_angle = math.pi / 2 - sweep
        stop_angle = math.pi / 2
        
        pygame.draw.arc(screen, (0, 255, 0), rect, start_angle, stop_angle, 4)
