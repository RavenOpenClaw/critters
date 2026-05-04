"""
Tests for MatingHut FIFO queue assignment logic.
"""
import pytest
from mating_hut import MatingHut
from critter import Critter, CritterState

def test_mating_hut_assignment_limit():
    """Verify that MatingHut only allows 2 critters and evicts the first one assigned."""
    hut = MatingHut(0, 0, cell_size=24)
    c1 = Critter(0, 0, cell_size=24)
    c2 = Critter(0, 0, cell_size=24)
    c3 = Critter(0, 0, cell_size=24)
    
    # Assign 1st
    hut.assign_critter(c1)
    assert c1 in hut.assigned_critters
    assert c1.state == CritterState.BREED
    
    # Assign 2nd
    hut.assign_critter(c2)
    assert c1 in hut.assigned_critters
    assert c2 in hut.assigned_critters
    assert len(hut.assigned_critters) == 2
    
    # Assign 3rd - should evict c1
    hut.assign_critter(c3)
    assert c1 not in hut.assigned_critters
    assert c2 in hut.assigned_critters
    assert c3 in hut.assigned_critters
    assert len(hut.assigned_critters) == 2
    
    # Check evicted critter state
    assert c1.assigned_hut is None
    assert c1.state == CritterState.IDLE

if __name__ == "__main__":
    test_mating_hut_assignment_limit()
    print("MatingHut FIFO test passed!")
