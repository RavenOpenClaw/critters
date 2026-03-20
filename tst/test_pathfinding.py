"""
Tests for PathfindingSystem (Task 13).
"""
import unittest
from grid_system import GridSystem
from pathfinding import PathfindingSystem

class TestPathfinding(unittest.TestCase):
    def setUp(self):
        self.grid = GridSystem(cell_size=1.0)
        self.pathfinder = PathfindingSystem()

    def test_pathfinding_no_obstacles(self):
        """13.3: Find path with no obstacles returns direct Manhattan path."""
        path = self.pathfinder.find_path((0, 0), (3, 0), self.grid)
        self.assertIsNotNone(path)
        self.assertEqual(path, [(0, 0), (1, 0), (2, 0), (3, 0)])

    def test_pathfinding_around_obstacle(self):
        """13.3: Find path around a single blocking cell."""
        # Block the direct horizontal path at (2,0) and (2,1) alternative maybe
        self.grid.occupied[(2, 0)] = None  # obstacle
        # Start (0,0) to (3,0) must go up and over: (0,0)->(0,1)->(1,1)->(2,1)->(3,1)->(3,0)
        path = self.pathfinder.find_path((0, 0), (3, 0), self.grid)
        self.assertIsNotNone(path)
        # The path should go around: one possible route is (0,0)->(1,0) is blocked? Actually (1,0) is free, but (2,0) blocked, so A* may try (1,0)->(2,0) blocked then go up from (1,0). Let's not rely on exact path. But we can verify path length is longer than Manhattan (4) because detour.
        self.assertNotEqual(path, [(0, 0), (1, 0), (2, 0), (3, 0)])
        # Verify that no step goes through occupied cell (2,0)
        for gx, gy in path:
            self.assertFalse((gx, gy) in self.grid.occupied and (gx, gy) != (0,0) and (gx, gy) != (3,0) and self.grid.occupied[(gx, gy)] is not None, f"Path steps on occupied cell {(gx, gy)}")
        # More simply ensure all cells in path are not occupied
        for cell in path:
            self.assertFalse(self.grid.is_occupied(*cell) and cell != (0,0) and cell != (3,0))
        # Actually better: just ensure each cell is not occupied (except maybe start/goal? They are checked before so they shouldn't be occupied anyway)
        for cell in path:
            self.assertNotIn(cell, self.grid.occupied)

    def test_pathfinding_no_path(self):
        """13.3: No path exists when goal is surrounded by obstacles."""
        # Enclose start at (0,0) with obstacles on its neighbors, but actually start is free; goal at (2,2) unreachable.
        # Simpler: block all paths to goal
        self.grid.occupied[(1, 0)] = None
        self.grid.occupied[(0, 1)] = None
        self.grid.occupied[(1, 2)] = None
        self.grid.occupied[(2, 1)] = None
        # Start (0,0) to (2,2) – only two possible Manhattan routes blocked.
        # Actually need to ensure no path: place a solid barrier.
        # Simpler: surround goal completely
        goal = (2, 2)
        for nx, ny in self.grid.get_neighbors(*goal):
            self.grid.occupied[(nx, ny)] = None
        # But ensure goal itself is not occupied
        path = self.pathfinder.find_path((0, 0), goal, self.grid)
        self.assertIsNone(path)

    def test_path_cache(self):
        """13.2: Path caching returns same object for identical queries and invalidate clears."""
        start = (0, 0)
        goal = (2, 0)
        path1 = self.pathfinder.find_path(start, goal, self.grid)
        path2 = self.pathfinder.find_path(start, goal, self.grid)
        self.assertIs(path1, path2)  # same cached object
        self.pathfinder.invalidate_cache()
        path3 = self.pathfinder.find_path(start, goal, self.grid)
        self.assertIsNot(path1, path3)  # new object (different list)
        self.assertEqual(path1, path3)

    def test_pathfinding_start_occupied_returns_none(self):
        """Start occupied should return None."""
        start = (1, 1)
        self.grid.occupied[start] = None
        path = self.pathfinder.find_path(start, (2, 2), self.grid)
        self.assertIsNone(path)

    def test_pathfinding_goal_occupied_returns_none(self):
        """Goal occupied should return None."""
        goal = (1, 1)
        self.grid.occupied[goal] = None
        path = self.pathfinder.find_path((0, 0), goal, self.grid)
        self.assertIsNone(path)

if __name__ == '__main__':
    unittest.main()
