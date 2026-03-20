"""
Property-based tests for player interaction and resource transfer.

Requires hypothesis: pip install hypothesis
"""
import unittest
from hypothesis import given, strategies as st
import pygame
from entity import Player
from world_object import WorldObject
from berry_bush import BerryBush

# Simple mock interactable object for testing interaction targeting
class MockInteractable(WorldObject):
    def __init__(self, x, y, cell_size=1.0, label="obj"):
        # Use WorldObject with grid coordinates as world coordinates directly
        # For simplicity, we treat gx, gy as world coordinates by setting cell_size=1 and width=height=1
        super().__init__(gx=x, gy=y, width=1, height=1, cell_size=cell_size)
        self.label = label
        self.interact_called = False
        self.interacted_with = None

    def interact(self, player):
        self.interact_called = True
        self.interacted_with = player

    def get_center(self):
        # Since width=height=1 and cell_size=1, center is (x+0.5, y+0.5)
        return (self.x + 0.5, self.y + 0.5)


class TestInteractionTargeting(unittest.TestCase):
    @given(
        player_x=st.floats(min_value=-100.0, max_value=100.0),
        player_y=st.floats(min_value=-100.0, max_value=100.0),
        player_radius=st.floats(min_value=0.1, max_value=50.0),
        num_objects=st.integers(min_value=0, max_value=10),
        # Generate a list of object positions; we'll create MockInteractable for each
        obj_positions=st.lists(
            st.tuples(st.floats(min_value=-200.0, max_value=200.0),
                      st.floats(min_value=-200.0, max_value=200.0)),
            max_size=10
        )
    )
    def test_nearest_object_within_radius_is_selected(self, player_x, player_y, player_radius, num_objects, obj_positions):
        """Property 7.3: Interact selects the nearest object within interaction_radius."""
        # Limit the number of objects to the generated list length (hypothesis may ignore num_objects)
        objects = []
        for idx, (ox, oy) in enumerate(obj_positions):
            obj = MockInteractable(ox, oy, cell_size=1.0, label=f"obj{idx}")
            objects.append(obj)

        player = Player(player_x, player_y, radius=player_radius)
        # Create a dummy world with objects attribute
        class DummyWorld:
            pass
        world = DummyWorld()
        world.objects = objects

        # Reset interact flags
        for obj in objects:
            obj.interact_called = False

        player.interact(world)

        # Determine expected target
        radius_sq = player.interaction_radius ** 2
        candidates = []
        for obj in objects:
            cx, cy = obj.get_center()
            dx = cx - player_x
            dy = cy - player_y
            dist_sq = dx*dx + dy*dy
            if dist_sq <= radius_sq:
                candidates.append((dist_sq, obj))

        if not candidates:
            # No objects within radius: expect no interact called on any object
            for obj in objects:
                self.assertFalse(obj.interact_called, f"Object {obj.label} should not have been interacted with")
        else:
            # Find the candidate with minimal distance; if ties, the first in iteration order (list order)
            min_dist = min(dist for dist, _ in candidates)
            expected_objs = [obj for dist, obj in candidates if abs(dist - min_dist) < 1e-9]
            expected_obj = expected_objs[0]  # first among minima
            # Only the expected object should have interact_called=True
            for obj in objects:
                if obj is expected_obj:
                    self.assertTrue(obj.interact_called, f"Expected object {obj.label} to be interacted with")
                    self.assertEqual(obj.interacted_with, player)
                else:
                    self.assertFalse(obj.interact_called, f"Object {obj.label} should not have been interacted with")


class TestResourceTransferConservation(unittest.TestCase):
    @given(
        bush_berries=st.integers(min_value=0, max_value=100),
        player_berries=st.integers(min_value=0, max_value=100)
    )
    def test_resource_transfer_conserves_total(self, bush_berries, player_berries):
        """Property 7.4: Transferring a berry conserves total resource count."""
        # Create a BerryBush with given berries; cell_size=1 for simplicity
        bush = BerryBush(gx=0, gy=0, cell_size=1, berries=bush_berries)
        # Create a player with given berries in inventory
        player = Player(0, 0, radius=20)
        player.inventory['berry'] = player_berries

        total_before = bush.inventory.get('berry', 0) + player.inventory.get('berry', 0)

        # Perform interaction (bush.interact(player))
        bush.interact(player)

        total_after = bush.inventory.get('berry', 0) + player.inventory.get('berry', 0)

        self.assertEqual(total_after, total_before, "Total berry count should be conserved during transfer")

        # Additionally, if bush had berries, exactly one transferred
        if bush_berries > 0:
            self.assertEqual(bush.inventory.get('berry', 0), bush_berries - 1)
            self.assertEqual(player.inventory.get('berry', 0), player_berries + 1)
        else:
            # No transfer occurred; inventories unchanged
            self.assertEqual(bush.inventory.get('berry', 0), 0)
            self.assertEqual(player.inventory.get('berry', 0), player_berries)

if __name__ == '__main__':
    unittest.main()
