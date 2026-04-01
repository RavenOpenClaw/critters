"""
Tests for Critter 2-frame animation system (Task 34.1).
"""
import pytest
from critter import Critter, CritterState

class TestCritterAnimation:
    """Test animation timer, frame toggling, and render offsets."""

    def test_initial_animation_state(self):
        critter = Critter(100, 100, cell_size=32)
        assert critter.animation_frame == 0
        assert critter.animation_timer == 0.0
        assert critter.animation_interval == 0.2

    def test_animation_timer_accumulates_and_toggles(self):
        critter = Critter(0, 0, cell_size=32)
        # Prevent state transitions that require world/pathfinding by freezing timers
        critter.loiter_target = None
        critter.loiter_timer = 1000.0
        critter.idle_timer = 1000.0
        # Initial frame 0
        assert critter.animation_frame == 0

        # Update with dt=0.1 -> timer=0.1, no toggle
        critter.update(0.1, None, None)
        assert critter.animation_frame == 0

        # Update with dt=0.15 -> total 0.25, should toggle to 1
        critter.update(0.15, None, None)
        assert critter.animation_frame == 1

        # Another dt=0.1 -> timer=0.15, no toggle
        critter.update(0.1, None, None)
        assert critter.animation_frame == 1

        # Another dt=0.1 -> timer=0.25, toggle back to 0
        critter.update(0.1, None, None)
        assert critter.animation_frame == 0

    def test_get_render_offset_idle_frame0(self):
        critter = Critter(0, 0, cell_size=32)
        critter.animation_frame = 0
        assert critter.get_render_offset() == (0, 0)

    def test_get_render_offset_idle_frame1(self):
        critter = Critter(0, 0, cell_size=32)
        critter.animation_frame = 1
        assert critter.get_render_offset() == (0, -2)

    def test_get_render_offset_gather_frame0(self):
        critter = Critter(0, 0, cell_size=32)
        critter.state = CritterState.GATHER
        critter.animation_frame = 0
        assert critter.get_render_offset() == (-1, 0)

    def test_get_render_offset_gather_frame1(self):
        critter = Critter(0, 0, cell_size=32)
        critter.state = CritterState.GATHER
        critter.animation_frame = 1
        assert critter.get_render_offset() == (1, 0)

    def test_get_render_offset_return_frame0(self):
        critter = Critter(0, 0, cell_size=32)
        critter.state = CritterState.RETURN
        critter.animation_frame = 0
        assert critter.get_render_offset() == (-1, 0)

    def test_get_render_offset_return_frame1(self):
        critter = Critter(0, 0, cell_size=32)
        critter.state = CritterState.RETURN
        critter.animation_frame = 1
        assert critter.get_render_offset() == (1, 0)
