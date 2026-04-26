"""
Regression test for Task 50: Ensure new_game() initializes without object overlaps.
"""
import unittest
import os

# Set dummy video driver for headless environments
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

from game_state import new_game

class TestNewGameOverlap(unittest.TestCase):
    def test_new_game_initialization_no_overlap(self):
        """
        Verify that new_game() completes without raising ValueError (overlaps).
        This caught a regression where a stick and a berry bush shared (50, 40).
        """
        try:
            world, player = new_game(800, 600)
        except ValueError as e:
            self.fail(f"new_game() raised ValueError: {e}")
        
        # Additional verification: ensure all objects in the grid are what we expect
        grid = world.grid
        for cell, obj in grid.occupied.items():
            # Basic sanity check: each occupied cell should have an object
            self.assertIsNotNone(obj, f"Cell {cell} marked as occupied but object is None")

if __name__ == '__main__':
    unittest.main()
