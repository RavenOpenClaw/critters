"""
Property-based tests for critter breeding (Task 23).
"""
import unittest
from hypothesis import given, strategies as st
import random
from unittest.mock import patch
from mating_hut import MatingHut
from critter import Critter, CritterState
from grid_system import GridSystem
from world import World
from entity import Player

class TestBreeding(unittest.TestCase):
    def test_breed_requires_two_critters(self):
        """Breeding with fewer than two assigned critters returns None."""
        hut = MatingHut(0, 0, cell_size=32)
        world = type('World', (), {'add_object': lambda self, obj: None})  # Dummy world
        # With 0 or 1 critters, breed should return None
        result = hut.breed(world)
        self.assertIsNone(result)
        critter1 = Critter(100, 100, cell_size=32)
        hut.assign_critter(critter1)
        result = hut.breed(world)
        self.assertIsNone(result)

    def test_breed_creates_offspring_at_hut_center(self):
        """Offspring is placed exactly at the hut's center and in IDLE state."""
        hut = MatingHut(10, 20, cell_size=32)
        # Add two critters
        c1 = Critter(0, 0, cell_size=32)
        c2 = Critter(100, 100, cell_size=32)
        hut.assign_critter(c1)
        hut.assign_critter(c2)

        # Track added objects
        added = []
        class DummyWorld:
            def add_object(self, obj):
                added.append(obj)

        world = DummyWorld()
        # Control randomness to avoid mutation affecting test's deterministic placement
        with patch('random.randint', return_value=0):
            offspring = hut.breed(world)

        self.assertIsNotNone(offspring)
        self.assertEqual(offspring.state, CritterState.IDLE)
        self.assertIs(offspring.assigned_hut, hut)
        # Position should be center of hut
        expected_x = hut.x + (hut.width * hut.cell_size) / 2
        expected_y = hut.y + (hut.height * hut.cell_size) / 2
        self.assertEqual(offspring.x, expected_x)
        self.assertEqual(offspring.y, expected_y)
        # Offspring should be added to world
        self.assertIn(offspring, added)

    def test_offspring_stats_are_parent_average_plus_mutation(self):
        """Offspring stats equal (parent1+parent2)/2 rounded plus ±5 mutation."""
        hut = MatingHut(0, 0, cell_size=32)
        c1 = Critter(0, 0, cell_size=32, strength=50, speed_stat=60, endurance=70)
        c2 = Critter(0, 0, cell_size=32, strength=80, speed_stat=90, endurance=100)
        hut.assign_critter(c1)
        hut.assign_critter(c2)

        class DummyWorld:
            def add_object(self, obj): pass
        world = DummyWorld()

        # Test with various mutation values
        for mutation in [-5, 0, 5]:
            with patch('random.randint', return_value=mutation):
                offspring = hut.breed(world)
                # Compute expected: average = (p1+p2)/2, rounded, plus mutation, clamped
                exp_str = round((50+80)/2) + mutation
                exp_spd = round((60+90)/2) + mutation
                exp_end = round((70+100)/2) + mutation
                # Clamp to [1,100] for expected too
                exp_str = max(1, min(100, exp_str))
                exp_spd = max(1, min(100, exp_spd))
                exp_end = max(1, min(100, exp_end))
                self.assertEqual(offspring.strength, exp_str)
                self.assertEqual(offspring.speed_stat, exp_spd)
                self.assertEqual(offspring.endurance, exp_end)

    @given(
        s1=st.integers(min_value=1, max_value=100),
        s2=st.integers(min_value=1, max_value=100),
        sp1=st.integers(min_value=1, max_value=100),
        sp2=st.integers(min_value=1, max_value=100),
        e1=st.integers(min_value=1, max_value=100),
        e2=st.integers(min_value=1, max_value=100)
    )
    def test_offspring_stats_always_within_bounds(self, s1, s2, sp1, sp2, e1, e2):
        """Property 28: Offspring stats are always within [1, 100] regardless of parent stats and mutation."""
        hut = MatingHut(0, 0, cell_size=32)
        c1 = Critter(0, 0, cell_size=32, strength=s1, speed_stat=sp1, endurance=e1)
        c2 = Critter(0, 0, cell_size=32, strength=s2, speed_stat=sp2, endurance=e2)
        hut.assign_critter(c1)
        hut.assign_critter(c2)

        class DummyWorld:
            def add_object(self, obj): pass
        world = DummyWorld()

        # For many random mutation values (just call breed - randomness will vary)
        # We'll call breed multiple times to cover different mutations indirectly? But one call yields one mutation.
        # Instead, we can directly compute range: The breed method clamps, so any result must be within [1,100].
        # So just call breed once and assert bounds. This will always pass because of clamp.
        offspring = hut.breed(world)
        self.assertIsNotNone(offspring)
        self.assertTrue(1 <= offspring.strength <= 100)
        self.assertTrue(1 <= offspring.speed_stat <= 100)
        self.assertTrue(1 <= offspring.endurance <= 100)

    @given(
        gx=st.integers(min_value=-100, max_value=100),
        gy=st.integers(min_value=-100, max_value=100),
        width=st.integers(min_value=1, max_value=10),
        height=st.integers(min_value=1, max_value=10),
        cell_size=st.floats(min_value=1.0, max_value=100.0)
    )
    def test_offspring_position_is_hut_center(self, gx, gy, width, height, cell_size):
        """Property 29: Offspring spawns at the exact center of the MatingHut."""
        hut = MatingHut(gx, gy, cell_size=cell_size)
        hut.width = width
        hut.height = height
        # Ensure objects are placeable: for test we ignore world constraints, just compute position.
        c1 = Critter(0, 0, cell_size=cell_size)
        c2 = Critter(10, 10, cell_size=cell_size)
        hut.assign_critter(c1)
        hut.assign_critter(c2)

        class DummyWorld:
            def add_object(self, obj): pass
        world = DummyWorld()

        with patch('random.randint', return_value=0):
            offspring = hut.breed(world)
        expected_x = hut.x + (width * cell_size) / 2
        expected_y = hut.y + (height * cell_size) / 2
        self.assertEqual(offspring.x, expected_x)
        self.assertEqual(offspring.y, expected_y)

class TestMatingHutInteraction(unittest.TestCase):
    def test_interact_requires_two_critters(self):
        grid = GridSystem(32, 10, 10)
        world = World(grid)
        hut = MatingHut(5, 5, 32)
        world.add_object(hut)
        player = Player(100, 100)
        player.inventory.add("food", 10)
        critter = Critter(0, 0, cell_size=32)
        hut.assign_critter(critter)
        hut.interact(player)
        self.assertEqual(len(world.current_map.objects), 1)
        self.assertEqual(world.message, "Need at least 2 critters to breed!")
        self.assertEqual(player.inventory.get_item_count("food"), 10)

    def test_interact_requires_food(self):
        grid = GridSystem(32, 10, 10)
        world = World(grid)
        hut = MatingHut(5, 5, 32)
        world.add_object(hut)
        player = Player(100, 100)
        player.inventory.add("food", 3)
        c1 = Critter(0, 0, cell_size=32)
        c2 = Critter(10, 10, cell_size=32)
        hut.assign_critter(c1)
        hut.assign_critter(c2)
        hut.interact(player)
        self.assertEqual(len(world.current_map.objects), 1)
        self.assertEqual(world.message, "Need 5 food to breed!")
        self.assertEqual(player.inventory.get_item_count("food"), 3)

    def test_interact_breeds_successfully(self):
        grid = GridSystem(32, 10, 10)
        world = World(grid)
        hut = MatingHut(5, 5, 32)
        world.add_object(hut)
        player = Player(100, 100)
        player.inventory.add("food", 10)
        c1 = Critter(0, 0, cell_size=32, strength=50, speed_stat=50, endurance=50)
        c2 = Critter(10, 10, cell_size=32, strength=70, speed_stat=70, endurance=70)
        hut.assign_critter(c1)
        hut.assign_critter(c2)
        with patch('random.randint', return_value=0):
            hut.interact(player)
        self.assertEqual(player.inventory.get_item_count("food"), 5)
        self.assertEqual(len(world.current_map.objects), 2)
        offspring = world.current_map.objects[1]
        self.assertIsInstance(offspring, Critter)
        self.assertIs(offspring.assigned_hut, hut)
        self.assertEqual(world.message, "Breeding produced a new critter!")

    def test_interact_ignores_non_player(self):
        hut = MatingHut(0, 0, 32)
        try:
            hut.interact("not a player")
        except Exception as e:
            self.fail(f"interact raised an exception with non-player: {e}")

class TestMatingHutAssignmentViaInteract(unittest.TestCase):
    def test_assigns_following_critter(self):
        """MatingHut.interact assigns player's following critter when present."""
        grid = GridSystem(32, 10, 10)
        world = World(grid)
        hut = MatingHut(5, 5, 32)
        world.add_object(hut)
        player = Player(100, 100)
        critter = Critter(0, 0, cell_size=32)
        player.following_critter = critter
        hut.interact(player)
        self.assertIn(critter, hut.assigned_critters)
        self.assertIs(critter.assigned_hut, hut)
        self.assertIsNone(player.following_critter)
        self.assertEqual(world.message, "Critter assigned to Mating Hut.")

    def test_assign_clears_following_even_if_already_assigned(self):
        """Assignment clears following flag even if critter already assigned to this hut."""
        grid = GridSystem(32, 10, 10)
        world = World(grid)
        hut = MatingHut(5, 5, 32)
        world.add_object(hut)
        player = Player(100, 100)
        critter = Critter(0, 0, cell_size=32)
        hut.assign_critter(critter)  # pre-assign
        player.following_critter = critter
        hut.interact(player)
        self.assertIn(critter, hut.assigned_critters)
        self.assertIsNone(player.following_critter)

    def test_assign_unassigns_from_previous_hut(self):
        """Assigning a following critter to this hut unassigns it from any other hut."""
        grid = GridSystem(32, 10, 10)
        world = World(grid)
        hut1 = MatingHut(5, 5, 32)
        hut2 = MatingHut(15, 15, 32)
        world.add_object(hut1)
        world.add_object(hut2)
        player = Player(100, 100)
        critter = Critter(0, 0, cell_size=32)
        hut1.assign_critter(critter)
        self.assertIn(critter, hut1.assigned_critters)
        self.assertIs(critter.assigned_hut, hut1)
        player.following_critter = critter
        hut2.interact(player)
        self.assertNotIn(critter, hut1.assigned_critters)
        self.assertIn(critter, hut2.assigned_critters)
        self.assertIs(critter.assigned_hut, hut2)
        self.assertIsNone(player.following_critter)

    def test_assign_does_not_assign_non_player(self):
        hut = MatingHut(0, 0, 32)
        try:
            hut.interact("not a player")
        except Exception as e:
            self.fail(f"interact raised an exception with non-player: {e}")

if __name__ == '__main__':
    unittest.main()
