import pytest
from save_system import serialize_world, deserialize_world
from world import World
from map_data import MapData
from chair import Chair
from campfire import Campfire

def test_chair_serialization_roundtrip():
    cell_size = 32
    chair = Chair(5, 5, cell_size=cell_size)
    map_data = MapData(name="test", width=20, height=15, cell_size=cell_size)
    world = World(map_data)
    world.add_object(chair)
    data = serialize_world(world)
    new_world = deserialize_world(data)
    chairs = [o for o in new_world.current_map.objects if isinstance(o, Chair)]
    assert len(chairs) == 1
    c = chairs[0]
    assert c.gx == 5 and c.gy == 5
    assert c.cost == Chair.cost

def test_campfire_serialization_roundtrip():
    cell_size = 32
    campfire = Campfire(10, 10, cell_size=cell_size)
    map_data = MapData(name="test", width=20, height=15, cell_size=cell_size)
    world = World(map_data)
    world.add_object(campfire)
    data = serialize_world(world)
    new_world = deserialize_world(data)
    campfires = [o for o in new_world.current_map.objects if isinstance(o, Campfire)]
    assert len(campfires) == 1
    c = campfires[0]
    assert c.gx == 10 and c.gy == 10
    assert c.cost == Campfire.cost
