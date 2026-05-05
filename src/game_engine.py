"""
GameEngine: Manages the core game lifecycle, coordinating managers and running the loop.
"""
import pygame
import sys
import math
from constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, MESSAGE_DECONSTRUCTED, MESSAGE_OUT_OF_RANGE,
    PROMPT_DIRECT_ASSIGN, DECONSTRUCTION_MODE_LABEL
)
from game_state import new_game, load_game
from input_handler import InputHandler
from build_menu import BuildMenu
from crafting_menu import CraftingMenu
from critter_inspector import CritterInspector
from ui_manager import UIManager
from camera import Camera
from pathfinding import PathfindingSystem
from building import Building
from obstacle import Obstacle

class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Critters Prototype")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        
        self.input_handler = InputHandler()
        self.camera = None
        self.pathfinding = PathfindingSystem()
        
        # Initialize UI Components (matching correct constructor signatures)
        self.build_menu = BuildMenu(24) # cell_size
        from recipes import RECIPES
        self.crafting_menu = CraftingMenu(RECIPES) # recipes list
        self.critter_inspector = CritterInspector(24, self.font, WINDOW_WIDTH, WINDOW_HEIGHT)
        
        self.ui_manager = UIManager(
            WINDOW_WIDTH, WINDOW_HEIGHT, self.font,
            self.build_menu, self.crafting_menu, self.critter_inspector
        )
        
        self.world = None
        self.player = None
        self.running = True

    def setup(self, state_tuple):
        """Inject world and player from game_state."""
        self.world, self.player = state_tuple
        self._update_camera_bounds()
        if self.camera:
            self.camera.center_on(self.player.x, self.player.y)

    def _update_camera_bounds(self):
        """Sync camera constraints with current world grid dimensions."""
        if not self.world:
            return
        grid = self.world.grid
        map_px_w = grid.width * grid.cell_size
        map_px_h = grid.height * grid.cell_size
        
        if self.camera is None:
            self.camera = Camera(WINDOW_WIDTH, WINDOW_HEIGHT, map_px_w, map_px_h)
        else:
            self.camera.map_width = map_px_w
            self.camera.map_height = map_px_h

    def run(self):
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            # Debug: print low dt warnings
            if dt > 0.5:
                print(f"Warning: large dt ({dt:.3f}s)")
            
            self._handle_input()
            self._update(dt)
            self._render()
            
        pygame.quit()
        sys.exit()

    def _handle_input(self):
        # Update movement vector from held keys (WASD)
        self.input_handler.update_movement()
        
        # Debug: print movement state if non-zero
        if self.input_handler.move_x != 0 or self.input_handler.move_y != 0:
            pass # print(f"Move input: ({self.input_handler.move_x}, {self.input_handler.move_y})")

        if not self.input_handler.handle_events():
            self.running = False
            return

        # 1. Unified UI Click Handling
        if self.input_handler.mouse_clicked:
            if self.ui_manager.handle_mouse_click(self.input_handler.mouse_pos, self.world, self.player, self.camera):
                return # UI consumed the click

            # 2. World-space clicks (if UI didn't consume)
            mx, my = self.input_handler.mouse_pos
            wx, wy = self.camera.undo(mx, my)
            gx, gy = self.world.grid.world_to_grid(wx, wy)

            # --- Target Identification ---
            
            # Check for Critter
            target_critter = None
            for c in self.world.current_map.critters:
                dx, dy = wx - c.x, wy - c.y
                if dx*dx + dy*dy <= (c.radius + 5) ** 2:
                    target_critter = c
                    break
            
            # Check for Building/Obstacle
            target_obj = self.world.grid.occupied.get((gx, gy))
            
            # --- Logic Pass ---

            # Deconstruction Mode (Priority)
            if self.input_handler.deconstruct_mode:
                if isinstance(target_obj, Building):
                    ox, oy = target_obj.get_center()
                    dx, dy = self.player.x - ox, self.player.y - oy
                    if dx*dx + dy*dy <= self.player.interaction_radius**2:
                        target_obj.deconstruct(self.world, self.player)
                        self.world.set_message(MESSAGE_DECONSTRUCTED, 2.0)
                    else:
                        self.world.set_message(MESSAGE_OUT_OF_RANGE, 1.5)
                return

            # Selection handling: don't close windows if we are picking a NEW relevant target
            is_selecting_new = False

            if target_critter:
                if self.critter_inspector.visible and self.critter_inspector.selected_critter is target_critter:
                    self.critter_inspector.hide()
                else:
                    self.critter_inspector.toggle(target_critter)
                is_selecting_new = True
            
            elif self.build_menu.visible and self.build_menu.selected_building_class:
                if self.world.grid.is_within_bounds(gx, gy):
                    self.build_menu.attempt_placement(self.player, self.world, self.world.grid, gx, gy)
                    is_selecting_new = True # Consider placement an 'interactive' action

            elif target_obj:
                from mating_hut import MatingHut
                if isinstance(target_obj, MatingHut):
                    self.ui_manager.mating_hut_inspector.toggle(target_obj)
                    is_selecting_new = True
                # Add other assignable/inspectable buildings here if needed
            
            # Global Close: Only if we didn't click a UI element AND didn't select a new interactive target
            if not is_selecting_new:
                self.critter_inspector.hide()
                self.mating_hut_inspector.hide()

        # 3. Right-click Assignment
        if self.input_handler.mouse_right_clicked:
            if self.critter_inspector.visible and self.critter_inspector.selected_critter:
                mx, my = self.input_handler.mouse_pos
                wx, wy = self.camera.undo(mx, my)
                gx, gy = self.world.grid.world_to_grid(wx, wy)
                if (gx, gy) in self.world.grid.occupied:
                    obj = self.world.grid.occupied[(gx, gy)]
                    if isinstance(obj, (Building, Obstacle)) and hasattr(obj, 'assign_critter'):
                        obj.assign_critter(self.critter_inspector.selected_critter)
                        self.world.set_message(f"Critter assigned to {type(obj).__name__}", 2.0)

        # 4. Keyboard Shortcuts
        if self.input_handler.escape_pressed:
            self._close_all_menus()
        
        if self.input_handler.save_request:
            from save_system import save_game
            try:
                save_game(self.world, self.player, "saves/save.json")
                self.world.set_message("Game Saved!", 2.0)
            except Exception as e:
                self.world.set_message(f"Save Failed: {e}", 3.0)
        
        if self.input_handler.build_toggle:
            self.build_menu.toggle()
            if self.build_menu.visible:
                self.crafting_menu.visible = False
        
        if self.input_handler.crafting_toggle:
            self.crafting_menu.toggle()
            if self.crafting_menu.visible:
                self.build_menu.visible = False

        if self.input_handler.f_pressed:
            if self.critter_inspector.visible and self.critter_inspector.selected_critter:
                self.critter_inspector.toggle_follow(self.player, self.world)
                self.critter_inspector.hide()

        # 5. Crafting
        if self.crafting_menu.visible and self.input_handler.craft_slot is not None:
            idx = self.input_handler.craft_slot - 1
            if 0 <= idx < len(self.crafting_menu.recipes):
                self.crafting_menu.craft_selected(self.player, self.crafting_menu.recipes[idx])
            self.input_handler.craft_slot = None

    def _update(self, dt):
        self.player.update(dt)
        # Debug: log player state
        # print(f"Player: ({self.player.x:.1f}, {self.player.y:.1f}) Speed: {self.player.speed:.1f}")
        
        # Campfire Aura
        self.world.apply_campfire_aura(self.player)
        
        self.player.move(self.input_handler.move_x, self.input_handler.move_y, dt, grid=self.world.grid)
        self.player.update_interaction(dt, self.world, self.input_handler.interact_held)
        
        # Player Trampling
        pgx, pgy = self.world.grid.world_to_grid(self.player.x, self.player.y)
        if (pgx, pgy) != self.player.last_trampled_cell:
            self.world.mark_trampled(pgx, pgy)
            self.player.last_trampled_cell = (pgx, pgy)

        # Map Transitions (Transport player if they move off-screen)
        if self.world.handle_map_transition(self.player):
            self._update_camera_bounds()

        self.camera.update(self.player.x, self.player.y)
        
        # Centralized World Update (includes critters, resources, trample decay, etc.)
        self.world.update(dt, self.pathfinding)
        
        # Critter Trampling
        for c in self.world.current_map.critters:
            cgx, cgy = self.world.grid.world_to_grid(c.x, c.y)
            if (cgx, cgy) != c.last_trampled_cell:
                self.world.mark_trampled(cgx, cgy)
                c.last_trampled_cell = (cgx, cgy)

        self.ui_manager.update(dt)

    def _render(self):
        self.screen.fill((200, 200, 200)) # Background
        self.world.draw(self.screen, self.camera)
        
        # Interaction Tooltips (Hover prompts)
        target_obj = self.player.get_interactable_target(self.world)
        if target_obj:
            from constants import PROMPT_ASSIGN
            if hasattr(target_obj, 'get_center'):
                ox, oy = target_obj.get_center()
            else:
                ox, oy = target_obj.x, target_obj.y
            
            text = None
            if isinstance(target_obj, (Building, Obstacle)) and self.player.following_critters:
                text = PROMPT_ASSIGN
            elif hasattr(target_obj, 'get_interaction_text'):
                text = target_obj.get_interaction_text()
            
            if text:
                text_surface = self.font.render(text, True, (0, 0, 0))
                sox, soy = self.camera.apply(ox, oy)
                text_rect = text_surface.get_rect(center=(sox, soy - 30))
                self.screen.blit(text_surface, text_rect)

        # Player render
        spx, spy = self.camera.apply(self.player.x, self.player.y)
        pygame.draw.circle(self.screen, (0, 0, 255), (int(spx), int(spy)), int(self.player.radius))

        # HUD and UI
        self.ui_manager.draw(self.screen, self.world, self.player, self.camera)
        
        # World Message
        if self.world.message:
            msg_surf = self.font.render(self.world.message, True, (0, 0, 0))
            self.screen.blit(msg_surf, (WINDOW_WIDTH//2 - msg_surf.get_width()//2, 50))

        # Modes
        if self.input_handler.deconstruct_mode:
            decon_surf = self.font.render(DECONSTRUCTION_MODE_LABEL, True, (255, 0, 0))
            self.screen.blit(decon_surf, (WINDOW_WIDTH - decon_surf.get_width() - 10, WINDOW_HEIGHT - 30))

        pygame.display.flip()

    def _close_all_menus(self):
        self.build_menu.visible = False
        self.crafting_menu.visible = False
        self.critter_inspector.hide()
        self.input_handler.deconstruct_mode = False
