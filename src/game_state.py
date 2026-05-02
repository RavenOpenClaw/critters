"""
Game state management module.

This module encapsulates all logic for starting a new game and loading a saved game.
It provides a clean separation of concerns and can be reused or tested independently.
"""

from save_system import load_game as _load_game
from world import World
from entity import Player
from map_data import MapData, Portal


def load_game(save_path: str) -> tuple[World, Player]:
    """
    Load a saved game from the specified save file.

    Args:
        save_path: Path to the save file (e.g., "saves/save.json").

    Returns:
        A tuple of (world, player) representing the loaded game state.

    Raises:
        Exception: If loading fails for any reason.
    """
    return _load_game(save_path)


def new_game(window_width: int = 800, window_height: int = 600) -> tuple[World, Player]:
    """
    Start a new game with default settings.

    Args:
        window_width: Width of the game window (default: 800).
        window_height: Height of the game window (default: 600).

    Returns:
        A tuple of (world, player) representing the new game state.
    """
    import random
    # Grid and world setup (multi-map)
    cell_size = 24  # slightly smaller grid squares
    # Quadruple the map area: 2x width, 2x height
    grid_width = 80
    grid_height = 60

    initial_map = MapData(name="main", width=grid_width, height=grid_height, cell_size=cell_size)
    world = World(initial_map)

    # Create a second map: east_plains (adjacent east of main)
    east_map = MapData(name="east_plains", width=grid_width, height=grid_height, cell_size=cell_size)
    world.add_map(east_map)

    # Link maps using neighbors for edge-to-edge travel
    initial_map.neighbors['east'] = "east_plains"
    east_map.neighbors['west'] = "main"

    # --- Populate Main Map ---

    # Add Berry Bushes (natural cluster)
    from berry_bush import BerryBush
    for _ in range(12):
        gx = random.randint(10, 30)
        gy = random.randint(10, 30)
        if not world.grid.is_occupied(gx, gy):
            world.add_object(BerryBush(gx, gy, cell_size))

    # Add Trees (2x2)
    from tree import Tree
    for _ in range(5):
        gx = random.randint(5, grid_width-5)
        gy = random.randint(5, grid_height-5)
        # Manual check for 2x2 area
        is_free = True
        for dx in range(2):
            for dy in range(2):
                if world.grid.is_occupied(gx + dx, gy + dy):
                    is_free = False
                    break
        if is_free:
            world.add_object(Tree(gx, gy, cell_size))

    # Add Rocks
    from rock import Rock
    for _ in range(10):
        gx = random.randint(5, grid_width-5)
        gy = random.randint(5, grid_height-5)
        if not world.grid.is_occupied(gx, gy):
            world.add_object(Rock(gx, gy, cell_size, stone=random.randint(5, 15)))

    # Add Sticks
    from stick import Stick
    for _ in range(15):
        gx = random.randint(5, grid_width-5)
        gy = random.randint(5, grid_height-5)
        if not world.grid.is_occupied(gx, gy):
            world.add_object(Stick(gx, gy, cell_size, sticks=random.randint(2, 5)))

    # Add Grass (scattered)
    from grass import Grass
    for _ in range(15):
        gx = random.randint(5, grid_width-5)
        gy = random.randint(5, grid_height-5)
        # Grass doesn't occupy grid, but we check anyway to avoid spawning under buildings
        if not world.grid.is_occupied(gx, gy):
            world.add_object(Grass(gx, gy, cell_size))

    # --- Buildings ---
    # Create player in the center
    player = Player(grid_width * cell_size // 2, grid_height * cell_size // 2, radius=18, speed=200)

    # Gathering Hut
    from gathering_hut import GatheringHut
    gh_gx, gh_gy = grid_width // 2 - 5, grid_height // 2 - 2
    gh = GatheringHut(gh_gx, gh_gy, cell_size)
    world.add_object(gh)

    # Mating Hut (Start with one!)
    from mating_hut import MatingHut
    mh_gx, mh_gy = grid_width // 2 + 3, grid_height // 2 - 2
    mh = MatingHut(mh_gx, mh_gy, cell_size)
    world.add_object(mh)

    # --- Specialized Starting Critters ---
    # (STR, SPD, END)
    critter_configs = [
        (10, 1, 1),   # Strong
        (1, 10, 1),   # Fast
        (1, 1, 10),   # Hardy
    ]
    from critter import Critter
    for i, (str_v, spd_v, end_v) in enumerate(critter_configs):
        cx = gh.x + (gh.width + 1) * cell_size
        cy = gh.y + (i * cell_size)
        c = Critter(cx, cy, cell_size=cell_size, strength=str_v, speed_stat=spd_v, endurance=end_v)
        gh.assign_critter(c) # Start assigned to gathering
        world.add_object(c)

    # --- Populate East Plains (Bonus) ---
    world.switch_map("east_plains")
    for _ in range(20):
        gx, gy = random.randint(5, 75), random.randint(5, 55)
        if not world.grid.is_occupied(gx, gy):
            world.add_object(BerryBush(gx, gy, cell_size))

    # Return to main map for start
    world.switch_map("main")

    return world, player
