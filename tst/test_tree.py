"""
Property-based and unit tests for Tree world object (Task 33.1).
"""
import pytest
from hypothesis import given, strategies as st
from tree import Tree
from inventory import Inventory

class TestTreeInstantiation:
    """Unit tests for Tree construction."""
    def test_tree_creates_with_valid_parameters(self):
        tree = Tree(5, 5, cell_size=1.0, wood=10, respawn_duration=20.0)
        assert tree.gx == 5
        assert tree.gy == 5
        assert tree.cell_size == 1.0
        assert tree.width == 2
        assert tree.height == 2
        assert tree.inventory.get_item_count('wood') == 10
        assert tree.max_wood == 10
        assert tree.respawn_duration == 20.0
        assert not tree.depleted

    def test_tree_default_values(self):
        tree = Tree(0, 0, cell_size=1.0)
        assert tree.inventory.get_item_count('wood') == 10
        assert tree.respawn_duration == 30.0

    def test_tree_position_to_world_coords(self):
        tree = Tree(2, 3, cell_size=32)
        # Top-left should be at (2*32, 3*32)
        assert tree.x == 64
        assert tree.y == 96
        # Center should be at (2*32 + 1*32, 3*32 + 1*32) = (96, 128)
        cx, cy = tree.get_center()
        assert cx == 96
        assert cy == 128

class TestTreeRegeneration:
    """Property tests for tree regeneration after depletion."""
    @given(
        initial_wood=st.integers(min_value=1, max_value=50),
        respawn_duration=st.floats(min_value=0.1, max_value=60.0, allow_nan=False, allow_infinity=False)
    )
    def test_tree_regeneration_after_depletion(self, initial_wood, respawn_duration):
        """For any tree with initial wood, after being fully harvested and waiting at least the respawn duration, the tree should replenish to its initial wood count."""
        tree = Tree(0, 0, cell_size=1.0, wood=initial_wood, respawn_duration=respawn_duration)

        # Initially not depleted
        assert not tree.depleted
        assert tree.inventory.get_item_count('wood') == initial_wood

        # Deplete the tree completely
        tree.inventory.remove('wood', initial_wood)
        tree.update(0.0)
        assert tree.depleted
        assert tree.time_depleted == 0.0
        assert tree.inventory.get_item_count('wood') == 0

        # Simulate time passing enough to exceed respawn duration
        tree.update(respawn_duration + 0.001)
        # After respawn, tree should no longer be depleted and wood replenished to max_wood
        assert not tree.depleted
        assert tree.inventory.get_item_count('wood') == initial_wood

class TestTreeInteraction:
    """Unit tests for tree interaction."""
    def test_tree_interact_transfers_wood(self):
        tree = Tree(0, 0, cell_size=1.0, wood=5)
        # Create a mock player with inventory and get_gather_multiplier returning 1
        class MockPlayer:
            def __init__(self):
                self.inventory = Inventory()
            def get_gather_multiplier(self):
                return 1.0
        player = MockPlayer()
        tree.interact(player)
        # Should take some amount; with multiplier 1, takes at least 1
        assert tree.inventory.get_item_count('wood') < 5
        assert player.inventory.has('wood', 1)

    def test_tree_interact_respects_gather_multiplier(self):
        tree = Tree(0, 0, cell_size=1.0, wood=10)
        class MockPlayer:
            def __init__(self):
                self.inventory = Inventory()
            def get_gather_multiplier(self):
                return 3.0
        player = MockPlayer()
        # Interact once: should take 3
        tree.interact(player)
        assert tree.inventory.get_item_count('wood') == 7
        assert player.inventory.get_item_count('wood') == 3

    def test_tree_get_interaction_text(self):
        tree = Tree(0, 0, cell_size=1.0)
        assert tree.get_interaction_text() == "Chop: E"
