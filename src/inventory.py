"""
Inventory system for managing player and world object resources.
"""

class Inventory:
    """Manages a collection of items with quantities."""
    def __init__(self):
        self.items = {}

    def _normalize(self, item_name):
        """Normalize item name to Title Case (e.g. 'wood' -> 'Wood')."""
        if not isinstance(item_name, str):
            return item_name
        return item_name.title()

    def add(self, item_name, quantity):
        """Add quantity of an item to the inventory."""
        if quantity < 0:
            raise ValueError("Quantity to add cannot be negative")
        name = self._normalize(item_name)
        self.items[name] = self.items.get(name, 0) + quantity

    def remove(self, item_name, quantity):
        """Remove quantity of an item from the inventory. Raises ValueError if insufficient quantity or item.
        """
        if quantity < 0:
            raise ValueError("Quantity to remove cannot be negative")
        name = self._normalize(item_name)
        if name not in self.items or self.items[name] < quantity:
            raise ValueError(f"Insufficient quantity of {name} in inventory")
        self.items[name] -= quantity
        if self.items[name] == 0:
            del self.items[name]

    def has(self, item_name, quantity=1):
        """Check if the inventory contains at least the specified quantity of an item."""
        name = self._normalize(item_name)
        return self.items.get(name, 0) >= quantity

    def get_item_count(self, item_name):
        """Return the count of a specific item, or 0 if not present."""
        name = self._normalize(item_name)
        return self.items.get(name, 0)

    def get_total_quantity(self):
        """Return the total quantity of all items in the inventory."""
        return sum(self.items.values())
