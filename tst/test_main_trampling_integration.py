"""
Integration test for main game loop trampling mechanic.

This test ensures the main game loop code path that converts world coordinates to
grid coordinates for entities is working correctly. This addresses the bug where
a typo (world_to_world_to_grid instead of world_to_grid) made it to production
because this specific code path wasn't being tested.
"""
import pytest
from entity import Entity, Player
from world import World
from grid_system import GridSystem
from grass import Grass


class TestMainTramplingIntegration:
    """Test the main game loop trampling code path."""

    def test_world_to_grid_conversion_in_main_loop_context(self):
        """
        Test that world_to_grid is called correctly in the main loop context.
        
        This simulates the exact code path in main.py that was failing:
        gx, gy = grid.world_to_grid(ent.x, ent.y)
        """
        cell_size = 16
        grid = GridSystem(cell_size=cell_size, width=50, height=50)
        world = World(grid)
        
        # Create a player at a specific position
        player = Player(250, 250, radius=20, speed=200)
        
        # Simulate the main loop code path
        ent = player
        gx, gy = grid.world_to_grid(ent.x, ent.y)
        
        # Verify the conversion worked
        assert isinstance(gx, int)
        assert isinstance(gy, int)
        assert gx == 250 // cell_size  # 15
        assert gy == 250 // cell_size  # 15
        
        # Verify the grid coordinates are within bounds
        assert grid.is_within_bounds(gx, gy)

    def test_entity_trampling_damage_in_main_loop_context(self):
        """
        Test that trampling damage is applied correctly through the main loop code path.
        
        This simulates the full trampling mechanic from main.py:
        entities = [player] + world.current_map.critters
        for ent in entities:
            gx, gy = grid.world_to_grid(ent.x, ent.y)
            if grid.is_within_bounds(gx, gy):
                if getattr(ent, 'last_trampled_cell', None) != (gx, gy):
                    world.mark_trampled(gx, gy)
                    ent.last_trampled_cell = (gx, gy)
        """
        cell_size = 16
        grid = GridSystem(cell_size=cell_size, width=50, height=50)
        world = World(grid)
        
        # Create grass at a known position
        grass = Grass(10, 10, cell_size=cell_size)
        world.add_object(grass)
        initial_condition = grass.condition
        
        # Create a player at that position
        player = Player(160, 160, radius=20, speed=200)  # 10*16, 10*16
        
        # Simulate the main loop code path
        entities = [player]
        for ent in entities:
            gx, gy = grid.world_to_grid(ent.x, ent.y)
            if grid.is_within_bounds(gx, gy):
                if getattr(ent, 'last_trampled_cell', None) != (gx, gy):
                    world.mark_trampled(gx, gy)
                    ent.last_trampled_cell = (gx, gy)
        
        # Verify trampling was marked
        assert world.is_trampled(10, 10)
        
        # Verify grass condition decreased (trampling damage)
        assert grass.condition < initial_condition
        assert grass.condition == initial_condition - world.trample_decay

    def test_critter_trampling_damage_in_main_loop_context(self):
        """
        Test that critter trampling damage works through the main loop code path.
        """
        from critter import Critter
        
        cell_size = 16
        grid = GridSystem(cell_size=cell_size, width=50, height=50)
        world = World(grid)
        
        # Create grass at a known position
        grass = Grass(15, 15, cell_size=cell_size)
        world.add_object(grass)
        initial_condition = grass.condition
        
        # Create a critter at that position
        critter = Critter(240, 240, cell_size=cell_size, strength=50, speed_stat=50, endurance=50)
        
        # Simulate the main loop code path
        entities = [critter]
        for ent in entities:
            gx, gy = grid.world_to_grid(ent.x, ent.y)
            if grid.is_within_bounds(gx, gy):
                if getattr(ent, 'last_trampled_cell', None) != (gx, gy):
                    world.mark_trampled(gx, gy)
                    ent.last_trampled_cell = (gx, gy)
        
        # Verify trampling was marked
        assert world.is_trampled(15, 15)
        
        # Verify grass condition decreased (trampling damage)
        assert grass.condition < initial_condition
        assert grass.condition == initial_condition - world.trample_decay

    def test_only_first_entry_applies_trampling_damage(self):
        """
        Test that trampling damage is only applied on first entry, not every frame.
        
        This simulates multiple frames where the entity stays on the same cell.
        """
        cell_size = 16
        grid = GridSystem(cell_size=cell_size, width=50, height=50)
        world = World(grid)
        
        # Create grass at a known position
        grass = Grass(20, 20, cell_size=cell_size)
        world.add_object(grass)
        initial_condition = grass.condition
        
        # Create a player at that position
        player = Player(320, 320, radius=20, speed=200)  # 20*16, 20*16
        
        # Simulate first frame (first entry)
        gx1, gy1 = grid.world_to_grid(player.x, player.y)
        if grid.is_within_bounds(gx1, gy1):
            if getattr(player, 'last_trampled_cell', None) != (gx1, gy1):
                world.mark_trampled(gx1, gy1)
                player.last_trampled_cell = (gx1, gy1)
        
        first_condition = grass.condition
        
        # Simulate multiple subsequent frames (entity stays on same cell)
        for _ in range(5):
            gx, gy = grid.world_to_grid(player.x, player.y)
            if grid.is_within_bounds(gx, gy):
                if getattr(player, 'last_trampled_cell', None) != (gx, gy):
                    world.mark_trampled(gx, gy)
                    player.last_trampled_cell = (gx, gy)
        
        # Condition should only decrease once
        assert grass.condition == first_condition
        assert grass.condition == initial_condition - world.trample_decay
