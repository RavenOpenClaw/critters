"""
Tests for resource depletion cleanup (RESOURCE_DEPLETION bug fix).
"""
import pytest
from world import World
from map_data import MapData
from stick import Stick
from rock import Rock
from berry_bush import BerryBush
from inventory import Inventory

class MockPlayer:
    def __init__(self):
        self.inventory = Inventory()
    def get_gather_multiplier(self):
        return 1.0

def test_stick_removed_when_depleted():
    cell_size = 32
    map_data = MapData(name="test", width=10, height=10, cell_size=cell_size)
    world = World(map_data)
    stick = Stick(5, 5, cell_size=cell_size, sticks=1)
    world.add_object(stick)
    player = MockPlayer()
    stick.interact(player)  # takes 1, empties
    assert stick.inventory.get_item_count('wood') == 0
    assert stick in world.current_map.objects
    world.cleanup_depleted_resources()
    assert stick not in world.current_map.objects

def test_rock_removed_when_depleted():
    cell_size = 32
    map_data = MapData(name="test", width=10, height=10, cell_size=cell_size)
    world = World(map_data)
    rock = Rock(3, 3, cell_size=cell_size, stone=2)
    world.add_object(rock)
    player = MockPlayer()
    # interact twice to deplete (multiplier 1 takes 1 each)
    rock.interact(player)
    rock.interact(player)
    assert rock.inventory.get_item_count('stone') == 0
    assert rock in world.current_map.objects
    world.cleanup_depleted_resources()
    assert rock not in world.current_map.objects

def test_non_renewable_not_removed_if_not_empty():
    cell_size = 32
    map_data = MapData(name="test", width=10, height=10, cell_size=cell_size)
    world = World(map_data)
    stick = Stick(2, 2, cell_size=cell_size, sticks=3)
    world.add_object(stick)
    player = MockPlayer()
    stick.interact(player)  # takes 1, leaves 2
    assert stick.inventory.get_item_count('wood') == 2
    world.cleanup_depleted_resources()
    assert stick in world.current_map.objects

def test_berry_bush_not_removed_when_depleted():
    # BerryBush is renewable; should not be removed even if empty
    cell_size = 32
    map_data = MapData(name="test", width=10, height=10, cell_size=cell_size)
    world = World(map_data)
    bush = BerryBush(1, 1, cell_size=cell_size, berries=1)
    world.add_object(bush)
    player = MockPlayer()
    bush.interact(player)  # deplete
    assert bush.inventory.get_item_count('berry') == 0
    world.cleanup_depleted_resources()
    assert bush in world.current_map.objects
