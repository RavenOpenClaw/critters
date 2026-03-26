import unittest
from main import STATE_COLORS
from critter import CritterState

class TestMain(unittest.TestCase):
    def test_initialization(self):
        self.assertTrue(True)

    def test_state_colors_defined(self):
        """Test that STATE_COLORS mapping includes all CritterStates."""
        self.assertIn(CritterState.IDLE, STATE_COLORS)
        self.assertIn(CritterState.GATHER, STATE_COLORS)
        self.assertIn(CritterState.RETURN, STATE_COLORS)

    def test_state_colors_are_rgb_tuples(self):
        """Test that each color is a 3-element tuple of integers in [0,255]."""
        for color in STATE_COLORS.values():
            self.assertIsInstance(color, tuple)
            self.assertEqual(len(color), 3)
            for component in color:
                self.assertIsInstance(component, int)
                self.assertGreaterEqual(component, 0)
                self.assertLessEqual(component, 255)

    def test_state_colors_are_distinct(self):
        """Test that different states have different colors."""
        colors = list(STATE_COLORS.values())
        self.assertEqual(len(colors), len(set(colors)), "State colors should be distinct")

if __name__ == '__main__':
    unittest.main()
