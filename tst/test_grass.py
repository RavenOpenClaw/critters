"""
Tests for Grass propagation behavior.

Feature: critters-game-prototype, Property 23: Grass Propagation to Empty Neighbors
"""
import pytest
from hypothesis import given, strategies as st
from grass import Grass
from world import World
from grid_system import GridSystem

class TestGrassPropagation:
    """Property tests for grass spreading."""

    @given(
        gx=st.integers(min_value=1, max_value=8),
        gy=st.integers(min_value=1, max_value=8),
        spread_threshold=st.floats(min_value=0.1, max_value=5.0, allow_nan=False, allow_infinity=False)
    )
    def test_grass_propagates_to_empty_neighbor(self, gx, gy, spread_threshold):
        """For any grass tile with at least one empty adjacent cell, it should eventually spread to exactly one of those neighbors after its spread threshold."""
        cell_size = 1
        grid = GridSystem(cell_size=cell_size, width=10, height=10)
        world = World(grid)
        grass = Grass(gx, gy, cell_size=cell_size, spread_threshold=spread_threshold)
        world.add_object(grass)

        # The world initially has one grass
        initial_grass = [o for o in world.objects if isinstance(o, Grass)]
        assert len(initial_grass) == 1

        # Simulate one update cycle with enough dt to trigger spread
        dt = spread_threshold + 0.01
        new_objects = []
        for obj in world.objects:
            if isinstance(obj, Grass):
                result = obj.update(dt)
                if result is not None:
                    new_objects.append(result)
        world.objects.extend(new_objects)

        # After spread, there should be exactly 2 grass objects
        final_grass = [o for o in world.objects if isinstance(o, Grass)]
        assert len(final_grass) == 2

        # Identify the new grass (different object from original)
        new_grass = final_grass[1] if final_grass[0] is grass else final_grass[0]
        ngx, ngy = new_grass.gx, new_grass.gy
        # Manhattan distance should be 1 (adjacent orthogonal)
        assert abs(ngx - gx) + abs(ngy - gy) == 1
