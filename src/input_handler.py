"""
Input handling for player movement and debug toggle.
"""
import pygame

class InputHandler:
    """Processes keyboard input for movement and debug toggle."""
    def __init__(self):
        self.move_x = 0
        self.move_y = 0
        self.show_debug = False

    def handle_events(self):
        """Process pygame events. Returns False if the app should quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F3:
                    self.show_debug = not self.show_debug
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
