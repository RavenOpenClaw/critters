"""
Property tests for multi-map world system (Task 30).
"""
import unittest
from hypothesis import given, strategies as st
from entity import Player
from world import World
from map_data import MapData
from berry_bush import BerryBush

class TestMultiMap(unittest.TestCase):
    def setUp(self):
        # Create two adjacent maps: map_a (left) and map_b (right)
        cell_size = 32
        self.map_a = MapData(name="map_a", width=10, height=10, cell_size=cell_size)
        self.map_b = MapData(name="map_b", width=10, height=10, cell_size=cell_size)
        # Connect map_a east to map_b, and map_b west to map_a
        self.map_a.neighbors = {'east': 'map_b'}
        self.map_b.neighbors = {'west': 'map_a'}
        # Create world starting at map_a
        self.world = World(self.map_a)
        # Register map_b in world's maps dict
        self.world.add_map(self.map_b)
        self.player = Player(0, 0, speed=0)  # stationary for test

    def test_map_transition_at_boundary(self):
        """Property 35: Crossing boundary to a neighbor map changes current_map."""
        # Position player at the far right edge of map_a (grid x >= width) to trigger east transition
        # Use grid coordinate exactly at width (which is out of bounds)
        self.player.x = self.world.current_map.cell_size * self.world.current_map.width  # just outside
        self.player.y = self.world.current_map.cell_size * 5  # middle vertically
        self.world.handle_map_transition(self.player)
        self.assertEqual(self.world.current_map.name, 'map_b')
        # Player should now be at west edge of map_b (x coordinate within map_b)
        expected_gx = 0
        expected_gy = 5  # same relative gy or clamped within height
        # The method set player.x,y based on neighbor's cell positions; check within map_b bounds
        gx, gy = self.world.grid.world_to_grid(self.player.x, self.player.y)
        self.assertEqual(gx, expected_gx)
        # gy should be 5 (since within vertical bounds)
        self.assertEqual(gy, expected_gy)

    def test_inactive_map_entity_preservation(self):
        """Property 36: Entities on non-current maps retain their state."""
        # Place a BerryBush on map_a (current map) and mutate it (deplete some food)
        bush_a = BerryBush(5, 5, cell_size=32, berries=5)
        self.world.add_object(bush_a)
        # Deplete it partially
        self.assertEqual(bush_a.inventory.get_item_count('food'), 5)
        bush_a.inventory.remove('food', 3)
        self.assertEqual(bush_a.inventory.get_item_count('food'), 2)
        # Transition to map_b (by placing player off east edge)
        self.player.x = self.world.current_map.cell_size * self.world.current_map.width
        self.player.y = self.world.current_map.cell_size * 5
        self.world.handle_map_transition(self.player)
        self.assertEqual(self.world.current_map.name, 'map_b')
        # Switch back to map_a to verify preservation
        self.player.x = 0  # move west into map_a? Actually map_b's west neighbor is map_a, so go west
        self.player.x = -self.world.current_map.cell_size  # one cell west of map_b's west edge
        self.world.handle_map_transition(self.player)
        self.assertEqual(self.world.current_map.name, 'map_a')
        # The bush on map_a should still have 2 food
        self.assertEqual(bush_a.inventory.get_item_count('food'), 2)

    def test_transition_only_with_neighbor(self):
        """Transition does not occur if no neighbor in that direction."""
        # Start on map_a with no neighbors
        self.world.current_map.neighbors = {}  # clear neighbors
        self.player.x = self.world.current_map.cell_size * self.world.current_map.width + 100
        self.player.y = 0
        result = self.world.handle_map_transition(self.player)
        self.assertFalse(result)
        self.assertEqual(self.world.current_map.name, 'map_a')

    def test_transition_multiple_directions(self):
        """Test north and south transitions."""
        # Set up north-south neighbors
        self.map_a.neighbors['north'] = 'map_b'
        self.map_b.neighbors['south'] = 'map_a'
        # Transition north
        self.world.current_map = self.map_a
        self.player.x = 0
        self.player.y = -self.world.current_map.cell_size  # just north of top
        self.world.handle_map_transition(self.player)
        self.assertEqual(self.world.current_map.name, 'map_b')
        # Player should be at south edge of map_b
        gx, gy = self.world.grid.world_to_grid(self.player.x, self.player.y)
        self.assertEqual(gy, self.world.current_map.height - 1)  # bottom row

        # Transition south back
        self.player.x = 0
        self.player.y = self.world.current_map.cell_size * self.world.current_map.height  # just below bottom
        self.world.handle_map_transition(self.player)
        self.assertEqual(self.world.current_map.name, 'map_a')
        gx, gy = self.world.grid.world_to_grid(self.player.x, self.player.y)
        self.assertEqual(gy, 0)  # top row

if __name__ == '__main__':
    unittest.main()
