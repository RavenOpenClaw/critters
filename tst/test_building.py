"""
Tests for Building and GatheringHut classes.
"""
import unittest
from hypothesis import given, strategies as st
from inventory import Inventory
from building import Building
from gathering_hut import GatheringHut
from grid_system import GridSystem
from world import World
from build_menu import BuildMenu
from entity import Player
from critter import Critter

class TestBuilding(unittest.TestCase):
    def test_can_place_with_sufficient_resources(self):
        """Building.can_place returns True when player has all required resources."""
        cost = {'wood': 5, 'stone': 3}
        building = Building(0, 0, width=2, height=2, cell_size=1.0, cost=cost)
        player_inv = Inventory()
        player_inv.add('wood', 10)
        player_inv.add('stone', 10)
        self.assertTrue(building.can_place(player_inv))

    def test_can_place_with_insufficient_one_resource(self):
        """Building.can_place returns False when any resource is insufficient."""
        cost = {'wood': 5, 'stone': 3}
        building = Building(0, 0, width=2, height=2, cell_size=1.0, cost=cost)
        player_inv = Inventory()
        player_inv.add('wood', 10)
        player_inv.add('stone', 2)  # Not enough stone
        self.assertFalse(building.can_place(player_inv))

    def test_can_place_with_missing_resource(self):
        """Building.can_place returns False when a required resource is absent."""
        cost = {'wood': 5, 'stone': 3}
        building = Building(0, 0, width=2, height=2, cell_size=1.0, cost=cost)
        player_inv = Inventory()
        player_inv.add('wood', 10)
        # No stone added
        self.assertFalse(building.can_place(player_inv))

    def test_building_cost_attribute(self):
        """Building stores cost dict correctly."""
        cost = {'wood': 5}
        building = Building(0, 0, width=2, height=2, cell_size=1.0, cost=cost)
        self.assertEqual(building.cost, cost)

class TestBuildingPlacement(unittest.TestCase):
    @given(
        wood=st.integers(min_value=5, max_value=20),
        stone=st.integers(min_value=3, max_value=20)
    )
    def test_placement_deducts_resources(self, wood, stone):
        """Property 9.5: Placing a building deducts exactly its cost from player inventory."""
        cell_size = 1.0
        grid = GridSystem(cell_size=cell_size)
        world = World(grid)
        # Define a test building class with fixed cost and size (1x1) that matches BuildMenu signature
        class TestBuilding(Building):
            def __init__(self, gx, gy, cell_size):
                super().__init__(gx, gy, width=1, height=1, cell_size=cell_size, cost={'wood': 5, 'stone': 3})
            def render(self, screen):
                pass  # No rendering needed for test
        # Build menu with this building selected
        menu = BuildMenu(cell_size)
        menu.selected_building_class = TestBuilding
        menu.visible = True
        # Player with given resources
        player = Player(0, 0, radius=20)
        player.inventory.add('wood', wood)
        player.inventory.add('stone', stone)
        starting_wood = player.inventory.get_item_count('wood')
        starting_stone = player.inventory.get_item_count('stone')
        # Attempt placement at grid (10, 10) – empty area
        success = menu.attempt_placement(player, world, grid, 10, 10)
        self.assertTrue(success, "Placement should succeed with sufficient resources")
        # Verify deduction
        self.assertEqual(player.inventory.get_item_count('wood'), starting_wood - 5)
        self.assertEqual(player.inventory.get_item_count('stone'), starting_stone - 3)

class TestGatheringHut(unittest.TestCase):
    def test_gathering_hut_dimensions(self):
        """9.6: GatheringHut has width=3, height=3."""
        hut = GatheringHut(0, 0, cell_size=1.0)
        self.assertEqual(hut.width, 3)
        self.assertEqual(hut.height, 3)

    def test_gathering_hut_storage_inventory(self):
        """GatheringHut initializes with empty storage inventory."""
        hut = GatheringHut(0, 0, cell_size=1.0)
        self.assertEqual(hut.storage.get_item_count('berry'), 0)

    def test_gathering_hut_assigned_critters_list(self):
        """GatheringHut starts with empty assigned_critters list."""
        hut = GatheringHut(0, 0, cell_size=1.0)
        self.assertEqual(hut.assigned_critters, [])

    def test_gathering_hut_gathering_radius(self):
        """GatheringHut gathering_radius equals 10.0 * cell_size."""
        hut = GatheringHut(0, 0, cell_size=32.0)
        self.assertEqual(hut.gathering_radius, 320.0)

class TestCritterAssignment(unittest.TestCase):
    """Tests for Task 12: Critter assignment to Gathering Hut."""

    def test_assign_critter_establishes_home_reference(self):
        """Property 10: Assigning a critter sets hut reference on critter and adds to hut's list."""
        hut = GatheringHut(0, 0, cell_size=32)
        critter = Critter(100, 100, cell_size=32)
        hut.assign_critter(critter)
        self.assertIn(critter, hut.assigned_critters)
        self.assertIs(critter.assigned_hut, hut)

    @given(n=st.integers(min_value=1, max_value=100))
    def test_gathering_hut_unbounded_assignment(self, n):
        """Property 11: Gathering Hut can have any number of critters assigned."""
        hut = GatheringHut(0, 0, cell_size=32)
        critters = [Critter(i*10, i*10, cell_size=32) for i in range(n)]
        for c in critters:
            hut.assign_critter(c)
        self.assertEqual(len(hut.assigned_critters), n)
        for c in critters:
            self.assertIs(c.assigned_hut, hut)

if __name__ == '__main__':
    unittest.main()
