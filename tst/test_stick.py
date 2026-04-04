"""
Tests for Stick world object (Task 33.3).
"""
import pytest
from stick import Stick
from inventory import Inventory

class TestStickInstantiation:
    def test_stick_creates_with_valid_parameters(self):
        stick = Stick(1, 1, cell_size=1.0, sticks=4)
        assert stick.gx == 1
        assert stick.gy == 1
        assert stick.width == 1
        assert stick.height == 1
        assert stick.inventory.get_item_count('wood') == 4

    def test_stick_default_stick_count(self):
        stick = Stick(0, 0, cell_size=1.0)
        assert stick.inventory.get_item_count('wood') == 2

    def test_stick_position_conversion(self):
        stick = Stick(3, 3, cell_size=32)
        assert stick.x == 96
        assert stick.y == 96
        cx, cy = stick.get_center()
        assert cx == 112
        assert cy == 112

class TestStickInteraction:
    def test_stick_interact_transfers_sticks(self):
        stick = Stick(0, 0, cell_size=1.0, sticks=5)
        class MockPlayer:
            def __init__(self):
                self.inventory = Inventory()
            def get_gather_multiplier(self):
                return 1.0
        player = MockPlayer()
        stick.interact(player)
        assert stick.inventory.get_item_count('wood') < 5
        assert player.inventory.has('wood', 1)

    def test_stick_get_interaction_text(self):
        stick = Stick(0, 0, cell_size=1.0)
        assert stick.get_interaction_text() == "Pick up: E"
