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
        assert tree.width == 1 # Refactored to 1x1
        assert tree.height == 1
        assert tree.inventory.get_item_count('wood') == 10
        assert tree.max_food == 10
        assert tree.respawn_duration == 20.0
        assert not tree.depleted

    def test_tree_default_values(self):
        tree = Tree(0, 0, cell_size=1.0)
        assert tree.inventory.get_item_count('wood') == 10
        assert tree.respawn_duration == 30.0

    def test_tree_position_to_world_coords(self):
        tree = Tree(2, 3, cell_size=32)
        # Top-left should be at (2*32, 3*32) = (64, 96)
        assert tree.x == 64
        assert tree.y == 96
        # Center should be at (2*32 + 0.5*32, 3*32 + 0.5*32) = (64+16, 96+16) = (80, 112)
        cx, cy = tree.get_center()
        assert cx == 80
        assert cy == 112

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

        # Deplete the tree completely via interact (so depleted flag is set)
        # Create a mock player with large multiplier to finish it in one interact call if needed
        class MockPlayer:
            def __init__(self): self.inventory = Inventory()
            def get_gather_multiplier(self): return float(initial_wood) + 1.0
        
        player = MockPlayer()
        tree.interact(player)
        
        assert tree.depleted
        assert tree.inventory.get_item_count('wood') == 0

        # Simulate time passing enough to exceed respawn duration
        tree.update(respawn_duration + 0.001)
        # After respawn, tree should no longer be depleted and wood replenished to max_food
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
        assert tree.get_interaction_text() == "Chop Wood: E"
