"""
Tests for BerryBush resource regeneration.

Feature: critters-game-prototype, Property 22: Tree Regeneration After Depletion
"""
import pytest
from hypothesis import given, strategies as st
from berry_bush import BerryBush

class TestBerryBushRegeneration:
    """Property tests for berry bush regeneration after depletion."""

    @given(
        initial_food=st.integers(min_value=1, max_value=20),
        respawn_duration=st.floats(min_value=0.1, max_value=10.0, allow_nan=False, allow_infinity=False)
    )
    def test_berry_bush_regeneration_after_depletion(self, initial_food, respawn_duration):
        """For any berry bush with initial food, after being fully harvested and waiting at least the respawn duration, the bush should replenish to its initial food count."""
        cell_size = 1
        bush = BerryBush(0, 0, cell_size=cell_size, berries=initial_food, respawn_duration=respawn_duration)

        # Initially not depleted
        assert not bush.depleted
        assert bush.inventory.get_item_count('food') == initial_food

        # Deplete the bush completely
        bush.inventory.remove('food', initial_food)
        # Trigger depletion detection via update (dt=0)
        bush.update(0.0)
        assert bush.depleted
        assert bush.time_depleted == 0.0
        assert bush.inventory.get_item_count('food') == 0

        # Simulate time passing enough to exceed respawn duration
        bush.update(respawn_duration + 0.001)
        # After respawn, bush should no longer be depleted and food replenished
        assert not bush.depleted
        assert bush.inventory.get_item_count('food') == initial_food

    @given(
        initial_food=st.integers(min_value=1, max_value=19),  # less than max_food (20)
        respawn_duration=st.floats(min_value=0.1, max_value=10.0, allow_nan=False, allow_infinity=False)
    )
    def test_berry_bush_partial_regrowth(self, initial_food, respawn_duration):
        """Berry bushes should regrow to full even when partially harvested (not fully depleted). This is the core fix for BERRY_REGROW."""
        max_food = 20
        cell_size = 1
        # Create a bush with max food, then remove some to get partial state
        bush = BerryBush(0, 0, cell_size=cell_size, berries=max_food, respawn_duration=respawn_duration)
        # Manually set max_food to fixed value (constructor sets it equal to berries, so adjust)
        bush.max_food = max_food
        # Remove enough food to reach the desired initial count
        to_remove = max_food - initial_food
        bush.inventory.remove('food', to_remove)
        assert bush.inventory.get_item_count('food') == initial_food
        assert not bush.depleted  # Not depleted since count > 0

        # Simulate time passing longer than respawn_duration
        bush.update(respawn_duration + 0.01)
        # After regrowth, bush should have max food
        assert bush.inventory.get_item_count('food') == max_food
        assert not bush.depleted
        assert bush.time_depleted == 0.0
