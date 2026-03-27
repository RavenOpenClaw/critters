"""
Tests for Obstacle work mechanics.

Feature: critters-game-prototype, Property 25: Obstacle Work Unit Depletion
         Property 26: Obstacle Removal at Zero Work Units
"""
import pytest
from hypothesis import given, strategies as st
from obstacle import Obstacle
from grid_system import GridSystem
from world import World
from critter import Critter

class TestObstacle:
    """Unit and property tests for Obstacle."""

    def test_obstacle_has_work_units_attribute(self):
        """Verify Obstacle has work_units attribute."""
        grid = GridSystem(cell_size=1)
        obs = Obstacle(0, 0, 1, 1, cell_size=1, work_units=10)
        assert hasattr(obs, 'work_units')
        assert obs.work_units == 10

    @given(
        initial_work=st.integers(min_value=1, max_value=100),
        strength=st.integers(min_value=1, max_value=100),
        n_interactions=st.integers(min_value=1, max_value=20)
    )
    def test_obstacle_work_depletion(self, initial_work, strength, n_interactions):
        """
        For any obstacle with initial work W and critter strength S,
        after N interactions, remaining work_units should be max(0, W - N*S).
        """
        cell_size = 1
        obs = Obstacle(0, 0, 1, 1, cell_size=cell_size, work_units=initial_work)
        critter = Critter(0, 0, cell_size=cell_size, strength=strength, speed_stat=50, endurance=50)

        expected_remaining = max(0, initial_work - n_interactions * strength)

        for _ in range(n_interactions):
            obs.interact(critter)

        assert obs.work_units == expected_remaining

    def test_obstacle_removed_when_zero_work_units(self):
        """
        For any obstacle that reaches zero work_units, it should be removed from the world
        and no longer block movement (i.e., no longer in grid occupancy).
        """
        cell_size = 1
        grid = GridSystem(cell_size=cell_size, width=10, height=10)
        world = World(grid)
        obs = Obstacle(5, 5, 1, 1, cell_size=cell_size, work_units=15)
        world.add_object(obs)

        assert grid.is_occupied(5, 5)
        assert obs in world.objects

        critter = Critter(0, 0, cell_size=cell_size, strength=10, speed_stat=50, endurance=50)

        # Interact until cleared
        while obs.work_units > 0:
            obs.interact(critter)

        # After clearing, obstacle should be removed from world and grid
        assert obs not in world.objects
        assert not grid.is_occupied(5, 5)