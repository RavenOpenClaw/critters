"""Save/Load system round-trip tests."""
import pytest
import tempfile
import os
from pathlib import Path
from save_system import save_game, load_game, serialize_world, deserialize_world, _serialize_player, _deserialize_player
from world import World
from entity import Player
from map_data import MapData
from berry_bush import BerryBush
from gathering_hut import GatheringHut
from critter import Critter
from grass import Grass
from obstacle import Obstacle
from tree import Tree
from rock import Rock
from stick import Stick
# No MatingHut needed for current tests

def make_test_world():
    """Create a small world with a variety of entities for testing."""
    cell_size = 32
    width = 20
    height = 15
    map_data = MapData(name="test", width=width, height=height, cell_size=cell_size)
    world = World(map_data)
    # Player with some inventory and buffs
    player = Player(100, 80, radius=20, speed=200)
    player.inventory.items = {"food": 5}
    # Buff: add a simple buff if Buff class is available; skip to avoid extra imports
    # Add various world objects
    bush = BerryBush(5, 5, cell_size=cell_size, berries=3)
    world.add_object(bush)
    hut = GatheringHut(10, 10, cell_size)
    world.add_object(hut)
    # Add a critter and assign to hut
    critter = Critter(400, 300, cell_size=cell_size, strength=5, speed_stat=1.2, endurance=10)
    hut.assign_critter(critter)
    world.add_object(critter)
    # Add grass
    grass = Grass(8, 8, cell_size)
    world.add_object(grass)
    # Add obstacle (1x1)
    obstacle = Obstacle(18, 10, 1, 1, cell_size, work_units=5)
    world.add_object(obstacle)
    return world, player

def test_serialize_world_contains_expected_keys():
    world, _ = make_test_world()
    data = serialize_world(world)
    assert "version" in data
    assert "current_map_name" in data
    assert "maps" in data
    assert isinstance(data["maps"], list)
    assert len(data["maps"]) == 1
    map_data = data["maps"][0]
    assert "name" in map_data
    assert "objects" in map_data
    assert "critters" in map_data
    assert "trampled" in map_data
    assert "portals" in map_data

def test_deserialize_world_roundtrip_preserves_objects():
    world, _ = make_test_world()
    data = serialize_world(world)
    new_world = deserialize_world(data)
    # Compare map name and dimensions
    assert new_world.current_map.name == world.current_map.name
    assert new_world.current_map.width == world.current_map.width
    assert new_world.current_map.height == world.current_map.height
    # Count world objects by type
    def count_by_type(objects):
        counts = {}
        for obj in objects:
            cls = obj.__class__.__name__
            counts[cls] = counts.get(cls, 0) + 1
        return counts
    orig_counts = count_by_type(world.current_map.objects)
    new_counts = count_by_type(new_world.current_map.objects)
    assert orig_counts == new_counts
    # Ensure references: each object has world set
    for obj in new_world.current_map.objects:
        assert obj.world is new_world
    # Ensure GatheringHut has assigned_critters rebuilt
    huts = [obj for obj in new_world.current_map.objects if isinstance(obj, GatheringHut)]
    assert len(huts) == 1
    hut = huts[0]
    assert hasattr(hut, "assigned_critters")
    assert len(hut.assigned_critters) == 1
    assert hut.assigned_critters[0].__class__.__name__ == "Critter"

def test_player_serialization_roundtrip():
    world, player = make_test_world()
    player_dict = _serialize_player(player)
    new_player = _deserialize_player(player_dict)
    assert new_player.x == player.x
    assert new_player.y == player.y
    assert new_player.radius == player.radius
    assert new_player.base_speed == player.base_speed
    assert new_player.speed == player.speed
    assert new_player.inventory.items == player.inventory.items
    # active_buffs may be empty; skip if empty
    # For unlocked_equipment and equipped sets
    assert new_player.unlocked_equipment == player.unlocked_equipment
    assert new_player.equipped == player.equipped

def test_save_and_load_file():
    world, player = make_test_world()
    with tempfile.TemporaryDirectory() as tmpdir:
        save_path = Path(tmpdir) / "save.json"
        save_game(world, player, save_path)
        assert os.path.exists(save_path)
        # Load
        loaded_world, loaded_player = load_game(save_path)
        # Verify loaded world matches original
        assert loaded_world.current_map.name == world.current_map.name
        loaded_counts = {}
        for obj in loaded_world.current_map.objects:
            cls = obj.__class__.__name__
            loaded_counts[cls] = loaded_counts.get(cls, 0) + 1
        original_counts = {}
        for obj in world.current_map.objects:
            cls = obj.__class__.__name__
            original_counts[cls] = original_counts.get(cls, 0) + 1
        assert loaded_counts == original_counts
        # Verify player inventory
        assert loaded_player.inventory.items == player.inventory.items

def test_critter_assignment_preserved_after_load():
    world, player = make_test_world()
    # The world already has a hut with an assigned critter
    # Get the hut and its assigned critter before saving
    huts_before = [obj for obj in world.current_map.objects if isinstance(obj, GatheringHut)]
    assert len(huts_before) == 1
    hut_before = huts_before[0]
    assert len(hut_before.assigned_critters) == 1
    critter_before = hut_before.assigned_critters[0]
    # Save and load
    data = serialize_world(world)
    world_after = deserialize_world(data)
    huts_after = [obj for obj in world_after.current_map.objects if isinstance(obj, GatheringHut)]
    assert len(huts_after) == 1
    hut_after = huts_after[0]
    assert len(hut_after.assigned_critters) == 1
    critter_after = hut_after.assigned_critters[0]
    # Check that the critter's essential attributes are preserved
    assert critter_after.x == critter_before.x
    assert critter_after.y == critter_before.y
    assert critter_after.strength == critter_before.strength
    assert critter_after.state == critter_before.state

def test_tree_serialization_roundtrip():
    cell_size = 32
    tree = Tree(5, 5, cell_size=cell_size, wood=10, respawn_duration=20.0)
    map_data = MapData(name="test", width=20, height=15, cell_size=cell_size)
    world = World(map_data)
    world.add_object(tree)
    data = serialize_world(world)
    new_world = deserialize_world(data)
    trees = [o for o in new_world.current_map.objects if isinstance(o, Tree)]
    assert len(trees) == 1
    t = trees[0]
    assert t.gx == 5 and t.gy == 5
    assert t.inventory.get_item_count('wood') == 10
    assert t.max_wood == 10
    assert t.respawn_duration == 20.0
    assert not t.depleted

def test_rock_serialization_roundtrip():
    cell_size = 32
    rock = Rock(3, 4, cell_size=cell_size, stone=5)
    map_data = MapData(name="test", width=20, height=15, cell_size=cell_size)
    world = World(map_data)
    world.add_object(rock)
    data = serialize_world(world)
    new_world = deserialize_world(data)
    rocks = [o for o in new_world.current_map.objects if isinstance(o, Rock)]
    assert len(rocks) == 1
    r = rocks[0]
    assert r.gx == 3 and r.gy == 4
    assert r.inventory.get_item_count('stone') == 5

def test_stick_serialization_roundtrip():
    cell_size = 32
    stick = Stick(2, 2, cell_size=cell_size, sticks=3)
    map_data = MapData(name="test", width=20, height=15, cell_size=cell_size)
    world = World(map_data)
    world.add_object(stick)
    data = serialize_world(world)
    new_world = deserialize_world(data)
    sticks = [o for o in new_world.current_map.objects if isinstance(o, Stick)]
    assert len(sticks) == 1
    s = sticks[0]
    assert s.gx == 2 and s.gy == 2
    assert s.inventory.get_item_count('stick') == 3
