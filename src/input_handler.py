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
        self.interact = False  # Interaction flag set on 'E' key press (tap)
        self.interact_count = 0  # Number of interactions to fire this frame
        self.build_toggle = False  # Toggle build menu on 'B' key press
        self.select_gathering_hut = False  # Select GatheringHut on 'G' key press
        self.crafting_toggle = False  # Toggle crafting menu on 'R' key press
        self.craft_slot = None  # Selected recipe slot (1-9) when crafting menu is open
        self.mouse_clicked = False
        self.mouse_pos = (0, 0)
        self.save_request = False  # Save game on 'S' key press
        self.load_request = False  # Load game on 'L' key press

        # Hold-to-interact state
        self._e_held = False          # Is E currently held down?
        self._hold_timer = 0.0        # Time E has been held since first press
        self._auto_timer = 0.0        # Accumulator for auto-repeat interval

    def handle_events(self):
        """Process pygame events. Returns False if the app should quit."""
        self.build_toggle = False
        self.select_gathering_hut = False
        self.mouse_clicked = False
        self.interact = False
        self.save_request = False
        self.load_request = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F3:
                    self.show_debug = not self.show_debug
                if event.key == pygame.K_e:
                    self.interact = True
                    self._e_held = True
                    self._hold_timer = 0.0
                    self._auto_timer = 0.0
                if event.key == pygame.K_b:
                    self.build_toggle = True
                if event.key == pygame.K_g:
                    self.select_gathering_hut = True
                if event.key == pygame.K_r:
                    self.crafting_toggle = True
                if event.key == pygame.K_s:
                    self.save_request = True
                if event.key == pygame.K_l:
                    self.load_request = True
                # Number keys 1-9 for crafting selection
                number_keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
                               pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]
                if event.key in number_keys:
                    self.craft_slot = number_keys.index(event.key) + 1  # 1-indexed
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_e:
                    self._e_held = False
                    self._hold_timer = 0.0
                    self._auto_timer = 0.0
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.mouse_clicked = True
                    self.mouse_pos = event.pos
        return True

    def update(self, dt, auto_interact_multiplier=1.0):
        """
        Update hold-to-interact timers and populate interact_count.

        Args:
            dt: Delta time in seconds since last frame.
            auto_interact_multiplier: Multiplier applied to the base interval.
                Values < 1.0 speed up auto-interact (e.g. 0.5 = twice as fast).
        """
        self.interact_count = 1 if self.interact else 0

        if self._e_held:
            prev_hold = self._hold_timer
            self._hold_timer += dt

            if self._hold_timer >= HOLD_INTERACT_DELAY:
                interval = BASE_AUTO_INTERACT_INTERVAL * auto_interact_multiplier
                # Only count time that has elapsed after the delay threshold
                time_before = max(0.0, HOLD_INTERACT_DELAY - prev_hold)
                auto_dt = dt - time_before
                # Pre-load _auto_timer to interval on the first frame past the delay,
                # so the first auto-fire triggers immediately when the delay expires.
                if prev_hold < HOLD_INTERACT_DELAY:
                    self._auto_timer = interval
                self._auto_timer += auto_dt
                while self._auto_timer >= interval:
                    self._auto_timer -= interval
                    self.interact_count += 1

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
