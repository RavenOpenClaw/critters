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
from grass import Grass
from build_menu import BuildMenu
from gathering_hut import GatheringHut
from chair import Chair
from campfire import Campfire
from critter import Critter, CritterState
from pathfinding import PathfindingSystem
from crafting_menu import CraftingMenu
from recipes import RECIPES

# Resource icon colors (for HUD)
RESOURCE_COLORS = {
    "food": (255, 0, 0),      # Red square for berries/food
    # Future: add wood, stone, plant, etc.
}

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BACKGROUND_COLOR = (200, 200, 200)  # Light gray
TARGET_FPS = 60

# Colors for critter state labels
STATE_COLORS = {
    CritterState.IDLE: (80, 80, 80),       # Dark gray
    CritterState.GATHER: (0, 150, 0),      # Dark green
    CritterState.RETURN: (0, 0, 200),      # Dark blue
}

def render_hud(screen, player, font, margin=10, icon_size=12):
    """Render resource HUD at top-left corner, left-aligned.

    Shows icons and counts for each resource in player inventory.
    """
    x = margin
    y = margin
    # Sort resources alphabetically for consistent display
    for resource, count in sorted(player.inventory.items.items()):
        color = RESOURCE_COLORS.get(resource, (100, 100, 100))  # Gray fallback
        # Draw small square icon
        pygame.draw.rect(screen, color, (x, y, icon_size, icon_size))
        # Draw resource name and count to the right
        text = f"{resource}: {count}"
        text_surface = font.render(text, True, (0, 0, 0))
        screen.blit(text_surface, (x + icon_size + 5, y))
        y += icon_size + 5  # Move down for next line

def render_active_buffs(screen, player, font):
    """Render active buffs in the top-right corner above the inventory."""
    x = WINDOW_WIDTH - 200
    y = 10
    # Title
    title = font.render("Buffs", True, (0, 0, 0))
    screen.blit(title, (x, y))
    y += 20
    if not player.active_buffs:
        none_surface = font.render("(none)", True, (80, 80, 80))
        screen.blit(none_surface, (x, y))
    else:
        for buff in player.active_buffs:
            text = f"{buff.name}: {buff.remaining:.1f}s"
            buff_surface = font.render(text, True, (0, 0, 0))
            screen.blit(buff_surface, (x, y))
            y += 20

def main():
    """Initialize Pygame and run the main game loop."""
    pygame.init()
    pygame.font.init()  # Ensure font module is initialized
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Critters Prototype")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    # Initialize HUD for resource display
    resource_hud = ResourceHUD()

    # Grid and world setup
    cell_size = 32
    # Compute grid dimensions that cover the window
    grid_width = (WINDOW_WIDTH + cell_size - 1) // cell_size
    grid_height = (WINDOW_HEIGHT + cell_size - 1) // cell_size
    grid = GridSystem(cell_size=cell_size, width=grid_width, height=grid_height)
    world = World(grid)
    # Add test berry bushes at various positions for collision and interaction testing
    test_positions = [
        (5, 5), (10, 5), (5, 10), (15, 5), (5, 15),
        (12, 12), (8, 14), (3, 8), (18, 7)
        # No bush at player start to avoid spawn collision
    ]
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

    # Crafting menu for equipment recipes
    crafting_menu = CraftingMenu(RECIPES)

    # Pathfinding system
    pathfinding = PathfindingSystem()

    # Create a GatheringHut and place it
    hut_gx, hut_gy = grid_width // 2 + 4, grid_height // 2 + 3
    hut = GatheringHut(hut_gx, hut_gy, cell_size)
    world.add_object(hut)

    # Create a Grass and place it # GRASS NOT VISIBLE? And I collide with it???
    grass_gx, grass_gy = grid_width // 2 - 1, grid_height // 2 - 2
    grass = Grass(grass_gx, grass_gy, cell_size)
    world.add_object(grass)

    # Create some critters and assign them to the hut
    critters = []
    for i in range(3):
        # Spawn critters just outside the hut to the right, each offset vertically
        critter_x = hut.x + (hut.width + 1) * cell_size + (i * cell_size)
        critter_y = hut.y + (i * cell_size * 0.5)
        critter = Critter(critter_x, critter_y, cell_size=cell_size)
        hut.assign_critter(critter)
        world.objects.append(critter)  # Add to world objects for rendering
        critters.append(critter)

    running = True
    while running:
        # Calculate delta time (seconds since last frame)
        dt = clock.tick(TARGET_FPS) / 1000.0

        # Input handling
        if not input_handler.handle_events():
            running = False
        input_handler.update(dt)
        input_handler.update_movement()

        # Update player state (buffs, speed recalculation)
        player.update(dt)

        # Player movement (with collision detection)
        player.move(input_handler.move_x, input_handler.move_y, dt, grid=grid)

        # Player interaction (tap = 1, hold = auto-repeat at base rate)
        for _ in range(input_handler.interact_count):
            player.interact(world)
        input_handler.interact_count = 0

        # Build menu toggle and selection
        if input_handler.build_toggle:
            build_menu.toggle()
        if input_handler.select_gathering_hut and build_menu.visible:
            build_menu.select_gathering_hut()

        # Crafting menu toggle and crafting
        if input_handler.crafting_toggle:
            crafting_menu.toggle()
        # If menu open and slot selected, craft that recipe
        if crafting_menu.visible and input_handler.craft_slot is not None:
            idx = input_handler.craft_slot - 1
            if 0 <= idx < len(crafting_menu.recipes):
                recipe = crafting_menu.recipes[idx]
                crafting_menu.craft_selected(player, recipe)
            input_handler.craft_slot = None

        # Building placement on mouse click
        if input_handler.mouse_clicked and build_menu.visible and build_menu.selected_building_class is not None:
            mx, my = input_handler.mouse_pos
            gx, gy = grid.world_to_grid(mx, my)
            success = build_menu.attempt_placement(player, world, grid, gx, gy)
            # For now, could add debug message if fails; we'll just ignore
            # Optionally, reset selection or close menu after placement? Keep simple: stay open, selection remains

        # Update crafting menu (for message timer, etc.)
        crafting_menu.update(dt)

        # Update critters
        for critter in critters:
            critter.update(dt, world, pathfinding)

        # Mark trampled cells by player and critters
        entities = [player] + critters
        for ent in entities:
            gx, gy = grid.world_to_grid(ent.x, ent.y)
            if grid.is_within_bounds(gx, gy):
                world.mark_trampled(gx, gy)
        # Decay trampled status over time
        world.update_trampled(dt)

        # Update world objects that have an update method (regeneration, grass spreading, etc.)
        # Collect any new objects created during updates (e.g., grass spreading)
        new_objects = []
        for obj in world.objects:
            # Only call update on objects that explicitly define it and are not Critters
            # (Critter.update requires additional arguments)
            if isinstance(obj, (BerryBush, Grass)):
                result = obj.update(dt)
                if result is not None:
                    new_objects.append(result)
        # Add new objects to the world after the update loop
        if new_objects:
            world.objects.extend(new_objects)

        # Rendering
        screen.fill(BACKGROUND_COLOR)

        # Draw HUD (top-left)
        render_hud(screen, player, font)

        # Draw world objects
        world.draw(screen)

        # Draw interaction prompts for nearby objects
        for obj in world.objects:
            # Get object center
            if hasattr(obj, 'get_center'):
                ox, oy = obj.get_center()
            else:
                ox, oy = obj.x, obj.y
            dx = ox - player.x
            dy = oy - player.y
            if dx*dx + dy*dy <= player.interaction_radius ** 2:
                if hasattr(obj, 'get_interaction_text'):
                    text = obj.get_interaction_text()
                    if text:
                        text_surface = font.render(text, True, (0, 0, 0))
                        text_rect = text_surface.get_rect(center=(ox, oy - 30))  # raised by 10px
                        screen.blit(text_surface, text_rect)

        # Draw player as a blue circle
        pygame.draw.circle(
            screen,
            (0, 0, 255),  # Blue
            (int(player.x), int(player.y)),
            player.radius
        )

        # Draw critters (red circles) with state labels
        for critter in critters:
            pygame.draw.circle(
                screen,
                (255, 0, 0),  # Red
                (int(critter.x), int(critter.y)),
                int(critter.radius)
            )
            # Render state label above critter with color based on state; optionally add debug info
            label = critter.state.name
            color = STATE_COLORS.get(critter.state, (0, 0, 0))
            if input_handler.show_debug and critter.is_calculating:
                label += " (CALC)"
            label_surface = font.render(label, True, color)
            label_rect = label_surface.get_rect(center=(int(critter.x), int(critter.y) - int(critter.radius) - 10))
            screen.blit(label_surface, label_rect)

        # Buffs display (top-right corner)
        render_active_buffs(screen, player, font)

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
            # Draw interaction radius
            pygame.draw.circle(
                screen,
                (0, 255, 0),  # Green
                (int(player.x), int(player.y)),
                int(player.interaction_radius),
                1  # line thickness
            )

        # Build menu overlay
        build_menu.render(screen, font)

        # Crafting menu overlay
        crafting_menu.render(screen, font)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
