"""
Tests for the Inventory system.

Requires hypothesis: pip install hypothesis
"""
import unittest
from hypothesis import given, strategies as st

from inventory import Inventory

class TestInventory(unittest.TestCase):
    @given(item_name=st.text(min_size=1), quantity=st.integers(min_value=1, max_value=100))
    def test_add_item(self, item_name, quantity):
        """Test adding items to inventory."""
        inventory = Inventory()
        inventory.add(item_name, quantity)
        self.assertEqual(inventory.get_item_count(item_name), quantity)
        # Add more of the same item
        inventory.add(item_name, quantity)
        self.assertEqual(inventory.get_item_count(item_name), quantity * 2)

    @given(item_name=st.text(min_size=1), quantity=st.integers(min_value=1, max_value=100))
    def test_remove_item_sufficient(self, item_name, quantity):
        """Test removing items when sufficient quantity is available."""
        inventory = Inventory()
        inventory.add(item_name, quantity * 2)
        inventory.remove(item_name, quantity)
        self.assertEqual(inventory.get_item_count(item_name), quantity)
        # Remove all items
        inventory.remove(item_name, quantity)
        self.assertEqual(inventory.get_item_count(item_name), 0)

    @given(item_name=st.text(min_size=1), quantity=st.integers(min_value=1, max_value=100))
    def test_remove_item_insufficient_raises_error(self, item_name, quantity):
        """Test removing items when insufficient quantity raises ValueError."""
        inventory = Inventory()
        inventory.add(item_name, quantity - 1)
        with self.assertRaises(ValueError):
            inventory.remove(item_name, quantity)
        # Test removing non-existent item
        with self.assertRaises(ValueError):
            inventory.remove("non_existent_item", 1)

    @given(item_name=st.text(min_size=1), quantity=st.integers(min_value=1, max_value=100))
    def test_has_item_sufficient(self, item_name, quantity):
        """Test checking for sufficient items."""
        inventory = Inventory()
        inventory.add(item_name, quantity)
        self.assertTrue(inventory.has(item_name, quantity))
        self.assertTrue(inventory.has(item_name, quantity // 2))

    @given(item_name=st.text(min_size=1), quantity=st.integers(min_value=1, max_value=100))
    def test_has_item_insufficient(self, item_name, quantity):
        """Test checking for insufficient items."""
        inventory = Inventory()
        inventory.add(item_name, quantity)
        self.assertFalse(inventory.has(item_name, quantity + 1))
        self.assertFalse(inventory.has("another_item", 1))

    def test_get_item_count_nonexistent(self):
        """Test getting count of a non-existent item returns 0."""
        inventory = Inventory()
        self.assertEqual(inventory.get_item_count("non_existent_item"), 0)

    def test_add_negative_quantity_raises_error(self):
        """Test adding negative quantity raises ValueError."""
        inventory = Inventory()
        with self.assertRaises(ValueError):
            inventory.add("wood", -5)

    def test_remove_negative_quantity_raises_error(self):
        """Test removing negative quantity raises ValueError."""
        inventory = Inventory()
        with self.assertRaises(ValueError):
            inventory.remove("wood", -5)

if __name__ == '__main__':
    unittest.main()
