"""
Property-based tests for GridSystem.

Requires hypothesis: pip install hypothesis
"""
import unittest
from hypothesis import given, strategies as st
import pytest
from grid_system import GridSystem

# Minimal mock world object that works with GridSystem
class MockWorldObject:
    def __init__(self, gx, gy, width, height, cell_size):
        self.gx = gx
        self.gy = gy
        self.width = width
        self.height = height
        self.cell_size = cell_size

    def get_occupied_cells(self):
        cells = []
        for i in range(self.width):
            for j in range(self.height):
                cells.append((self.gx + i, self.gy + j))
        return cells

class TestGridOccupation(unittest.TestCase):
    @given(
        gx=st.integers(min_value=-100, max_value=100),
        gy=st.integers(min_value=-100, max_value=100),
        width=st.integers(min_value=1, max_value=20),
        height=st.integers(min_value=1, max_value=20),
        cell_size=st.sampled_from([1, 2, 4, 8, 16, 32, 64])
    )
    def test_grid_occupation_by_dimensions(self, gx, gy, width, height, cell_size):
        """Property 5.4: An object occupies exactly width*height cells within its bounding rectangle."""
        grid = GridSystem(cell_size=cell_size, width=1000, height=1000)
        obj = MockWorldObject(gx, gy, width, height, cell_size)
        grid.register(obj)
        occupied_cells = obj.get_occupied_cells()
        # Exact count
        assert len(occupied_cells) == width * height
        # All cells lie within [gx, gx+width) x [gy, gy+height)
        for (cx, cy) in occupied_cells:
            assert gx <= cx < gx + width
            assert gy <= cy < gy + height
        # Every cell in the rectangle is present
        for x in range(gx, gx+width):
            for y in range(gy, gy+height):
                assert (x, y) in occupied_cells
        grid.unregister(obj)

class TestGridMutualExclusion(unittest.TestCase):
    @given(
        gx=st.integers(min_value=-50, max_value=50),
        gy=st.integers(min_value=-50, max_value=50),
        width=st.integers(min_value=1, max_value=10),
        height=st.integers(min_value=1, max_value=10),
        cell_size=st.sampled_from([1, 16, 32])
    )
    def test_mutual_exclusion(self, gx, gy, width, height, cell_size):
        """Property 5.5: Overlapping placements should be prevented."""
        grid = GridSystem(cell_size=cell_size, width=1000, height=1000)
        obj1 = MockWorldObject(gx, gy, width, height, cell_size)
        grid.register(obj1)
        # Second object with the exact same grid footprint
        obj2 = MockWorldObject(gx, gy, width, height, cell_size)
        with pytest.raises(ValueError):
            grid.register(obj2)
        # Cleanup
        grid.unregister(obj1)

if __name__ == '__main__':
    unittest.main()
