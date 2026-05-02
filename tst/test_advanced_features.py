"""
Tests for Task 59 (Advanced Breeding) and Task 60 (Recycling & Candies).
"""
import pytest
from critter import Critter, CritterState
from mating_hut import MatingHut
from world import World
from grid_system import GridSystem
from map_data import MapData
from entity import Player
from constants import ITEM_CANDY_STR, ITEM_CANDY_SPD, ITEM_CANDY_END

class TestAdvancedSystems:
    def setup_method(self):
        self.grid = GridSystem(cell_size=24)
        self.m = MapData(name="main", width=10, height=10, cell_size=24)
        self.world = World(self.m)
        self.player = Player(0, 0)

    def test_breeding_inheritance_and_bounds(self):
        """Verify offspring stats are within valid bounds and not just discrete tiers."""
        hut = MatingHut(0, 0, 24)
        c1 = Critter(0, 0, strength=80, speed_stat=80, endurance=80)
        c2 = Critter(0, 0, strength=20, speed_stat=20, endurance=20)
        
        # Breed multiple times to check range
        offspring_stats = []
        for _ in range(50):
            child = hut._breed(c1, c2, self.world)
            offspring_stats.append((child.strength, child.speed_stat, child.endurance))
            assert 1 <= child.strength <= 100
            assert 1 <= child.speed_stat <= 100
            assert 1 <= child.endurance <= 100

        # With 80 and 20 parents, we should see a variety of stats, not just 50.
        # (Though we can't strictly assert randomness, we can check for variance)
        unique_str = set(s[0] for s in offspring_stats)
        assert len(unique_str) > 1

    def test_release_critter_yields_candy(self):
        """Verify releasing a critter adds the correct candy to player inventory."""
        from critter_inspector import CritterInspector
        inspector = CritterInspector(24, None, 800, 600)
        
        # Critter with high strength
        c = Critter(0, 0, strength=90, speed_stat=10, endurance=10)
        self.world.add_object(c)
        inspector.toggle(c)
        
        # Release it
        inspector.release_critter(self.player, self.world)
        
        # Check world and inventory
        assert c not in self.world.objects
        assert self.player.inventory.get_item_count(ITEM_CANDY_STR) == 1

    def test_release_critter_tie_break(self):
        """Verify releasing a critter with tied stats still yields a valid candy."""
        from critter_inspector import CritterInspector
        inspector = CritterInspector(24, None, 800, 600)
        
        # Critter with tied high stats
        c = Critter(0, 0, strength=50, speed_stat=50, endurance=10)
        self.world.add_object(c)
        inspector.toggle(c)
        
        inspector.release_critter(self.player, self.world)
        
        total_candies = (self.player.inventory.get_item_count(ITEM_CANDY_STR) + 
                         self.player.inventory.get_item_count(ITEM_CANDY_SPD))
        assert total_candies == 1

    def test_use_candy_boosts_stat(self):
        """Verify using a candy boosts the correct stat and consumes the item."""
        from critter_inspector import CritterInspector
        inspector = CritterInspector(24, None, 800, 600)
        
        c = Critter(0, 0, strength=50)
        inspector.toggle(c)
        self.player.inventory.add(ITEM_CANDY_STR, 1)
        
        inspector.use_candy_on_stat(self.player, self.world, "strength")
        
        assert c.strength == 51
        assert self.player.inventory.get_item_count(ITEM_CANDY_STR) == 0

    def test_use_candy_respects_cap(self):
        """Verify candy cannot boost a stat beyond 100."""
        from critter_inspector import CritterInspector
        inspector = CritterInspector(24, None, 800, 600)
        
        c = Critter(0, 0, strength=100)
        inspector.toggle(c)
        self.player.inventory.add(ITEM_CANDY_STR, 1)
        
        inspector.use_candy_on_stat(self.player, self.world, "strength")
        
        assert c.strength == 100
        assert self.player.inventory.get_item_count(ITEM_CANDY_STR) == 1 # Not consumed
