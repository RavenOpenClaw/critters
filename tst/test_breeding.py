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
from constants import MSG_BREED_SUCCESS, MSG_ASSIGN_MATING, MSG_BREED_NEED_TWO, MSG_BREED_NEED_FOOD

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
        self.assertIsNone(offspring.assigned_hut)
        # Position should be center of hut
        expected_x = hut.x + (hut.width * hut.cell_size) / 2
        expected_y = hut.y + (hut.height * hut.cell_size) / 2
        self.assertEqual(offspring.x, expected_x)
        self.assertEqual(offspring.y, expected_y)
        # Offspring should be added to world
        self.assertIn(offspring, added)

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
        self.assertEqual(world.message, MSG_BREED_NEED_TWO)
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
        self.assertEqual(world.message, MSG_BREED_NEED_FOOD.format(5))
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
        self.assertIsNone(offspring.assigned_hut)
        self.assertEqual(world.message, MSG_BREED_SUCCESS)

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
        critter.start_follow(player)  # Properly initiate following
        hut.interact(player)
        self.assertIn(critter, hut.assigned_critters)
        self.assertIs(critter.assigned_hut, hut)
        self.assertIsNone(player.following_critter)
        self.assertEqual(world.message, MSG_ASSIGN_MATING)

    def test_assign_clears_following_even_if_already_assigned(self):
        """Assignment clears following flag even if critter already assigned to this hut."""
        grid = GridSystem(32, 10, 10)
        world = World(grid)
        hut = MatingHut(5, 5, 32)
        world.add_object(hut)
        player = Player(100, 100)
        critter = Critter(0, 0, cell_size=32)
        hut.assign_critter(critter)  # pre-assign
        critter.start_follow(player)  # set following correctly
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
        critter.start_follow(player)  # properly set following
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
