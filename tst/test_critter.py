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
from grid_system import GridSystem
from world import World
from gathering_hut import GatheringHut
from berry_bush import BerryBush
from pathfinding import PathfindingSystem
from buff import Buff
from entity import Player

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


def test_critter_carry_capacity():
    """Test that carry capacity is ceil(endurance/20), with bounds 1-100."""
    c1 = Critter(0, 0, cell_size=32, endurance=1)
    assert c1.carry_capacity == 1
    c20 = Critter(0, 0, cell_size=32, endurance=20)
    assert c20.carry_capacity == 1
    c21 = Critter(0, 0, cell_size=32, endurance=21)
    assert c21.carry_capacity == 2
    c50 = Critter(0, 0, cell_size=32, endurance=50)
    assert c50.carry_capacity == 3
    c100 = Critter(0, 0, cell_size=32, endurance=100)
    assert c100.carry_capacity == 5


# Additional tests for Task 14 (Critter AI state machine)

def test_idle_state_spatial_constraint():
    """
    Property 12: IDLE State Spatial Constraint – IDLE critters stay near their hut.
    We'll test that after calling start_idle(), the critter's position remains within a small
    radius of the hut's center (or exactly at the hut position if not moving).
    """
    cell_size = 32
    grid = GridSystem(cell_size=cell_size, width=50, height=50)
    world = World(grid)
    hut = GatheringHut(10, 10, cell_size)
    world.add_object(hut)
    critter = Critter(hut.x, hut.y, cell_size=cell_size)
    hut.assign_critter(critter)
    # Critter should enter IDLE automatically
    assert critter.state == CritterState.IDLE

    # Simulate several updates; position should not change significantly
    initial_x, initial_y = critter.x, critter.y
    for _ in range(10):
        critter.update(0.1, world, None)  # pathfinding not needed for IDLE

    # Critter should still be very close to initial position (within epsilon)
    assert abs(critter.x - initial_x) < 1e-6
    assert abs(critter.y - initial_y) < 1e-6


def test_gather_target_within_radius():
    """
    Property 13: GATHER Target Within Radius – selected targets are within gathering radius.
    """
    cell_size = 32
    grid = GridSystem(cell_size=cell_size, width=50, height=50)
    world = World(grid)
    hut = GatheringHut(10, 10, cell_size)
    world.add_object(hut)

    # Create berry bush within gathering radius, placed to the right of hut without overlap.
    # Hut occupies cells (10-12, 10-12). Place bush at (13,10).
    bush = BerryBush(13, 10, cell_size=cell_size, berries=5)
    world.add_object(bush)

    # Place critter at a free cell adjacent to hut, e.g., (9,10) left of hut
    critter = Critter(9 * cell_size, 10 * cell_size, cell_size=cell_size, endurance=1)
    hut.assign_critter(critter)

    # Use a real pathfinding system
    pathfinding = PathfindingSystem()

    # Simulate updates until critter enters GATHER with a target selected
    max_steps = 500
    for i in range(max_steps):
        critter.update(0.05, world, pathfinding)
        if critter.state == CritterState.GATHER and critter.target_resource is not None:
            break
    else:
        pytest.fail("Critter did not enter GATHER with target")

    # Verify target is within hut's gathering radius
    hut_x = hut.x + (hut.width * cell_size) / 2
    hut_y = hut.y + (hut.height * cell_size) / 2
    tr = critter.target_resource
    tr_cx = tr.x + (getattr(tr, 'width', 0) * getattr(tr, 'cell_size', 0)) / 2
    tr_cy = tr.y + (getattr(tr, 'height', 0) * getattr(tr, 'cell_size', 0)) / 2
    dx = tr_cx - hut_x
    dy = tr_cy - hut_y
    dist = (dx*dx + dy*dy) ** 0.5
    assert dist <= hut.gathering_radius + 1e-6


def test_resource_collection_triggers_return():
    """
    Property 14: Resource Collection Triggers RETURN – collecting resource transitions to RETURN.
    """
    cell_size = 32
    grid = GridSystem(cell_size=cell_size, width=50, height=50)
    world = World(grid)
    hut = GatheringHut(10, 10, cell_size)
    world.add_object(hut)

    # Place a berry bush not overlapping the hut, within gathering radius.
    # Hut occupies cells (10-12, 10-12). Place bush at (13,10).
    bush = BerryBush(13, 10, cell_size=cell_size, berries=5)
    world.add_object(bush)

    # Place critter at a free cell to the left of the hut, e.g., (9,10)
    critter = Critter(9 * cell_size, 10 * cell_size, cell_size=cell_size, endurance=1)
    hut.assign_critter(critter)

    # Use a pathfinding system to enable movement
    pathfinding = PathfindingSystem()

    # Simulate updates until state becomes RETURN
    max_steps = 2000
    for i in range(max_steps):
        critter.update(0.05, world, pathfinding)
        if critter.state == CritterState.RETURN:
            break
    else:
        pytest.fail("Critter did not reach RETURN state")

    assert critter.state == CritterState.RETURN


def test_return_navigation_to_hut():
    """
    Property 15: RETURN Navigation to Hut – distance to hut decreases over time.
    """
    cell_size = 32
    grid = GridSystem(cell_size=cell_size, width=50, height=50)
    world = World(grid)
    hut = GatheringHut(10, 10, cell_size)
    world.add_object(hut)

    # Place a bush far enough that the critter will actually need to move
    bush = BerryBush(20, 20, cell_size=cell_size, berries=5)
    world.add_object(bush)

    critter = Critter(hut.x, hut.y, cell_size=cell_size)
    hut.assign_critter(critter)

    # Force critter into RETURN state directly to test navigation
    # We'll set held_resource and then call start_return()
    critter.held_resource = 'berry'
    critter.start_return()

    pathfinding = PathfindingSystem()

    # Record initial distance to hut center
    hut_cx = hut.x + (hut.width * hut.cell_size)/2
    hut_cy = hut.y + (hut.height * hut.cell_size)/2
    dx0 = critter.x - hut_cx
    dy0 = critter.y - hut_cy
    dist0 = (dx0*dx0 + dy0*dy0) ** 0.5

    # Simulate several updates
    for _ in range(100):
        critter.update(0.05, world, pathfinding)
        # If it reaches IDLE again, deposit completed; stop early
        if critter.state == CritterState.IDLE:
            break

    dx1 = critter.x - hut_cx
    dy1 = critter.y - hut_cy
    dist1 = (dx1*dx1 + dy1*dy1) ** 0.5

    # Distance should have decreased (or reached zero and become IDLE)
    assert dist1 <= dist0 + 1e-6, f"Distance did not decrease: {dist0} -> {dist1}"


def test_deposit_completes_cycle():
    """
    Property 16: Deposit Completes Cycle – deposit transfers resource and returns to IDLE.
    """
    cell_size = 32
    grid = GridSystem(cell_size=cell_size, width=50, height=50)
    world = World(grid)
    hut = GatheringHut(10, 10, cell_size)
    world.add_object(hut)

    critter = Critter(hut.x, hut.y, cell_size=cell_size)
    hut.assign_critter(critter)

    # Directly simulate a deposit without moving: place critter at hut center and set state to RETURN with held resource
    critter.x = hut.x + (hut.width * hut.cell_size)/2
    critter.y = hut.y + (hut.height * hut.cell_size)/2
    critter.held_resource = 'berry'
    critter.held_quantity = 1  # New: track quantity
    critter.start_return()

    # Run one update; should detect arrival and deposit
    critter.update(0.05, world, None)

    assert critter.state == CritterState.IDLE
    assert critter.held_resource is None
    assert hut.storage.has('berry', 1)


def test_gathering_hut_filters_to_berry_bushes_only():
    """
    Bug check: Gathering Hut should only return BerryBush objects as gather targets.
    Trees (or other resources) must be excluded even if they have inventory and are within radius.
    """
    from tree import Tree
    cell_size = 32
    grid = GridSystem(cell_size=cell_size, width=50, height=50)
    world = World(grid)
    hut = GatheringHut(10, 10, cell_size)
    world.add_object(hut)

    # Place a Tree with wood within gathering radius
    tree = Tree(13, 10, cell_size=cell_size, wood=10)
    world.add_object(tree)

    # Place a BerryBush also within radius
    bush = BerryBush(15, 10, cell_size=cell_size, berries=5)
    world.add_object(bush)

    # A dummy critter (position not critical)
    critter = Critter(hut.x, hut.y, cell_size=cell_size)
    hut.assign_critter(critter)

    # Repeatedly query the hut's resource selection to ensure it never picks the tree
    for _ in range(100):
        resource = hut.find_resource_in_radius(world, critter)
        # Resource should be either the BerryBush or None (if somehow bush not found); but never the Tree
        if resource is not None:
            assert isinstance(resource, BerryBush), f"Expected BerryBush, got {type(resource).__name__}"


# Regression tests for Critter buff system

def test_critter_apply_buff_resets_timer():
    critter = Critter(0, 0, cell_size=32)
    buff = Buff("Strength", {'gather': 2.0}, 30.0)
    critter.apply_buff(buff)
    assert len(critter.active_buffs) == 1
    assert critter.active_buffs[0].remaining == 30.0
    critter.active_buffs[0].update(10.0)
    assert critter.active_buffs[0].remaining == 20.0
    critter.apply_buff(buff)  # reset
    assert critter.active_buffs[0].remaining == 30.0

def test_critter_get_gather_multiplier_combines():
    critter = Critter(0, 0, cell_size=32)
    critter.active_buffs = [
        Buff("A", {'gather': 2.0}, 30),
        Buff("B", {'gather': 1.5}, 30),
        Buff("C", {'speed': 1.2}, 30)
    ]
    assert critter._get_gather_multiplier() == pytest.approx(3.0)

def test_critter_get_speed_multiplier_combines():
    critter = Critter(0, 0, cell_size=32)
    critter.active_buffs = [
        Buff("A", {'speed': 2.0}, 30),
        Buff("B", {'speed': 1.5}, 30),
        Buff("C", {'gather': 1.5}, 30)
    ]
    assert critter._get_speed_multiplier() == pytest.approx(3.0)

def test_critter_update_removes_expired_buffs():
    critter = Critter(0, 0, cell_size=32)
    b1 = Buff("Short", {}, 1.0)
    b2 = Buff("Long", {}, 5.0)
    critter.active_buffs = [b1, b2]
    b1.update(1.5)  # expired
    b2.update(1.0)  # still active
    critter._update_buffs(dt=0)
    assert b1 not in critter.active_buffs
    assert b2 in critter.active_buffs

def test_critter_buff_affects_gather_speed():
    critter = Critter(0, 0, cell_size=32, strength=50)
    assert critter.get_gather_speed() == pytest.approx(5.0)
    buff = Buff("Strength", {'gather': 2.0}, 30.0)
    critter.apply_buff(buff)
    assert critter.get_gather_speed() == pytest.approx(10.0)

def test_critter_buff_affects_movement_speed():
    critter = Critter(0, 0, cell_size=32, speed_stat=50)
    assert critter.get_movement_speed() == pytest.approx(150.0)
    buff = Buff("Haste", {'speed': 2.0}, 30.0)
    critter.apply_buff(buff)
    assert critter.get_movement_speed() == pytest.approx(300.0)

