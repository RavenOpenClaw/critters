"""
Tests for follower map transitions.
"""
import pytest
from world import World
from map_data import MapData
from critter import Critter
from entity import Player
from grid_system import GridSystem

def test_follower_map_transition_boundary():
    # Setup
    cell_size = 24
    m1 = MapData(name="map1", width=10, height=10, cell_size=cell_size)
    m2 = MapData(name="map2", width=10, height=10, cell_size=cell_size)
    m1.neighbors['east'] = "map2"
    m2.neighbors['west'] = "map1"
    
    world = World(m1)
    world.add_map(m2)
    
    player = Player(x=cell_size*10 + 1, y=cell_size*5) # Just off the east edge of map1
    c = Critter(x=cell_size*9, y=cell_size*5, cell_size=cell_size)
    world.add_object(c)
    
    # Make critter follow player
    c.start_follow(player)
    assert c in player.following_critters
    assert c in world.current_map.objects
    
    # Perform transition
    transitioned = world.handle_map_transition(player)
    
    assert transitioned is True
    assert world.current_map.name == "map2"
    
    # Check player position (should be at the west edge of map2)
    assert player.x == cell_size / 2
    
    # Check critter transport
    assert c in world.current_map.objects
    assert c in world.current_map.critters
    assert c.x == player.x
    assert c.y == player.y
    assert c in player.following_critters

if __name__ == "__main__":
    test_follower_map_transition_boundary()
    print("Test passed!")
