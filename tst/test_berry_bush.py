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
        initial_berries=st.integers(min_value=1, max_value=20),
        respawn_duration=st.floats(min_value=0.1, max_value=10.0, allow_nan=False, allow_infinity=False)
    )
    def test_berry_bush_regeneration_after_depletion(self, initial_berries, respawn_duration):
        """For any berry bush with initial berries, after being fully harvested and waiting at least the respawn duration, the bush should replenish to its initial berry count."""
        cell_size = 1
        bush = BerryBush(0, 0, cell_size=cell_size, berries=initial_berries, respawn_duration=respawn_duration)

        # Initially not depleted
        assert not bush.depleted
        assert bush.inventory.get_item_count('berry') == initial_berries

        # Deplete the bush completely
        bush.inventory.remove('berry', initial_berries)
        # Trigger depletion detection via update (dt=0)
        bush.update(0.0)
        assert bush.depleted
        assert bush.time_depleted == 0.0
        assert bush.inventory.get_item_count('berry') == 0

        # Simulate time passing enough to exceed respawn duration
        bush.update(respawn_duration + 0.001)
        # After respawn, bush should no longer be depleted and berries replenished
        assert not bush.depleted
        assert bush.inventory.get_item_count('berry') == initial_berries
