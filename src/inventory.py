"""
Inventory system for managing player and world object resources.
"""

class Inventory:
    """Manages a collection of items with quantities."""
    def __init__(self):
        self.items = {}

    def add(self, item_name, quantity):
        """Add quantity of an item to the inventory."""
        if quantity < 0:
            raise ValueError("Quantity to add cannot be negative")
        self.items[item_name] = self.items.get(item_name, 0) + quantity

    def remove(self, item_name, quantity):
        """Remove quantity of an item from the inventory. Raises ValueError if insufficient quantity or item.
        """
        if quantity < 0:
            raise ValueError("Quantity to remove cannot be negative")
        if item_name not in self.items or self.items[item_name] < quantity:
            raise ValueError(f"Insufficient quantity of {item_name} in inventory")
        self.items[item_name] -= quantity
        if self.items[item_name] == 0:
            del self.items[item_name]

    def has(self, item_name, quantity=1):
        """Check if the inventory contains at least the specified quantity of an item."""
        return self.items.get(item_name, 0) >= quantity

    def get_item_count(self, item_name):
        """Return the count of a specific item, or 0 if not present."""
        return self.items.get(item_name, 0)
