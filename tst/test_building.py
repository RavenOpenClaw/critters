"""
Tests for Building and GatheringHut classes.
"""
import unittest
from hypothesis import given, strategies as st
from inventory import Inventory
from building import Building
from gathering_hut import GatheringHut
from chair import Chair
from campfire import Campfire
from mating_hut import MatingHut
from grid_system import GridSystem
from world import World
from build_menu import BuildMenu
from entity import Player
from critter import Critter
from constants import ITEM_WOOD, ITEM_STONE

class TestBuilding(unittest.TestCase):
    def test_building_base_find_resource_in_radius_returns_none(self):
        """Base Building.find_resource_in_radius returns None; subclasses should override."""
        cell_size = 32
        building = Building(0, 0, width=1, height=1, cell_size=cell_size, cost={})
        grid = GridSystem(cell_size, 10, 10)
        world = World(grid)
        critter = Critter(50, 50, cell_size=cell_size)
        result = building.find_resource_in_radius(world, critter)
        self.assertIsNone(result)

    def test_can_place_with_insufficient_one_resource(self):
        """Building.can_place returns False when any resource is insufficient."""
        cost = {ITEM_WOOD: 5, 'stone': 3}
        building = Building(0, 0, width=2, height=2, cell_size=1.0, cost=cost)
        player_inv = Inventory()
        player_inv.add(ITEM_WOOD, 10)
        player_inv.add('stone', 2)  # Not enough stone
        self.assertFalse(building.can_place(player_inv))

    def test_can_place_with_missing_resource(self):
        """Building.can_place returns False when a required resource is absent."""
        cost = {ITEM_WOOD: 5, 'stone': 3}
        building = Building(0, 0, width=2, height=2, cell_size=1.0, cost=cost)
        player_inv = Inventory()
        player_inv.add(ITEM_WOOD, 10)
        # No stone added
        self.assertFalse(building.can_place(player_inv))

    def test_building_cost_attribute(self):
        """Building stores cost dict correctly."""
        cost = {ITEM_WOOD: 5}
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
        grid = GridSystem(cell_size=cell_size, width=20, height=20)
        world = World(grid)
        # Define a test building class with fixed cost and size (1x1) that matches BuildMenu signature
        class TestBuilding(Building):
            cost = {ITEM_WOOD: 5, 'stone': 3}
            def __init__(self, gx, gy, cell_size):
                super().__init__(gx, gy, width=1, height=1, cell_size=cell_size, cost=self.cost)
            def render(self, screen):
                pass  # No rendering needed for test
        # Build menu with this building selected
        menu = BuildMenu(cell_size)
        menu.selected_building_class = TestBuilding
        menu.visible = True
        # Player with given resources
        player = Player(0, 0, radius=20)
        player.inventory.add(ITEM_WOOD, wood)
        player.inventory.add('stone', stone)
        starting_wood = player.inventory.get_item_count(ITEM_WOOD)
        starting_stone = player.inventory.get_item_count('stone')
        # Attempt placement at grid (10, 10) – empty area
        success = menu.attempt_placement(player, world, grid, 10, 10)
        self.assertTrue(success, "Placement should succeed with sufficient resources")
        # Verify deduction
        self.assertEqual(player.inventory.get_item_count(ITEM_WOOD), starting_wood - 5)
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
        """GatheringHut gathering_radius equals 20.0 * cell_size."""
        hut = GatheringHut(0, 0, cell_size=32.0)
        self.assertEqual(hut.gathering_radius, 640.0)

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

class TestBuildingCosts(unittest.TestCase):
    """Tests for Task 40: Building costs enforcement."""

    def test_gathering_hut_cost(self):
        """GatheringHut has correct cost."""
        hut = GatheringHut(0, 0, cell_size=32)
        self.assertEqual(hut.cost, {ITEM_WOOD: 10, ITEM_STONE: 5})

    def test_chair_cost(self):
        """Chair has correct cost."""
        chair = Chair(0, 0, cell_size=32)
        self.assertEqual(chair.cost, {ITEM_WOOD: 4})

    def test_campfire_cost(self):
        """Campfire has correct cost."""
        cf = Campfire(0, 0, cell_size=32)
        self.assertEqual(cf.cost, {ITEM_WOOD: 2, ITEM_STONE: 2})

    def test_mating_hut_cost(self):
        """MatingHut has correct cost."""
        mh = MatingHut(0, 0, cell_size=32)
        self.assertEqual(mh.cost, {ITEM_WOOD: 15, ITEM_STONE: 10})

    def test_gathering_hut_placement_deducts_cost(self):
        """Placing a GatheringHut deducts exact cost from player inventory."""
        cell_size = 32
        grid = GridSystem(cell_size=cell_size, width=20, height=20)
        world = World(grid)
        menu = BuildMenu(cell_size)
        menu.selected_building_class = GatheringHut
        menu.visible = True
        player = Player(0, 0, radius=20)
        player.inventory.add(ITEM_WOOD, 100)
        player.inventory.add(ITEM_STONE, 100)
        start_wood = player.inventory.get_item_count(ITEM_WOOD)
        start_stone = player.inventory.get_item_count(ITEM_STONE)
        success = menu.attempt_placement(player, world, grid, 5, 5)
        self.assertTrue(success, "Placement should succeed with sufficient resources")
        self.assertEqual(player.inventory.get_item_count(ITEM_WOOD), start_wood - 10)
        self.assertEqual(player.inventory.get_item_count(ITEM_STONE), start_stone - 5)

    def test_gathering_hut_placement_fails_without_resources(self):
        """Placement fails when resources insufficient and deducts nothing."""
        cell_size = 32
        grid = GridSystem(cell_size=cell_size, width=20, height=20)
        world = World(grid)
        menu = BuildMenu(cell_size)
        menu.selected_building_class = GatheringHut
        menu.visible = True
        player = Player(0, 0, radius=20)
        player.inventory.add(ITEM_WOOD, 5)  # not enough wood (need 10)
        player.inventory.add(ITEM_STONE, 10)
        start_wood = player.inventory.get_item_count(ITEM_WOOD)
        start_stone = player.inventory.get_item_count(ITEM_STONE)
        success = menu.attempt_placement(player, world, grid, 5, 5)
        self.assertFalse(success, "Placement should fail with insufficient resources")
        self.assertEqual(player.inventory.get_item_count(ITEM_WOOD), start_wood)
        self.assertEqual(player.inventory.get_item_count(ITEM_STONE), start_stone)

    def test_chair_placement_deducts_cost(self):
        """Placing a Chair deducts its wood cost."""
        cell_size = 32
        grid = GridSystem(cell_size=cell_size, width=20, height=20)
        world = World(grid)
        menu = BuildMenu(cell_size)
        menu.selected_building_class = Chair
        menu.visible = True
        player = Player(0, 0, radius=20)
        player.inventory.add(ITEM_WOOD, 50)
        start_wood = player.inventory.get_item_count(ITEM_WOOD)
        success = menu.attempt_placement(player, world, grid, 2, 2)
        self.assertTrue(success)
        self.assertEqual(player.inventory.get_item_count(ITEM_WOOD), start_wood - 4)

    def test_campfire_placement_deducts_cost(self):
        """Placing a Campfire deducts wood and stone."""
        cell_size = 32
        grid = GridSystem(cell_size=cell_size, width=20, height=20)
        world = World(grid)
        menu = BuildMenu(cell_size)
        menu.selected_building_class = Campfire
        menu.visible = True
        player = Player(0, 0, radius=20)
        player.inventory.add(ITEM_WOOD, 50)
        player.inventory.add(ITEM_STONE, 50)
        start_wood = player.inventory.get_item_count(ITEM_WOOD)
        start_stone = player.inventory.get_item_count(ITEM_STONE)
        success = menu.attempt_placement(player, world, grid, 3, 3)
        self.assertTrue(success)
        self.assertEqual(player.inventory.get_item_count(ITEM_WOOD), start_wood - 2)
        self.assertEqual(player.inventory.get_item_count(ITEM_STONE), start_stone - 2)

    def test_mating_hut_placement_deducts_cost(self):
        """Placing a MatingHut deducts its cost."""
        cell_size = 32
        grid = GridSystem(cell_size=cell_size, width=20, height=20)
        world = World(grid)
        menu = BuildMenu(cell_size)
        menu.selected_building_class = MatingHut
        menu.visible = True
        player = Player(0, 0, radius=20)
        player.inventory.add(ITEM_WOOD, 100)
        player.inventory.add(ITEM_STONE, 100)
        start_wood = player.inventory.get_item_count(ITEM_WOOD)
        start_stone = player.inventory.get_item_count(ITEM_STONE)
        success = menu.attempt_placement(player, world, grid, 4, 4)
        self.assertTrue(success)
        self.assertEqual(player.inventory.get_item_count(ITEM_WOOD), start_wood - 15)
        self.assertEqual(player.inventory.get_item_count(ITEM_STONE), start_stone - 10)


if __name__ == '__main__':
    unittest.main()
