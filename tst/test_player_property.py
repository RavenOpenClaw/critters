"""
Property-based test for Player movement.

Requires hypothesis: pip install hypothesis
This test verifies that after any movement within bounds, the player remains within world boundaries.
"""
import unittest
from hypothesis import given, strategies as st
import pygame
from entity import Player

# We'll define a simple rect for bounds
WORLD_WIDTH = 800
WORLD_HEIGHT = 600

class TestPlayerMovementProperties(unittest.TestCase):
    def setUp(self):
        self.world_rect = pygame.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT)

    @given(
        x=st.floats(min_value=0, max_value=WORLD_WIDTH),
        y=st.floats(min_value=0, max_value=WORLD_HEIGHT),
        dx=st.integers(min_value=-1, max_value=1),
        dy=st.integers(min_value=-1, max_value=1),
        dt=st.floats(min_value=0.001, max_value=1.0)
    )
    def test_player_stays_in_bounds(self, x, y, dx, dy, dt):
        """Property: After moving, player should remain within world bounds."""
        player = Player(x, y, speed=200)
        player.world_rect = self.world_rect
        player.move(dx, dy, dt)
        self.assertGreaterEqual(player.x, player.radius)
        self.assertLessEqual(player.x, self.world_rect.width - player.radius)
        self.assertGreaterEqual(player.y, player.radius)
        self.assertLessEqual(player.y, self.world_rect.height - player.radius)

if __name__ == '__main__':
    unittest.main()
