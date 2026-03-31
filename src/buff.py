"""
Buff class: represents a temporary stat multiplier applied to the player.
"""
class Buff:
    """
    A buff that applies a multiplier to specific player stats for a limited duration.

    Attributes:
        name: Human-readable buff name (e.g., "Rested", "Strength").
        multipliers: Dictionary mapping stat names to multiplier floats (e.g., {'speed': 1.5}).
        duration: Total duration in seconds.
        remaining: Time left in seconds.
    """
    def __init__(self, name, multipliers, duration):
        self.name = name
        self.multipliers = multipliers  # {'speed': 1.5, 'gather': 2.0}
        self.duration = duration
        self.remaining = duration

    def update(self, dt):
        """
        Update the buff's remaining time by dt seconds.
        Returns True if the buff is still active, False if it has expired.
        """
        self.remaining -= dt
        return self.remaining > 0
