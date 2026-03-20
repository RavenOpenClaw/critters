import unittest
from entity import Entity, Player

class TestEntity(unittest.TestCase):
    def test_entity_initialization(self):
        e = Entity(10, 20, radius=15)
        self.assertEqual(e.x, 10)
        self.assertEqual(e.y, 20)
        self.assertEqual(e.radius, 15)

    def test_entity_default_radius(self):
        e = Entity(0, 0)
        self.assertEqual(e.radius, 20)

class TestPlayer(unittest.TestCase):
    def test_player_attributes(self):
        p = Player(100, 200, radius=25, speed=300)
        self.assertEqual(p.x, 100)
        self.assertEqual(p.y, 200)
        self.assertEqual(p.radius, 25)
        self.assertEqual(p.speed, 300)

    def test_player_defaults(self):
        p = Player(0, 0)
        self.assertEqual(p.radius, 20)
        self.assertEqual(p.speed, 200)

    def test_player_move(self):
        p = Player(0, 0, speed=100)  # 100 units/sec
        # Move right (dx=1, dy=0) for 0.1 seconds -> expected x = 10
        p.move(1, 0, 0.1)
        self.assertAlmostEqual(p.x, 10.0)
        self.assertEqual(p.y, 0)
        # Move down (dx=0, dy=1) for 0.5 seconds -> expected y = 50
        p.move(0, 1, 0.5)
        self.assertAlmostEqual(p.y, 50.0)

    def test_player_interaction_radius_constant(self):
        """7.5: Verify player.interaction_radius equals 2 × player.radius."""
        p = Player(0, 0, radius=20)
        self.assertEqual(p.interaction_radius, 40.0)
        p = Player(0, 0, radius=10)
        self.assertEqual(p.interaction_radius, 20.0)

if __name__ == '__main__':
    unittest.main()
