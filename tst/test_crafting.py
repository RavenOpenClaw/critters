"""
Tests for crafting system (Task 28).
"""
import unittest
from hypothesis import given, strategies as st
from entity import Player
from recipe import Recipe
from equipment import Equipment, EQUIPMENT_REGISTRY
from crafting_menu import CraftingMenu

class TestCraftingSystem(unittest.TestCase):
    def setUp(self):
        EQUIPMENT_REGISTRY.clear()
        # Register test equipment
        self.equipment = Equipment("test_axe", "Test Axe", gather_multiplier=1.5)
        self.recipe = Recipe("Test Axe", "test_axe", {"food": 5}, unlocks_equipment=True)
        self.player = Player(0, 0)
        self.menu = CraftingMenu([self.recipe])

    def test_craft_success_with_sufficient_resources(self):
        """Property 33: Crafting succeeds when resources are sufficient."""
        self.player.inventory.add('food', 10)
        result = self.menu.craft_selected(self.player, self.recipe)
        self.assertTrue(result)
        self.assertIn("test_axe", self.player.unlocked_equipment)
        self.assertEqual(self.player.inventory.get_item_count('food'), 5)
        self.assertIn("Unlocked: Test Axe!", self.menu.last_message)

    def test_craft_fails_with_insufficient_resources(self):
        """Crafting fails when resources are insufficient; no unlock, inventory unchanged."""
        self.player.inventory.add('food', 3)
        result = self.menu.craft_selected(self.player, self.recipe)
        self.assertFalse(result)
        self.assertNotIn("test_axe", self.player.unlocked_equipment)
        self.assertEqual(self.player.inventory.get_item_count('food'), 3)
        self.assertIn("Not enough food!", self.menu.last_message)

    def test_craft_multiple_resource_types(self):
        """Crafting works with multiple resource types."""
        EQUIPMENT_REGISTRY.clear()
        eq = Equipment("multi_tool", "Multi Tool", gather_multiplier=2.0)
        recipe = Recipe("Multi Tool", "multi_tool", {"food": 3, "wood": 2}, unlocks_equipment=True)
        player = Player(0, 0)
        player.inventory.add('food', 5)
        player.inventory.add('wood', 4)
        menu = CraftingMenu([recipe])
        result = menu.craft_selected(player, recipe)
        self.assertTrue(result)
        self.assertIn("multi_tool", player.unlocked_equipment)
        self.assertEqual(player.inventory.get_item_count('food'), 2)
        self.assertEqual(player.inventory.get_item_count('wood'), 2)

    @given(
        available=st.integers(min_value=0, max_value=100),
        required=st.integers(min_value=1, max_value=50)
    )
    def test_crafting_success_depends_on_sufficiency(self, available, required):
        """Property: Crafting succeeds iff player has at least required amount of each resource."""
        EQUIPMENT_REGISTRY.clear()
        eq = Equipment("prop_equip", "PropEquip", gather_multiplier=1.0)
        recipe = Recipe("PropEquip", "prop_equip", {"food": required}, unlocks_equipment=True)
        player = Player(0, 0)
        if available >= required:
            player.inventory.add('food', available)
            menu = CraftingMenu([recipe])
            result = menu.craft_selected(player, recipe)
            self.assertTrue(result)
            self.assertIn("prop_equip", player.unlocked_equipment)
            self.assertEqual(player.inventory.get_item_count('food'), available - required)
        else:
            player.inventory.add('food', available)
            menu = CraftingMenu([recipe])
            result = menu.craft_selected(player, recipe)
            self.assertFalse(result)
            self.assertNotIn("prop_equip", player.unlocked_equipment)
            self.assertEqual(player.inventory.get_item_count('food'), available)

if __name__ == '__main__':
    unittest.main()
