import unittest
from grid_system import GridSystem

class MockObject:
    """A mock world object that occupies a given set of grid cells."""
    def __init__(self, cells):
        self.cells = cells  # list of (gx, gy)

    def get_occupied_cells(self):
        return self.cells

class TestGridSystem(unittest.TestCase):
    def setUp(self):
        self.grid = GridSystem(cell_size=1.0, width=100, height=100)

    def test_world_to_grid(self):
        self.assertEqual(self.grid.world_to_grid(10.4, 20.9), (10, 20))
        self.assertEqual(self.grid.world_to_grid(0.0, 0.0), (0, 0))
        self.assertEqual(self.grid.world_to_grid(-0.5, -1.2), (-1, -2))

    def test_grid_to_world(self):
        self.assertEqual(self.grid.grid_to_world(3, 4), (3.0, 4.0))
        self.assertEqual(self.grid.grid_to_world(0, 0), (0.0, 0.0))

    def test_round_trip(self):
        for x, y in [(5.3, 7.8), (0.1, 128.5), (-3.2, -4.5)]:
            gx, gy = self.grid.world_to_grid(x, y)
            wx, wy = self.grid.grid_to_world(gx, gy)
            # The round-trip gives the top-left corner of the cell, not the original point
            # That's expected; we just check conversion consistency
            self.assertEqual((gx, gy), self.grid.world_to_grid(wx, wy))

    def test_occupancy(self):
        obj = MockObject([(1, 1), (1, 2)])
        self.grid.register(obj)
        self.assertTrue(self.grid.is_occupied(1, 1))
        self.assertTrue(self.grid.is_occupied(1, 2))
        self.assertFalse(self.grid.is_occupied(2, 2))
        self.grid.unregister(obj)
        self.assertFalse(self.grid.is_occupied(1, 1))
        self.assertFalse(self.grid.is_occupied(1, 2))

    def test_get_neighbors(self):
        neighbors = self.grid.get_neighbors(5, 5)
        expected = {(5, 6), (5, 4), (6, 5), (4, 5)}
        self.assertEqual(set(neighbors), expected)

if __name__ == '__main__':
    unittest.main()
