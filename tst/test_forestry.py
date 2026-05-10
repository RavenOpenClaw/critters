"""
Tests for Task 65 (UI Fixes) and Task 66 (Advanced Forestry).
"""
import pytest
import pygame
import random
from tree import Tree
from sapling import Sapling
from lumber_mill import LumberMill
from world import World
from map_data import MapData
from grid_system import GridSystem
from entity import Player
from critter import Critter
from constants import ITEM_WOOD, ITEM_SAPLING

class TestForestry:
    def setup_method(self):
        self.cell_size = 24
        self.m = MapData(name="main", width=20, height=20, cell_size=24)
        self.world = World(self.m)
        self.player = Player(100, 100)

    def test_tree_chopping_and_depletion(self):
        """Verify tree drops bonus wood and saplings when fully chopped down."""
        # 1. Setup tree with 1 wood for quick depletion
        tree = Tree(5, 5, cell_size=self.cell_size, wood=1)
        self.world.add_object(tree)
        
        # 2. Interact
        tree.interact(self.player)
        
        # 3. Verify
        # Tree should be removed
        assert tree not in self.world.objects
        # Player should have 1 (base) + 3-5 (bonus) wood
        wood_count = self.player.inventory.get_item_count(ITEM_WOOD)
        assert 4 <= wood_count <= 6
        # Player should have 1-2 saplings
        sapling_count = self.player.inventory.get_item_count(ITEM_SAPLING)
        assert 1 <= sapling_count <= 2

    def test_sapling_placement_constraints(self):
        """Verify sapling placement requires 8 empty surrounding cells."""
        # 1. Place a tree at (5, 5)
        tree = Tree(5, 5, cell_size=self.cell_size)
        self.world.add_object(tree)
        
        # 2. Try to place sapling at (6, 5) - adjacent to tree
        can_place = Sapling.can_place_at(self.world, 6, 5)
        assert can_place is False
        
        # 3. Try to place sapling at (4, 4) - diagonal to tree
        can_place = Sapling.can_place_at(self.world, 4, 4)
        assert can_place is False
        
        # 4. Try to place sapling at (10, 10) - far from tree
        can_place = Sapling.can_place_at(self.world, 10, 10)
        assert can_place is True

    def test_sapling_growth_to_tree(self):
        """Verify sapling replaces itself with a tree after growth timer."""
        # 1. Setup sapling with 0.1s timer
        sapling = Sapling(5, 5, cell_size=self.cell_size, growth_timer=0.1)
        self.world.add_object(sapling)
        
        # 2. Update world
        self.world.update(0.2)
        
        # 3. Verify
        # Sapling should be gone
        assert sapling not in self.world.objects
        # A Tree should be in its place
        trees = [obj for obj in self.world.objects if isinstance(obj, Tree)]
        assert len(trees) == 1
        assert trees[0].gx == 5 and trees[0].gy == 5

    def test_lumber_mill_gathering(self):
        """Verify critters assigned to Lumber Mill correctly target and chop trees."""
        # 1. Setup Mill and Tree
        mill = LumberMill(10, 10, self.cell_size)
        self.world.add_object(mill)
        tree = Tree(11, 14, self.cell_size, wood=10)
        self.world.add_object(tree)
        
        # 2. Assign critter
        critter = Critter(200, 200, cell_size=self.cell_size)
        self.world.add_object(critter)
        mill.assign_critter(critter)
        
        # 3. Simulate AI cycle
        # Force critter to arrived at mill
        critter.x, critter.y = mill.get_center()
        self.world.update(0.1) # Transition to IDLE/GATHER
        
        # Find target
        target = mill.find_resource_in_radius(self.world, critter)
        assert target == tree
        
        # Simulate chopping
        tree.interact(critter)
        assert critter.inventory.get_item_count(ITEM_WOOD) > 0

    def test_deconstruction_unbind_range(self):
        """Verify that deconstruction no longer checks for player distance."""
        from game_engine import GameEngine
        from chair import Chair
        from unittest.mock import MagicMock
        
        pygame.init()
        pygame.display.set_mode((800, 600))
        
        engine = GameEngine()
        # Mock handle_events to do nothing (preserve our manual flags)
        engine.input_handler.handle_events = MagicMock(return_value=True)
        
        map_data = MapData("test", 20, 20, 24)
        world = World(map_data)
        player = Player(0, 0)
        engine.setup((world, player))
        
        chair = Chair(15, 15, 24)
        world.add_object(chair)
        
        # Set flags AFTER engine.setup
        engine.input_handler.deconstruct_mode = True
        engine.input_handler.mouse_clicked = True
        cx, cy = chair.get_center()
        mx, my = engine.camera.apply(cx, cy)
        engine.input_handler.mouse_pos = (mx, my)
        
        # Process input
        engine._handle_input()
        
        assert chair not in world.objects
        pygame.quit()
