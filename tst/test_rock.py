"""
Tests for Rock world object (Task 33.2).
"""
import pytest
from rock import Rock
from inventory import Inventory

class TestRockInstantiation:
    def test_rock_creates_with_valid_parameters(self):
        rock = Rock(3, 4, cell_size=1.0, stone=5)
        assert rock.gx == 3
        assert rock.gy == 4
        assert rock.width == 1
        assert rock.height == 1
        assert rock.inventory.get_item_count('stone') == 5

    def test_rock_default_stone_count(self):
        rock = Rock(0, 0, cell_size=1.0)
        assert rock.inventory.get_item_count('stone') == 3

    def test_rock_position_conversion(self):
        rock = Rock(2, 2, cell_size=32)
        assert rock.x == 64
        assert rock.y == 64
        cx, cy = rock.get_center()
        assert cx == 80  # 2*32 + 16
        assert cy == 80

class TestRockInteraction:
    def test_rock_interact_transfers_stone(self):
        rock = Rock(0, 0, cell_size=1.0, stone=5)
        class MockPlayer:
            def __init__(self):
                self.inventory = Inventory()
            def get_gather_multiplier(self):
                return 1.0
        player = MockPlayer()
        rock.interact(player)
        assert rock.inventory.get_item_count('stone') < 5
        assert player.inventory.has('stone', 1)

    def test_rock_get_interaction_text(self):
        rock = Rock(0, 0, cell_size=1.0)
        assert rock.get_interaction_text() == "Mine: E"
