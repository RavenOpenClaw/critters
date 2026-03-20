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
from build_menu import BuildMenu

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
    # Add test berry bushes at various positions for collision and interaction testing
    test_positions = [(5, 5), (10, 5), (5, 10), (15, 5), (5, 15), (12, 12), (8, 14), (3, 8), (18, 7)]
    for gx, gy in test_positions:
        bush = BerryBush(gx, gy, cell_size=cell_size, berries=5)
        world.add_object(bush)

    # Create input handler and player
    input_handler = InputHandler()
    player = Player(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, radius=20, speed=200)
    # Set world bounds for player
    player.world_rect = screen.get_rect()

    # Build menu for building system
    build_menu = BuildMenu(cell_size)

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

        # Build menu toggle and selection
        if input_handler.build_toggle:
            build_menu.toggle()
        if input_handler.select_gathering_hut and build_menu.visible:
            build_menu.select_gathering_hut()

        # Building placement on mouse click
        if input_handler.mouse_clicked and build_menu.visible and build_menu.selected_building_class is not None:
            mx, my = input_handler.mouse_pos
            gx, gy = grid.world_to_grid(mx, my)
            success = build_menu.attempt_placement(player, world, grid, gx, gy)
            # For now, could add debug message if fails; we'll just ignore
            # Optionally, reset selection or close menu after placement? Keep simple: stay open, selection remains

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

        # Inventory display (top-right corner)
        inv_x = WINDOW_WIDTH - 200
        inv_y = 10
        # Title
        inv_title = font.render("Inventory", True, (0, 0, 0))
        screen.blit(inv_title, (inv_x, inv_y))
        inv_y += 25
        # List items
        items = player.inventory.items
        if not items:
            empty_surface = font.render("(empty)", True, (80, 80, 80))
            screen.blit(empty_surface, (inv_x, inv_y))
        else:
            for resource, count in sorted(items.items()):
                inv_surface = font.render(f"{resource}: {count}", True, (0, 0, 0))
                screen.blit(inv_surface, (inv_x, inv_y))
                inv_y += 20

        # Debug display (F3 toggle)
        if input_handler.show_debug:
            fps_surface = font.render(f"FPS: {clock.get_fps():.1f}", True, (0, 0, 0))
            pos_surface = font.render(f"Player: ({int(player.x)}, {int(player.y)})", True, (0, 0, 0))
            screen.blit(fps_surface, (10, 10))
            screen.blit(pos_surface, (10, 40))

        # Build menu overlay
        build_menu.render(screen, font)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
