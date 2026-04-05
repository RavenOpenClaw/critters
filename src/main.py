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
from map_data import MapData
from berry_bush import BerryBush
from grass import Grass
from tree import Tree
from rock import Rock
from stick import Stick
from build_menu import BuildMenu
from building import Building
from gathering_hut import GatheringHut
from chair import Chair
from campfire import Campfire
from buff import Buff  # for applying campfire aura
from critter_inspector import CritterInspector
from critter import Critter, CritterState
from pathfinding import PathfindingSystem
from crafting_menu import CraftingMenu
from recipes import RECIPES
from save_system import save_game, load_game
from title_screen import TitleScreen

# Resource icon colors (for HUD)
RESOURCE_COLORS = {
    "food": (255, 0, 0),      # Red square for berries/food
    "wood": (101, 67, 33),    # Brown for wood
    "stone": (128, 128, 128), # Gray for stone
    "stick": (210, 180, 140), # Tan for sticks (unused after stick->wood change)
    "plant": (144, 238, 144), # Light green for plants
    "berry": (255, 0, 0),     # Red for berries (explicit mapping)
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

    # Title screen
    title = TitleScreen(WINDOW_WIDTH, WINDOW_HEIGHT)
    # Title screen loop
    while title.selected_action is None:
        dt = clock.tick(TARGET_FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            title.handle_event(event)
        title.render(screen)
        pygame.display.flip()

    action = title.selected_action
    if action == "quit":
        pygame.quit()
        sys.exit()

    # World and player setup based on action
    if action == "continue":
        try:
            world, player = load_game("saves/save.json")
            grid = world.grid
            player.world_rect = screen.get_rect()
            # Derive grid parameters from loaded map
            cell_size = world.current_map.cell_size
            grid_width = world.current_map.width
            grid_height = world.current_map.height
        except Exception as e:
            print(f"Load failed: {e}")
            # Fallback to new game
            action = "new_game"

    if action == "new_game":
        # Grid and world setup (multi-map)
        cell_size = 32
        grid_width = (WINDOW_WIDTH + cell_size - 1) // cell_size
        grid_height = (WINDOW_HEIGHT + cell_size - 1) // cell_size
        initial_map = MapData(name="main", width=grid_width, height=grid_height, cell_size=cell_size)
        world = World(initial_map)
        grid = world.grid  # alias to current grid for convenience
        # Add test berry bushes at various positions for collision and interaction testing
        test_positions = [
            (5, 5), (10, 5), (5, 10), (15, 5), (5, 15),
            (12, 12), (8, 14), (3, 8), (18, 7)
            # No bush at player start to avoid spawn collision
        ]
        for gx, gy in test_positions:
            bush = BerryBush(gx, gy, cell_size=cell_size, berries=5)
            world.add_object(bush)

        # Add Trees (2x2) - renewable wood source
        tree_positions = [(2, 5), (8, 3), (14, 8), (20, 12)]
        for gx, gy in tree_positions:
            tree = Tree(gx, gy, cell_size=cell_size, wood=10, respawn_duration=30.0)
            world.add_object(tree)

        # Add Rocks (1x1) - non-renewable stone source
        rock_positions = [(4, 8), (12, 2), (18, 10), (6, 15)]
        for gx, gy in rock_positions:
            rock = Rock(gx, gy, cell_size=cell_size, stone=5)
            world.add_object(rock)

        # Add Sticks (1x1) - small collectibles
        stick_positions = [(7, 6), (15, 4), (10, 16), (3, 12)]
        for gx, gy in stick_positions:
            stick = Stick(gx, gy, cell_size=cell_size, sticks=3)
            world.add_object(stick)

        # Create player
        player = Player(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, radius=20, speed=200)
        # Set world bounds for player
        player.world_rect = screen.get_rect()
    else:
        # Should not happen, but default to new game if unknown action
        raise ValueError(f"Unknown title screen action: {action}")

    # Create input handler (common to both paths)
    input_handler = InputHandler()

    # For a new game, add hut, grass, and starting critters
    if action == "new_game":
        # Create a GatheringHut and place it
        hut_gx, hut_gy = grid_width // 2 + 4, grid_height // 2 + 3
        hut = GatheringHut(hut_gx, hut_gy, cell_size)
        world.add_object(hut)

        # Create a Grass and place it
        grass_gx, grass_gy = grid_width // 2 - 1, grid_height // 2 - 2
        grass = Grass(grass_gx, grass_gy, cell_size)
        world.add_object(grass)

        # Create some critters and assign them to the hut
        for i in range(3):
            # Spawn critters just outside the hut to the right, each offset vertically
            critter_x = hut.x + (hut.width + 1) * cell_size + (i * cell_size)
            critter_y = hut.y + (i * cell_size * 0.5)
            critter = Critter(critter_x, critter_y, cell_size=cell_size)
            hut.assign_critter(critter)
            world.add_object(critter)  # Add to world objects and to current_map.critters

    # Crafting menu for equipment recipes (common)
    crafting_menu = CraftingMenu(RECIPES)

    # Pathfinding system (common)
    pathfinding = PathfindingSystem()

    # Build menu for building system
    build_menu = BuildMenu(cell_size)

    # Critter inspector UI
    critter_inspector = CritterInspector(cell_size, font, WINDOW_WIDTH, WINDOW_HEIGHT)

    # HUD build button rectangle (top-left, below resource HUD)
    hud_button_margin = 10
    hud_button_size = 40
    hud_button_rect = pygame.Rect(
        hud_button_margin,
        WINDOW_HEIGHT - hud_button_size - hud_button_margin,
        hud_button_size,
        hud_button_size
    )

    running = True
    while running:
        # Calculate delta time (seconds since last frame)
        dt = clock.tick(TARGET_FPS) / 1000.0

        # Input handling
        if not input_handler.handle_events():
            running = False
        input_handler.update(dt)
        input_handler.update_movement()

        # Save/Load requests
        if input_handler.save_request:
            try:
                save_game(world, player, "saves/save.json")
                print("Game saved.")
            except Exception as e:
                print(f"Save failed: {e}")

        if input_handler.load_request:
            try:
                world, player = load_game("saves/save.json")
                grid = world.grid
                player.world_rect = screen.get_rect()
                print("Game loaded.")
            except Exception as e:
                print(f"Load failed: {e}")

        # Apply campfire aura buffs to player and critters
        for obj in world.current_map.objects:
            if isinstance(obj, Campfire):
                cx = obj.x + (obj.width * obj.cell_size) / 2.0
                cy = obj.y + (obj.height * obj.cell_size) / 2.0
                radius_sq = (3.0 * obj.cell_size) ** 2
                # Player
                dx = player.x - cx
                dy = player.y - cy
                if dx*dx + dy*dy <= radius_sq:
                    buff = Buff("Strength", {'gather': 2.0}, duration=30.0)
                    player.apply_buff(buff)
                # Critters
                for critter in world.current_map.critters:
                    dx = critter.x - cx
                    dy = critter.y - cy
                    if dx*dx + dy*dy <= radius_sq:
                        buff = Buff("Strength", {'gather': 2.0}, duration=30.0)
                        critter.apply_buff(buff)

        # Update player state (buffs, speed recalculation)
        player.update(dt)

        # Player movement (with collision detection)
        player.move(input_handler.move_x, input_handler.move_y, dt, grid=grid)

        # Handle map transitions
        world.handle_map_transition(player)
        # Keep grid alias in sync with current map's grid
        grid = world.grid

        # Player interaction (tap = 1, hold = auto-repeat at base rate)
        for _ in range(input_handler.interact_count):
            player.interact(world)
        input_handler.interact_count = 0

        # Build menu toggle (B key) and mouse handling
        if input_handler.build_toggle:
            build_menu.toggle()

        if input_handler.mouse_clicked:
            mx, my = input_handler.mouse_pos
            clicked_hud = hud_button_rect.collidepoint(mx, my)
            clicked_build_menu = False
            if clicked_hud:
                build_menu.toggle()
            elif build_menu.visible:
                clicked_build_menu = build_menu.handle_mouse_click((mx, my))

            # Only act if click was not on HUD or build menu UI
            if not clicked_hud and not clicked_build_menu:
                # If inspector is visible, let it handle the click first to consume events inside its panel
                inspector_consumed = False
                if critter_inspector.visible:
                    inspector_consumed = critter_inspector.handle_mouse_click((mx, my))
                # If inspector didn't consume the click, handle other interactions
                if not inspector_consumed:
                    # Deconstruction mode takes precedence
                    if input_handler.deconstruct_mode:
                        gx, gy = grid.world_to_grid(mx, my)
                        if grid.is_within_bounds(gx, gy):
                            # Check if a building occupies this grid cell
                            if (gx, gy) in grid.occupied:
                                obj = grid.occupied[(gx, gy)]
                                if isinstance(obj, Building):
                                    # Check player is within interaction range
                                    ox, oy = obj.get_center()
                                    dx = player.x - ox
                                    dy = player.y - oy
                                    if dx*dx + dy*dy <= player.interaction_radius**2:
                                        obj.deconstruct(world, player)
                    else:
                        # Critter inspection: prioritize clicking on critters
                        clicked_critter = False
                        for c in world.current_map.critters:
                            # Check player is within interaction radius of the critter
                            dxp = player.x - c.x
                            dyp = player.y - c.y
                            if dxp*dxp + dyp*dyp > player.interaction_radius**2:
                                continue
                            # Check mouse click near critter (within radius + 5px tolerance)
                            dx = mx - c.x
                            dy = my - c.y
                            if dx*dx + dy*dy <= (c.radius + 5) ** 2:
                                # Toggle inspector for this critter
                                if critter_inspector.visible and critter_inspector.selected_critter is c:
                                    critter_inspector.hide()
                                else:
                                    critter_inspector.toggle(c)
                                clicked_critter = True
                                break
                        # If no critter clicked and build menu is active with a selected building, attempt placement
                        if not clicked_critter and build_menu.visible and build_menu.selected_building_class is not None:
                            gx, gy = grid.world_to_grid(mx, my)
                            if grid.is_within_bounds(gx, gy):
                                build_menu.attempt_placement(player, world, grid, gx, gy)

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

        # Update crafting menu (for message timer, etc.)
        crafting_menu.update(dt)

        # Update critters
        for critter in world.current_map.critters:
            critter.update(dt, world, pathfinding)

        # Mark trampled cells by player and critters
        entities = [player] + world.current_map.critters
        for ent in entities:
            gx, gy = grid.world_to_grid(ent.x, ent.y)
            if grid.is_within_bounds(gx, gy):
                world.mark_trampled(gx, gy)
        # Decay trampled status over time
        world.update_trampled(dt)

        # Update world objects that have an update method (regeneration, grass spreading, etc.)
        new_objects = []
        for obj in list(world.current_map.objects):
            if isinstance(obj, (BerryBush, Grass)):
                result = obj.update(dt)
                if result is not None:
                    new_objects.append(result)
        for new_obj in new_objects:
            world.add_object(new_obj)

        # Remove depleted non-renewable resources (Sticks, Rocks)
        world.cleanup_depleted_resources()

        # Rendering
        screen.fill(BACKGROUND_COLOR)

        # Draw world objects
        world.draw(screen)

        # Draw interaction prompts for nearby objects
        for obj in world.current_map.objects:
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
        for critter in world.current_map.critters:
            dx, dy = critter.get_render_offset()
            rx = int(critter.x + dx)
            ry = int(critter.y + dy)
            pygame.draw.circle(
                screen,
                (255, 0, 0),  # Red
                (rx, ry),
                int(critter.radius)
            )
            # Render state label above critter with color based on state; optionally add debug info
            label = critter.state.name
            color = STATE_COLORS.get(critter.state, (0, 0, 0))
            if input_handler.show_debug and critter.is_calculating:
                label += " (CALC)"
            label_surface = font.render(label, True, color)
            label_rect = label_surface.get_rect(center=(rx, ry - int(critter.radius) - 10))
            screen.blit(label_surface, label_rect)

        # HUD elements (drawn on top of world)
        # Draw HUD (top-left)
        render_hud(screen, player, font)

        # Draw HUD build button (bottom-left)
        pygame.draw.rect(screen, (100, 100, 200), hud_button_rect)
        build_lbl = font.render("Build", True, (255, 255, 255))
        screen.blit(build_lbl, build_lbl.get_rect(center=hud_button_rect.center))

        # Buffs display (top-right corner)
        render_active_buffs(screen, player, font)

        # Debug display (F3 toggle)
        if input_handler.show_debug:
            fps_surface = font.render(f"FPS: {clock.get_fps():.1f}", True, (0, 0, 0))
            pos_surface = font.render(f"Player: ({int(player.x)}, {int(player.y)})", True, (0, 0, 0))
            # Counts
            critter_count = len(world.current_map.critters)
            building_count = sum(1 for obj in world.current_map.objects if isinstance(obj, Building))
            # Performance: entity count and trampled cells
            entity_count = critter_count + 1  # +1 for player
            trampled_count = len(world.trampled)
            count_surface = font.render(f"Critters: {critter_count}  Buildings: {building_count}", True, (0, 0, 0))
            perf_surface = font.render(f"Entities: {entity_count}  Trampled: {trampled_count}", True, (0, 0, 0))
            screen.blit(fps_surface, (10, 10))
            screen.blit(pos_surface, (10, 40))
            screen.blit(count_surface, (10, 70))
            screen.blit(perf_surface, (10, 100))
            # Draw interaction radius
            pygame.draw.circle(
                screen,
                (0, 255, 0),  # Green
                (int(player.x), int(player.y)),
                int(player.interaction_radius),
                1  # line thickness
            )
            # Overlay trampled cells (semi-transparent red)
            for (gx, gy) in world.trampled:
                wx, wy = world.grid.grid_to_world(gx, gy)
                cell_sz = world.grid.cell_size
                overlay = pygame.Surface((cell_sz, cell_sz), pygame.SRCALPHA)
                overlay.fill((255, 0, 0, 50))  # red with alpha
                screen.blit(overlay, (wx, wy))

        # Build menu overlay (pass HUD button rect for consistent styling? not needed)
        build_menu.render(screen, font, hud_button_rect=hud_button_rect)

        # Crafting menu overlay
        crafting_menu.render(screen, font)

        # Deconstruction mode indicator
        if input_handler.deconstruct_mode:
            decon_surface = font.render("Deconstruction Mode (X to exit)", True, (255, 0, 0))
            screen.blit(decon_surface, (WINDOW_WIDTH - decon_surface.get_width() - 10, WINDOW_HEIGHT - 30))

        # Draw critter inspector UI (if visible)
        critter_inspector.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
