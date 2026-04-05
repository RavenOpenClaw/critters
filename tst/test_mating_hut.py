"""
Tests for MatingHut class (Task 22).
"""
import unittest
from hypothesis import given, strategies as st
from mating_hut import MatingHut
from critter import Critter

class TestMatingHut(unittest.TestCase):
    def test_mating_hut_dimensions(self):
        """MatingHut has width=2 and height=2."""
        hut = MatingHut(0, 0, cell_size=1.0)
        self.assertEqual(hut.width, 2)
        self.assertEqual(hut.height, 2)

    def test_mating_hut_assigned_critters_list(self):
        """MatingHut starts with empty assigned_critters list."""
        hut = MatingHut(0, 0, cell_size=1.0)
        self.assertEqual(hut.assigned_critters, [])

    def test_mating_hut_cost_attribute(self):
        """MatingHut has correct building cost."""
        hut = MatingHut(0, 0, cell_size=1.0)
        self.assertEqual(hut.cost, {"wood": 15, "stone": 10})

class TestMatingHutAssignment(unittest.TestCase):
    """Assignment behavior for MatingHut."""

    def test_assign_critter_establishes_home_reference(self):
        """Assigning a critter sets hut reference on critter and adds to hut's list."""
        hut = MatingHut(0, 0, cell_size=32)
        critter = Critter(100, 100, cell_size=32)
        hut.assign_critter(critter)
        self.assertIn(critter, hut.assigned_critters)
        self.assertIs(critter.assigned_hut, hut)

    @given(n=st.integers(min_value=1, max_value=100))
    def test_mating_hut_unbounded_assignment(self, n):
        """Mating Hut can have any number of critters assigned."""
        hut = MatingHut(0, 0, cell_size=32)
        critters = [Critter(i*10, i*10, cell_size=32) for i in range(n)]
        for c in critters:
            hut.assign_critter(c)
        self.assertEqual(len(hut.assigned_critters), n)
        for c in critters:
            self.assertIs(c.assigned_hut, hut)

if __name__ == '__main__':
    unittest.main()
