"""
Tests for trampling system preventing grass growth on trampled cells.

Feature: critters-game-prototype, Property 24: Trampling Prevents Grass Growth
"""
import pytest
from grass import Grass
from world import World
from grid_system import GridSystem

class TestTrampling:
    """Property tests for trampling mechanics."""

    def test_trampling_prevents_grass_growth_on_trampled_cell(self):
        """For any grass with a single empty adjacent cell that is trampled, the grass should not spread to that cell."""
        from world_object import WorldObject  # Import to create blocking objects

        cell_size = 1
        spread_threshold = 0.5
        grid = GridSystem(cell_size=cell_size, width=10, height=10)
        world = World(grid)
        grass = Grass(5, 5, cell_size=cell_size, spread_threshold=spread_threshold)
        world.add_object(grass)

        # Occupy all other orthogonal neighbors except (5,6) to leave only that one as the sole empty candidate
        blocked_neighbors = [(4, 5), (6, 5), (5, 4)]
        for (gx, gy) in blocked_neighbors:
            block = WorldObject(gx, gy, width=1, height=1, cell_size=cell_size, inventory=None)
            world.add_object(block)

        # Mark the remaining neighbor (5,6) as trampled
        world.mark_trampled(5, 6)

        initial_count = len([o for o in world.objects if isinstance(o, Grass)])
        assert initial_count == 1

        # Simulate one update cycle with enough dt to trigger spread
        dt = spread_threshold + 0.01
        new_objects = []
        for obj in world.objects:
            if isinstance(obj, Grass):
                result = obj.update(dt)
                if result is not None:
                    new_objects.append(result)
        world.objects.extend(new_objects)

        # No new grass should appear because the only viable neighbor is trampled
        final_grass = [o for o in world.objects if isinstance(o, Grass)]
        assert len(final_grass) == 1

    def test_grass_spreads_to_non_trampled_neighbor(self):
        """Ensure that grass still spreads to non-trampled empty cells even if some neighbors are trampled."""
        cell_size = 1
        spread_threshold = 0.5
        grid = GridSystem(cell_size=cell_size, width=10, height=10)
        world = World(grid)
        grass = Grass(5, 5, cell_size=cell_size, spread_threshold=spread_threshold)
        world.add_object(grass)

        # Mark two neighbors as trampled, but leave one non-trampled (e.g., (5,6) trampled, (6,5) free)
        world.mark_trampled(5, 6)
        world.mark_trampled(5, 4)
        # (6,5) should be free and not trampled

        initial_count = len([o for o in world.objects if isinstance(o, Grass)])
        assert initial_count == 1

        dt = spread_threshold + 0.01
        new_objects = []
        for obj in world.objects:
            if isinstance(obj, Grass):
                result = obj.update(dt)
                if result is not None:
                    new_objects.append(result)
        world.objects.extend(new_objects)

        final_grass = [o for o in world.objects if isinstance(o, Grass)]
        assert len(final_grass) == 2
        # The new grass should be at (6,5) or another non-trampled neighbor.
        new_grass = [g for g in final_grass if g is not grass][0]
        # Verify it's not in the trampled set
        assert not world.is_trampled(new_grass.gx, new_grass.gy)
        # Verify it's adjacent to original
        assert abs(new_grass.gx - 5) + abs(new_grass.gy - 5) == 1

    def test_trampled_status_decays_over_time(self):
        """Trampled cells should decay and be removed after the trample duration elapses."""
        cell_size = 1
        grid = GridSystem(cell_size=cell_size, width=10, height=10)
        world = World(grid)
        # Mark a cell as trampled; default trample_duration is 5.0
        world.mark_trampled(5, 5)
        assert world.is_trampled(5, 5)
        # Initially, trampled dict should have entry with remaining = 5.0
        assert (5, 5) in world.trampled
        assert world.trampled[(5, 5)] == world.trample_duration

        # Advance time by half duration
        world.update_trampled(world.trample_duration / 2)
        assert world.is_trampled(5, 5)
        # Remaining should be roughly half (exactly half if no rounding)
        expected_remaining = world.trample_duration / 2
        assert world.trampled[(5, 5)] == expected_remaining

        # Advance time by the remaining duration plus a bit
        world.update_trampled(expected_remaining + 0.01)
        # Should have been removed
        assert not world.is_trampled(5, 5)
        assert (5, 5) not in world.trampled
