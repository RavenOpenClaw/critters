"""
Campfire: A building that provides a Strength buff (increased gathering) when interacted with.
"""
from building import Building
from buff import Buff

class Campfire(Building):
    """Campfire building (2x2) that grants the Strength gather buff."""
    def __init__(self, gx, gy, cell_size):
        cost = {}  # Free for now
        super().__init__(gx, gy, width=2, height=2, cell_size=cell_size, cost=cost)

    def get_interaction_text(self):
        """Return None: campfire now provides automatic aura buff, no manual interaction needed."""
        return None

    def interact(self, other):
        """Optional: still allow manual buff for compatibility, but aura handles automatically."""
        from entity import Player
        if isinstance(other, Player):
            buff = Buff("Strength", {'gather': 2.0}, duration=30.0)
            other.apply_buff(buff)
