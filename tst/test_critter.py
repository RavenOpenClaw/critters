"""
Tests for Critter entity.

These tests cover:
- CritterState enum membership
- Critter attributes existence and defaults
- Stat bounds (1-100)
- Monotonicity of stats vs derived values
- Well-fed buff multiplier and cap
"""
import pytest
from hypothesis import given, strategies as st
from critter import Critter, CritterState

# Feature: critters-game-prototype

class TestCritterState:
    """Unit tests for CritterState enum."""

    def test_enum_has_idle(self):
        assert CritterState.IDLE is not None

    def test_enum_has_gather(self):
        assert CritterState.GATHER is not None

    def test_enum_has_return(self):
        assert CritterState.RETURN is not None


class TestCritterAttributes:
    """Unit tests for Critter class attributes."""

    def test_critter_has_required_attributes(self):
        c = Critter(0, 0, cell_size=32)
        assert hasattr(c, 'strength')
        assert hasattr(c, 'speed_stat')
        assert hasattr(c, 'endurance')
        assert hasattr(c, 'state')
        assert hasattr(c, 'assigned_hut')
        assert hasattr(c, 'target_resource')
        assert hasattr(c, 'held_resource')
        assert hasattr(c, 'is_well_fed')
        assert hasattr(c, 'radius')

    def test_critter_defaults(self):
        c = Critter(0, 0, cell_size=32)
        assert c.strength == 50
        assert c.speed_stat == 50
        assert c.endurance == 50
        assert c.state == CritterState.IDLE
        assert c.assigned_hut is None
        assert c.target_resource is None
        assert c.held_resource is None
        assert c.is_well_fed is False
        assert c.radius == 32 * 0.4

    def test_critter_custom_stats(self):
        c = Critter(0, 0, cell_size=32, strength=30, speed_stat=70, endurance=80)
        assert c.strength == 30
        assert c.speed_stat == 70
        assert c.endurance == 80

    def test_critter_radius_scales_with_cell_size(self):
        c = Critter(0, 0, cell_size=64)
        assert c.radius == 64 * 0.4


# Property tests

@given(
    st.integers(min_value=1, max_value=100),
    st.integers(min_value=1, max_value=100),
    st.integers(min_value=1, max_value=100)
)
def test_stat_bounds(strength, speed_stat, endurance):
    """Property 17: Stat Bounds – stats remain within [1, 100]."""
    c = Critter(0, 0, cell_size=32, strength=strength, speed_stat=speed_stat, endurance=endurance)
    assert 1 <= c.strength <= 100
    assert 1 <= c.speed_stat <= 100
    assert 1 <= c.endurance <= 100


@given(
    st.integers(min_value=1, max_value=99),
    st.integers(min_value=2, max_value=100)
)
def test_strength_gather_speed_monotonic(s1, delta):
    """Property 18: Strength Affects Gather Speed Monotonically."""
    s2 = s1 + delta
    c1 = Critter(0, 0, cell_size=32, strength=s1)
    c2 = Critter(0, 0, cell_size=32, strength=s2)
    assert c1.get_gather_speed() < c2.get_gather_speed()


@given(
    st.integers(min_value=1, max_value=99),
    st.integers(min_value=2, max_value=100)
)
def test_speed_stat_movement_speed_monotonic(speed1, delta):
    """Property 19: Speed Stat Affects Movement Speed Monotonically."""
    speed2 = speed1 + delta
    c1 = Critter(0, 0, cell_size=32, speed_stat=speed1)
    c2 = Critter(0, 0, cell_size=32, speed_stat=speed2)
    # Without well-fed, both use base speed; ensure monotonic
    assert c1.get_movement_speed() < c2.get_movement_speed()


@given(
    st.integers(min_value=1, max_value=99),
    st.integers(min_value=2, max_value=100)
)
def test_endurance_idle_duration_monotonic(e1, delta):
    """Property 20: Endurance Affects Idle Duration Monotonically."""
    e2 = e1 + delta
    c1 = Critter(0, 0, cell_size=32, endurance=e1)
    c2 = Critter(0, 0, cell_size=32, endurance=e2)
    assert c1.get_idle_duration() < c2.get_idle_duration()


def test_well_fed_buff_multiplier_and_cap():
    """Property 21: Well-Fed Buff Multiplier – applies 1.1×, capped at 100."""
    # Strength case: below cap
    c = Critter(0, 0, cell_size=32, strength=50)
    base = c.get_gather_speed()  # 5.0
    c.is_well_fed = True
    well_fed = c.get_gather_speed()
    assert well_fed == pytest.approx(min(50 * 1.1, 100) * 0.1)  # 5.5

    # Speed case: below cap
    c2 = Critter(0, 0, cell_size=32, speed_stat=50)
    base_speed = c2.get_movement_speed()  # 50 + 50*2 = 150
    c2.is_well_fed = True
    well_fed_speed = c2.get_movement_speed()
    assert well_fed_speed == pytest.approx(50 + min(50 * 1.1, 100) * 2)  # 50+110=160

    # Cap case: strength=100 -> effective strength = 100 after cap, gather stays 10.0
    c3 = Critter(0, 0, cell_size=32, strength=100)
    base3 = c3.get_gather_speed()  # 10.0
    c3.is_well_fed = True
    assert c3.get_gather_speed() == pytest.approx(10.0)
    # Verify stat itself didn't exceed 100
    assert c3._effective_stat(c3.strength) == 100

    # Cap case: speed_stat=100 -> effective speed=100, movement speed = 250? Actually 50+100*2=250
    c4 = Critter(0, 0, cell_size=32, speed_stat=100)
    c4.is_well_fed = True
    assert c4.get_movement_speed() == pytest.approx(50 + 100 * 2)  # still 250 since cap on stat
    # So it's consistent.
