"""
Tests for Task 57: Strength-based Obstacle Requirements.
"""
import pytest
from obstacle import Obstacle
from grid_system import GridSystem
from world import World
from critter import Critter
from entity import Player

class TestObstacleStrengthRequirement:
    """Unit tests for collective strength requirements on obstacles."""

    def test_obstacle_assignment(self):
        """Verify critters can be assigned to obstacles."""
        obs = Obstacle(0, 0, 1, 1, cell_size=1, work_units=10)
        c = Critter(0, 0, cell_size=1)
        
        obs.assign_critter(c)
        assert c in obs.assigned_critters
        assert c.assigned_hut is obs

    def test_collective_strength_calculation(self):
        """Verify collective strength is the sum of assigned critters' strengths."""
        obs = Obstacle(0, 0, 1, 1, cell_size=1, work_units=10)
        c1 = Critter(0, 0, cell_size=1, strength=10)
        c2 = Critter(0, 0, cell_size=1, strength=20)
        
        obs.assign_critter(c1)
        obs.assign_critter(c2)
        
        # Collective strength should be 10 + 20 = 30
        assert obs.get_collective_strength() == 30

    def test_work_blocked_by_min_strength(self):
        """Verify work is not applied if collective strength is below min_strength."""
        obs = Obstacle(0, 0, 1, 1, cell_size=1, work_units=10, min_strength=50)
        c1 = Critter(0, 0, cell_size=1, strength=10)
        
        obs.assign_critter(c1)
        assert obs.get_collective_strength() == 10
        
        # Interaction should not reduce work units
        obs.interact(c1)
        assert obs.work_units == 10

    def test_work_applied_when_min_strength_met(self):
        """Verify work is applied if collective strength meets or exceeds min_strength."""
        obs = Obstacle(0, 0, 1, 1, cell_size=1, work_units=10, min_strength=50)
        c1 = Critter(0, 0, cell_size=1, strength=25)
        c2 = Critter(0, 0, cell_size=1, strength=30)
        
        obs.assign_critter(c1)
        obs.assign_critter(c2)
        assert obs.get_collective_strength() == 55 # 55 >= 50
        
        # Interaction by c1 should reduce work units by c1's strength
        obs.interact(c1)
        assert obs.work_units == 0 # 10 - 25 = -15 -> clamped to 0

    def test_player_interaction_assigns_follower(self):
        """Verify player interaction with obstacle assigns a following critter."""
        obs = Obstacle(0, 0, 1, 1, cell_size=1, work_units=10)
        player = Player(0, 0)
        c = Critter(0, 0, cell_size=1)
        
        c.start_follow(player)
        assert c in player.following_critters
        
        obs.interact(player)
        assert c not in player.following_critters
        assert c in obs.assigned_critters
        assert c.assigned_hut is obs

    def test_clearing_obstacle_unassigns_critters(self):
        """Verify that clearing an obstacle clears its assigned critters' references."""
        grid = GridSystem(cell_size=1)
        world = World(grid)
        obs = Obstacle(0, 0, 1, 1, cell_size=1, work_units=10, min_strength=10)
        world.add_object(obs)
        c = Critter(0, 0, cell_size=1, strength=20)
        
        obs.assign_critter(c)
        assert c.assigned_hut is obs
        
        obs.interact(c) # Clears it
        assert obs.work_units == 0
        assert c.assigned_hut is None
        assert c not in obs.assigned_critters
