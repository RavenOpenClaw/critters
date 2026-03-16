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

    def test_sliding_along_obstacle(self):
        """When moving diagonally into an obstacle, player should slide along it (one axis blocked, other free)."""
        grid = GridSystem(cell_size=1.0)
        obj = WorldObject(2, 0, width=1, height=1, cell_size=1.0)
        grid.register(obj)
        player = Player(1.3, 0.5, radius=0.6, speed=1.0)
        # Move diagonally: dx=1 (right), dy=1 (down)
        player.move(1, 1, 1.0, grid=grid)
        # X is blocked by obstacle; Y is free because with x=1.3 the player does not overlap the obstacle at new_y=1.5
        self.assertEqual(player.x, 1.3)  # X blocked
        self.assertEqual(player.y, 1.5)  # Y moved freely

    def test_sliding_preserves_other_axis_when_one_blocked(self):
        """If Y movement would collide after X movement, Y should be blocked and X preserved."""
        grid = GridSystem(cell_size=1.0)
        # Place obstacle directly below the one we had, creating a corner
        obj1 = WorldObject(2, 0, width=1, height=1, cell_size=1.0)
        obj2 = WorldObject(2, 1, width=1, height=1, cell_size=1.0)
        grid.register(obj1)
        grid.register(obj2)
        player = Player(1.3, 0.5, radius=0.6, speed=1.0)
        # Move diagonally down-right: both axes individually would collide with obstacles at (2,0) and (2,1)
        player.move(1, 1, 1.0, grid=grid)
        self.assertEqual(player.x, 1.3)  # X blocked by wall at x=2
        self.assertEqual(player.y, 0.5)  # Y also blocked because moving down would touch obstacle at (2,1)

if __name__ == '__main__':
    unittest.main()
