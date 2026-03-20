"""
Input handling for player movement, debug toggle, interaction, and building.
"""
import pygame

class InputHandler:
    """Processes keyboard input for movement, debug toggle, interaction, and building."""
    def __init__(self):
        self.move_x = 0
        self.move_y = 0
        self.show_debug = False
        self.interact = False  # Interaction flag set on 'E' key press
        self.build_toggle = False  # Toggle build menu on 'B' key press
        self.select_gathering_hut = False  # Select GatheringHut on 'G' key press
        self.mouse_clicked = False
        self.mouse_pos = (0, 0)

    def handle_events(self):
        """Process pygame events. Returns False if the app should quit."""
        self.build_toggle = False
        self.select_gathering_hut = False
        self.mouse_clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F3:
                    self.show_debug = not self.show_debug
                if event.key == pygame.K_e:
                    self.interact = True
                if event.key == pygame.K_b:
                    self.build_toggle = True
                if event.key == pygame.K_g:
                    self.select_gathering_hut = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.mouse_clicked = True
                    self.mouse_pos = event.pos
        return True

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
