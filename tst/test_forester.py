"""
Tests for ForesterHut and AI planting logic.
"""
import pytest
import pygame
import random
from forester_hut import ForesterHut
from sapling import Sapling
from world import World
from map_data import MapData
from grid_system import GridSystem
from entity import Player
from critter import Critter, CritterState
from constants import ITEM_SAPLING

class TestForester:
    def setup_method(self):
        self.cell_size = 24
        self.m = MapData(name="main", width=20, height=20, cell_size=24)
        self.world = World(self.m)
        self.player = Player(100, 100)

    def test_forester_fetch_and_plant_cycle(self):
        """Verify critter assigned to Forester Hut fetches saplings and plants them."""
        # 1. Setup Hut with saplings
        hut = ForesterHut(10, 10, self.cell_size)
        hut.storage.add(ITEM_SAPLING, 5)
        self.world.add_object(hut)
        
        # 2. Assign critter
        critter = Critter(200, 200, cell_size=self.cell_size)
        self.world.add_object(critter)
        hut.assign_critter(critter)
        
        # 3. Simulate arrival and fetching
        # Force critter adjacent to hut
        critter.x, critter.y = hut.x - 10, hut.y - 10
        critter._deposit_at_hut() # Standard transition point
        
        assert critter.state == CritterState.PLANT
        assert critter.inventory.get_item_count(ITEM_SAPLING) == 1
        assert hut.storage.get_item_count(ITEM_SAPLING) == 4
        
        # 4. Simulate planting
        # Mock a valid spot within radius
        # We need a pathfinding mock or a small world where a path is found
        from pathfinding import PathfindingSystem
        ps = PathfindingSystem()
        
        # Force a goal cell and path
        critter.goal_cell = (5, 5)
        critter.path = [(5, 5)]
        critter.gathering = True # Arrived
        
        # Update to trigger planting
        critter._update_plant(0.1, self.world, ps) # Progressing...
        # Cheat to finish interaction
        critter.interaction_progress = 1.0
        critter._update_plant(0.1, self.world, ps)
        
        # 5. Verify sapling placed
        saplings = [obj for obj in self.world.objects if isinstance(obj, Sapling)]
        assert len(saplings) == 1
        assert saplings[0].gx == 5 and saplings[0].gy == 5
        assert critter.inventory.get_item_count(ITEM_SAPLING) == 0
        assert critter.state == CritterState.RETURN # Going back for more

    def test_overburdened_speed_penalty(self):
        """Verify that critters move slower when carrying more than capacity."""
        critter = Critter(0, 0, endurance=20) # Capacity = 1
        assert critter.carry_capacity == 1
        
        base_speed = critter.get_movement_speed()
        
        # Overburden: 2 items
        critter.inventory.add("wood", 2)
        penalty_speed = critter.get_movement_speed()
        
        assert penalty_speed == base_speed * 0.5
