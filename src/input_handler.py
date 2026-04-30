"""
Input handling for player movement, debug toggle, interaction, and building.
"""
import pygame

# Delay (seconds) before hold-to-interact auto-repeat kicks in
HOLD_INTERACT_DELAY = 0.5
# Base interval (seconds) between auto-repeat interactions while E is held
BASE_AUTO_INTERACT_INTERVAL = 0.5  # 2 interactions per second


class InputHandler:
    """Processes keyboard input for movement, debug toggle, interaction, and building."""
    def __init__(self):
        self.move_x = 0
        self.move_y = 0
        self.show_debug = False
        self.interact_held = False # True if E or Space is held
        self.build_toggle = False
        self.select_gathering_hut = False
        self.crafting_toggle = False
        self.craft_slot = None
        self.mouse_clicked = False
        self.mouse_right_clicked = False
        self.mouse_pos = (0, 0)
        self.save_request = False
        self.load_request = False
        self.deconstruct_mode = False
        self.escape_pressed = False  # Escape key to close overlays
        self.f_pressed = False  # F key for critter follow toggle

    def handle_events(self):
        """Process pygame events. Returns False if the app should quit."""
        self.build_toggle = False
        self.select_gathering_hut = False
        self.mouse_clicked = False
        self.mouse_right_clicked = False
        self.save_request = False
        self.load_request = False
        self.escape_pressed = False
        self.f_pressed = False
        
        # We check held state using key.get_pressed() in update_movement or here
        # but for individual presses we use the event queue.
        # For 'held' status of interaction, let's use the event queue to toggle a flag.
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F3:
                    self.show_debug = not self.show_debug
                if event.key == pygame.K_f:
                    self.f_pressed = True
                if event.key in (pygame.K_e, pygame.K_SPACE):
                    self.interact_held = True
                if event.key == pygame.K_b:
                    self.build_toggle = True
                    # Exiting deconstruct mode if build mode is toggled
                    if self.deconstruct_mode:
                        self.deconstruct_mode = False
                if event.key == pygame.K_g:
                    self.select_gathering_hut = True
                if event.key == pygame.K_r:
                    self.crafting_toggle = True
                if event.key == pygame.K_x:
                    self.deconstruct_mode = not self.deconstruct_mode
                    # Exiting build mode if deconstruct mode is toggled on
                    if self.deconstruct_mode and self.build_toggle:
                        self.build_toggle = False
                if event.key == pygame.K_F5:
                    self.save_request = True
                if event.key == pygame.K_F6:
                    self.load_request = True
                if event.key == pygame.K_ESCAPE:
                    self.escape_pressed = True
                # Number keys 1-9 for crafting selection
                number_keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
                               pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]
                if event.key in number_keys:
                    self.craft_slot = number_keys.index(event.key) + 1  # 1-indexed
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_e, pygame.K_SPACE):
                    # Only release if BOTH are up? 
                    # Simpler: just check if the released key was one of them.
                    # If user holds both and releases one, it stops. That's fine.
                    self.interact_held = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.mouse_clicked = True
                    self.mouse_pos = event.pos
                if event.button == 3:  # Right click
                    self.mouse_right_clicked = True
                    self.mouse_pos = event.pos
        return True

    def update(self, dt, auto_interact_multiplier=1.0):
        """
        InputHandler.update is now a no-op for interaction as it's handled in the main loop/Player.
        """
        pass

    def update_movement(self):
        """Update movement vector based on current key states (WASD)."""
        keys = pygame.key.get_pressed()
        self.move_x = 0
        self.move_y = 0
        if keys[pygame.K_w]:
            self.move_y -= 1
        if keys[pygame.K_s]:
            self.move_y += 1
        if keys[pygame.K_a]:
            self.move_x -= 1
        if keys[pygame.K_d]:
            self.move_x += 1
