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
    cell_size = 24  # slightly smaller grid squares
    # Quadruple the map area: 2x width, 2x height
    grid_width = ((window_width * 2) + cell_size - 1) // cell_size
    grid_height = ((window_height * 2) + cell_size - 1) // cell_size

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

    # Add berry bush clusters at various positions for exploration and multiple gathering sites
    # Each cluster has 3-4 bushes with gaps for player movement.
    clusters = [
        # Northwest Cluster
        [(8, 8), (12, 8), (8, 12), (12, 12)],
        # Southwest Cluster
        [(10, 35), (14, 35), (10, 39), (14, 39)],
        # Northeast Cluster
        [(55, 10), (59, 10), (55, 14), (59, 14)],
        # Southeast Cluster
        [(50, 40), (54, 40), (50, 44), (54, 44)],
        # Scattered bushes near center (but not at spawn)
        [(25, 15), (45, 15), (25, 35), (45, 35)]
    ]
    
    for cluster in clusters:
        for gx, gy in cluster:
            from berry_bush import BerryBush
            bush = BerryBush(gx, gy, cell_size=cell_size, berries=5)
            world.add_object(bush)

    # Add Trees (2x2) - renewable wood source
    from tree import Tree
    tree_positions = [
        (5, 5), (15, 5), (60, 5), (5, 45), (60, 45),
        (30, 10), (40, 40), (10, 25), (55, 25)
    ]
    for gx, gy in tree_positions:
        tree = Tree(gx, gy, cell_size=cell_size, wood=10, respawn_duration=30.0)
        world.add_object(tree)

    # Add Rocks (1x1) - non-renewable stone source
    from rock import Rock
    rock_positions = [
        (10, 2), (2, 10), (64, 2), (2, 48), (64, 48),
        (33, 5), (33, 45), (5, 30), (60, 30)
    ]
    for gx, gy in rock_positions:
        rock = Rock(gx, gy, cell_size=cell_size, stone=5)
        world.add_object(rock)

    # Add Sticks (1x1) - small collectibles
    from stick import Stick
    stick_positions = [
        (15, 15), (50, 15), (15, 40), (50, 40),
        (33, 12), (33, 38), (12, 25), (54, 25)
    ]
    for gx, gy in stick_positions:
        stick = Stick(gx, gy, cell_size=cell_size, sticks=3)
        world.add_object(stick)

    # Create player in the center of the large map
    world_width_px = grid_width * cell_size
    world_height_px = grid_height * cell_size
    player = Player(world_width_px // 2, world_height_px // 2, radius=18, speed=200)

    # Create a GatheringHut and place it near center
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