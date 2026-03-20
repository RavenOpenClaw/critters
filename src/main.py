"""
Critters Game Prototype - Core game loop and rendering.

This module initializes Pygame, creates the game window, and runs the main loop.
"""

import pygame
import sys
from entity import Player
from input_handler import InputHandler
from grid_system import GridSystem
from world import World
from berry_bush import BerryBush

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BACKGROUND_COLOR = (200, 200, 200)  # Light gray
TARGET_FPS = 60

def main():
    """Initialize Pygame and run the main game loop."""
    pygame.init()
    pygame.font.init()  # Ensure font module is initialized
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Critters Prototype")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    # Grid and world setup
    cell_size = 32
    grid = GridSystem(cell_size=cell_size)
    world = World(grid)
    # Add a test berry bush at grid position (5, 5)
    bush = BerryBush(5, 5, cell_size=cell_size, berries=5)
    world.add_object(bush)

    # Create input handler and player
    input_handler = InputHandler()
    player = Player(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, radius=20, speed=200)
    # Set world bounds for player
    player.world_rect = screen.get_rect()

    running = True
    while running:
        # Calculate delta time (seconds since last frame)
        dt = clock.tick(TARGET_FPS) / 1000.0

        # Input handling
        if not input_handler.handle_events():
            running = False
        input_handler.update_movement()

        # Player movement (with collision detection)
        player.move(input_handler.move_x, input_handler.move_y, dt, grid=grid)

        # Player interaction
        if input_handler.interact:
            player.interact(world)
            input_handler.interact = False  # Consume the flag

        # Rendering
        screen.fill(BACKGROUND_COLOR)

        # Draw world objects
        world.draw(screen)

        # Draw player as a blue circle
        pygame.draw.circle(
            screen,
            (0, 0, 255),  # Blue
            (int(player.x), int(player.y)),
            player.radius
        )

        # Debug display (F3 toggle)
        if input_handler.show_debug:
            fps_surface = font.render(f"FPS: {clock.get_fps():.1f}", True, (0, 0, 0))
            pos_surface = font.render(f"Player: ({int(player.x)}, {int(player.y)})", True, (0, 0, 0))
            screen.blit(fps_surface, (10, 10))
            screen.blit(pos_surface, (10, 40))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
