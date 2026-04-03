"""
Tests for the deconstruction feature.
"""
import math
import pytest
from building import Building
from inventory import Inventory
from entity import Player
from world import World
from map_data import MapData
from gathering_hut import GatheringHut
from critter import Critter
from chair import Chair
from campfire import Campfire


class DummyWorld:
    """A minimal world-like object for testing deconstruct removal."""
    def __init__(self):
        self.objects = []

    def remove_object(self, obj):
        if obj in self.objects:
            self.objects.remove(obj)


def test_deconstruct_refund_half_round_up():
    """Deconstructing a building refunds half the cost, rounded up."""
    cell_size = 32
    world = DummyWorld()
    player = Player(0, 0, radius=20, speed=200)
    # cost: food=10 -> 5, wood=5 -> 3, stone=1 -> 1
    building = Building(0, 0, 1, 1, cell_size, cost={'food': 10, 'wood': 5, 'stone': 1})
    world.objects.append(building)

    building.deconstruct(world, player)

    assert player.inventory.items['food'] == 5
    assert player.inventory.items['wood'] == 3
    assert player.inventory.items['stone'] == 1
    assert building not in world.objects


def test_deconstruct_with_zero_cost():
    """Deconstructing a building with no cost still removes it."""
    cell_size = 32
    world = DummyWorld()
    player = Player(0, 0, radius=20, speed=200)
    building = Building(0, 0, 1, 1, cell_size, cost={})
    world.objects.append(building)

    building.deconstruct(world, player)

    assert building not in world.objects
    assert not player.inventory.items  # inventory unchanged


def test_deconstruct_removes_building_from_real_world():
    """Test deconstruction removes building from a proper World instance."""
    cell_size = 32
    map_data = MapData(name="test", width=10, height=10, cell_size=cell_size)
    world = World(map_data)
    player = Player(100, 100, radius=20, speed=200)
    building = Building(5, 5, 2, 2, cell_size, cost={'wood': 4})
    world.add_object(building)
    assert building in world.objects

    building.deconstruct(world, player)

    assert building not in world.objects
    # Also ensure player received refund
    assert player.inventory.items['wood'] == 2  # half of 4


def test_deconstruct_unassigns_critters_on_hut():
    """Deconstructing a GatheringHut unassigns all assigned critters."""
    cell_size = 32
    map_data = MapData(name="test", width=20, height=20, cell_size=cell_size)
    world = World(map_data)
    player = Player(100, 100, radius=20, speed=200)
    hut = GatheringHut(5, 5, cell_size)
    world.add_object(hut)

    critters = [Critter(100, 100, cell_size=cell_size) for _ in range(3)]
    for c in critters:
        hut.assign_critter(c)
        world.add_object(c)

    # Precondition: all critters assigned
    for c in critters:
        assert c.assigned_hut is hut
    assert len(hut.assigned_critters) == 3

    hut.deconstruct(world, player)

    # Hut removed
    assert hut not in world.objects
    # Critters unassigned
    for c in critters:
        assert c.assigned_hut is None
    assert len(hut.assigned_critters) == 0


def test_deconstruct_works_on_various_building_subclasses():
    """Deconstruction works on any Building subclass (Chair, Campfire)."""
    cell_size = 32
    map_data = MapData(name="test", width=10, height=10, cell_size=cell_size)
    world = World(map_data)
    player = Player(100, 100, radius=20, speed=200)

    chair = Chair(3, 3, cell_size)
    campfire = Campfire(6, 6, cell_size)
    world.add_object(chair)
    world.add_object(campfire)

    chair.deconstruct(world, player)
    assert chair not in world.objects
    # No cost for chair? Actually Chair has cost? Need to check. In design, Chair likely has cost. But our test just verifies removal.

    campfire.deconstruct(world, player)
    assert campfire not in world.objects
