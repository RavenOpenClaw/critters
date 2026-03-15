"""
Critters Game Prototype - Core game loop and rendering.

This module initializes Pygame, creates the game window, and runs the main loop.
"""

import pygame
import sys

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BACKGROUND_COLOR = (200, 200, 200)  # Light gray
TARGET_FPS = 60

def main():
    """Initialize Pygame and run the main game loop."""
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Critters Prototype")
    clock = pygame.time.Clock()

    running = True
    while running:
        # Calculate delta time (seconds since last frame)
        dt = clock.tick(TARGET_FPS) / 1000.0

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Rendering
        screen.fill(BACKGROUND_COLOR)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
