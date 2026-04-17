"""
Game state management module.

This module encapsulates all logic for starting a new game and loading a saved game.
It provides a clean separation of concerns and can be reused or tested independently.
"""

from save_system import load_game as _load_game
from world import World
from entity import Player
from map_data import MapData


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
    # Grid and world setup (multi-map)
    cell_size = 32
    grid_width = (window_width + cell_size - 1) // cell_size
    grid_height = (window_height + cell_size - 1) // cell_size

    initial_map = MapData(name="main", width=grid_width, height=grid_height, cell_size=cell_size)
    world = World(initial_map)

    # Create a second map: north_woods (adjacent north of main)
    north_woods = MapData(name="north_woods", width=grid_width, height=grid_height, cell_size=cell_size)

    # Populate north_woods with resources (sparse set)
    second_bush_positions = [(5, 5), (10, 5), (5, 10), (12, 12)]
    for gx, gy in second_bush_positions:
        from berry_bush import BerryBush
        bush = BerryBush(gx, gy, cell_size=cell_size, berries=5)
        north_woods.objects.append(bush)

    second_tree_positions = [(2, 5), (8, 3), (14, 8)]
    for gx, gy in second_tree_positions:
        from tree import Tree
        tree = Tree(gx, gy, cell_size=cell_size, wood=10, respawn_duration=30.0)
        north_woods.objects.append(tree)

    second_rock_positions = [(4, 8), (12, 2)]
    for gx, gy in second_rock_positions:
        from rock import Rock
        rock = Rock(gx, gy, cell_size=cell_size, stone=5)
        north_woods.objects.append(rock)

    second_stick_positions = [(7, 6), (15, 4)]
    for gx, gy in second_stick_positions:
        from stick import Stick
        stick = Stick(gx, gy, cell_size=cell_size, sticks=3)
        north_woods.objects.append(stick)

    # Add a GatheringHut on north_woods (for demo)
    from gathering_hut import GatheringHut
    second_hut = GatheringHut(grid_width//2 + 2, grid_height//2 + 2, cell_size)
    north_woods.objects.append(second_hut)

    # Register the second map with the world
    world.add_map(north_woods)
    # Configure neighbors for boundary-based transitions
    world.current_map.neighbors = {'north': 'north_woods'}
    north_woods.neighbors = {'south': 'main'}

    # Add test berry bushes at various positions for collision and interaction testing
    test_positions = [
        (5, 5), (10, 5), (5, 10), (15, 5), (5, 15),
        (12, 12), (8, 14), (3, 8), (18, 7)
        # No bush at player start to avoid spawn collision
    ]
    for gx, gy in test_positions:
        from berry_bush import BerryBush
        bush = BerryBush(gx, gy, cell_size=cell_size, berries=5)
        world.add_object(bush)

    # Add Trees (2x2) - renewable wood source
    from tree import Tree
    tree_positions = [(2, 5), (8, 3), (14, 8), (20, 12)]
    for gx, gy in tree_positions:
        tree = Tree(gx, gy, cell_size=cell_size, wood=10, respawn_duration=30.0)
        world.add_object(tree)

    # Add Rocks (1x1) - non-renewable stone source
    from rock import Rock
    rock_positions = [(4, 8), (12, 2), (18, 10), (6, 15)]
    for gx, gy in rock_positions:
        rock = Rock(gx, gy, cell_size=cell_size, stone=5)
        world.add_object(rock)

    # Add Sticks (1x1) - small collectibles
    from stick import Stick
    stick_positions = [(7, 6), (15, 4), (10, 16), (3, 12)]
    for gx, gy in stick_positions:
        stick = Stick(gx, gy, cell_size=cell_size, sticks=3)
        world.add_object(stick)

    # Create player
    player = Player(window_width // 2, window_height // 2, radius=20, speed=200)

    # Create a GatheringHut and place it
    from gathering_hut import GatheringHut
    hut_gx, hut_gy = grid_width // 2 + 4, grid_height // 2 + 3
    hut = GatheringHut(hut_gx, hut_gy, cell_size)
    world.add_object(hut)

    # Create a Grass and place it
    from grass import Grass
    grass_gx, grass_gy = grid_width // 2 - 1, grid_height // 2 - 2
    grass = Grass(grass_gx, grass_gy, cell_size)
    world.add_object(grass)

    # Create some critters and assign them to the hut
    # Stats variations: weak (25), strong (75), average (50)
    critter_stats = [
        (25, 25, 25),   # weak
        (75, 75, 75),   # strong
        (50, 50, 50)    # average
    ]
    for i, (strength, speed, endurance) in enumerate(critter_stats):
        # Spawn critters just outside the hut to the right, each offset vertically
        critter_x = hut.x + (hut.width + 1) * cell_size + (i * cell_size)
        critter_y = hut.y + (i * cell_size * 0.5)
        from critter import Critter
        critter = Critter(critter_x, critter_y, cell_size=cell_size,
                          strength=strength, speed_stat=speed, endurance=endurance)
        hut.assign_critter(critter)
        world.add_object(critter)  # Add to world objects and to current_map.critters

    return world, player