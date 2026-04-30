"""
Unit tests for timed interaction logic and boundary-based distance calculation.
"""
import unittest
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

import pygame
pygame.init()

from entity import Player
from berry_bush import BerryBush
from tree import Tree
from world import World
from grid_system import GridSystem
from utils import get_distance_to_boundary

class TestInteractionLogic(unittest.TestCase):
    def setUp(self):
        self.cell_size = 32
        self.grid = GridSystem(cell_size=self.cell_size, width=20, height=20)
        self.world = World(self.grid)
        self.player = Player(100, 100, radius=10)

    def test_distance_to_boundary(self):
        """Verify boundary-based distance calculation for different object sizes."""
        # 1x1 bush at (0,0) -> pixels (0,0) to (32,32)
        bush = BerryBush(0, 0, self.cell_size)
        
        # Player at (40, 16) is exactly 8 pixels from the right edge
        self.player.x, self.player.y = 40, 16
        dist = get_distance_to_boundary(self.player, bush)
        self.assertEqual(dist, 8.0)
        
        # Player inside bush
        self.player.x, self.player.y = 16, 16
        dist = get_distance_to_boundary(self.player, bush)
        self.assertEqual(dist, 0.0)

        # 3x3 hut at (2,2) -> pixels (64,64) to (160,160)
        from gathering_hut import GatheringHut
        hut = GatheringHut(2, 2, self.cell_size)
        
        # Player at (50, 50) is diagonal from top-left corner
        # dx = 64-50 = 14, dy = 64-50 = 14
        self.player.x, self.player.y = 50, 50
        dist = get_distance_to_boundary(self.player, hut)
        import math
        self.assertAlmostEqual(dist, math.sqrt(14*14 + 14*14))

    def test_timed_interaction_progress(self):
        """Interaction progress should increment with dt and trigger after duration."""
        bush = BerryBush(4, 4, self.cell_size, berries=5)
        self.world.add_object(bush)
        
        # Place player near bush
        bx, by = bush.x + self.cell_size + 5, bush.y + 16
        self.player.x, self.player.y = bx, by
        
        duration = bush.get_interaction_duration() # 2.0s
        
        # Hold key for 1 second
        self.player.update_interaction(1.0, self.world, True)
        self.assertAlmostEqual(self.player.interaction_progress, 0.5)
        self.assertEqual(self.player.inventory.get_item_count('food'), 0)
        
        # Hold for another 1.1 seconds (triggers)
        self.player.update_interaction(1.1, self.world, True)
        self.assertEqual(self.player.inventory.get_item_count('food'), 1)
        # Progress resets to 0.1 because 0.5 + 0.55 = 1.05 -> triggers, then 0.05 left?
        # My implementation resets to 0.0 if still targetable. 
        # Actually it resets to 0.0, then continues. Let's check implementation.
        # current impl: self.interaction_progress = 0.0
        self.assertAlmostEqual(self.player.interaction_progress, 0.0)

    def test_interaction_interruption(self):
        """Progress should reset immediately if key released or player moves away."""
        bush = BerryBush(0, 0, self.cell_size)
        self.world.add_object(bush)
        self.player.x, self.player.y = 40, 16 # Near bush
        
        # Start gathering
        self.player.update_interaction(1.0, self.world, True)
        self.assertGreater(self.player.interaction_progress, 0)
        
        # Release key
        self.player.update_interaction(0.1, self.world, False)
        self.assertEqual(self.player.interaction_progress, 0.0)
        self.assertIsNone(self.player.active_target)
        
        # Restart and move away
        self.player.update_interaction(1.0, self.world, True)
        self.player.x = 500 # Way out of range
        self.player.update_interaction(0.1, self.world, True)
        self.assertEqual(self.player.interaction_progress, 0.0)

if __name__ == '__main__':
    unittest.main()
