import unittest
from grid_system import GridSystem
from world_object import WorldObject
from entity import Player

class TestCollisionDetection(unittest.TestCase):
    def test_player_collision_blocks_movement(self):
        """Player should not move into a cell occupied by a world object."""
        grid = GridSystem(cell_size=1.0)
        obj = WorldObject(2, 0, width=1, height=1, cell_size=1.0)
        grid.register(obj)
        player = Player(1.4, 0.5, radius=0.6, speed=1.0)
        # Move right by 1 second would result in new_x = 2.4, overlapping occupied cell (2,0)
        player.move(1, 0, 1.0, grid=grid)
        self.assertEqual(player.x, 1.4)  # Blocked, x unchanged

    def test_player_free_movement(self):
        """Player should move freely when no collision."""
        grid = GridSystem(cell_size=1.0)  # No objects registered
        player = Player(0.5, 0.5, radius=0.4, speed=2.0)
        player.move(1, 0, 1.0, grid=grid)
        self.assertEqual(player.x, 2.5)  # Moved 2 units

    def test_collision_respects_circle(self):
        """Collision should consider player radius; moving so circle overlaps occupied cell should block."""
        grid = GridSystem(cell_size=1.0)
        obj = WorldObject(2, 0, width=1, height=1, cell_size=1.0)
        grid.register(obj)
        player = Player(1.2, 0.5, radius=0.3, speed=1.0)
        # new_x = 2.2; circle covers x [1.9, 2.5]; overlaps cell (2,0) in x direction? Yes, 2.2 is within [2,3)
        player.move(1, 0, 1.0, grid=grid)
        self.assertEqual(player.x, 1.2)  # Blocked

    def test_boundary_clamping_after_collision(self):
        """Even if movement blocked, player should still respect world_rect clamping."""
        grid = GridSystem(cell_size=1.0)
        obj = WorldObject(2, 0, width=1, height=1, cell_size=1.0)
        grid.register(obj)
        player = Player(1.4, 0.5, radius=0.6, speed=1.0)
        # Mock world_rect
        class MockRect:
            width = 3.0
            height = 3.0
        player.world_rect = MockRect()
        player.move(1, 0, 1.0, grid=grid)
        self.assertEqual(player.x, 1.4)  # Still blocked, no boundary change

if __name__ == '__main__':
    unittest.main()
