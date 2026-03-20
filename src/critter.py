"""
Critter entity with stats and behavior helpers.
"""
from enum import Enum, auto
from entity import Entity

class CritterState(Enum):
    """State machine states for critter AI."""
    IDLE = auto()
    GATHER = auto()
    RETURN = auto()

class Critter(Entity):
    """Critter entity with attributes and stat-based behavior."""

    def __init__(self, x, y, cell_size=32, strength=50, speed_stat=50, endurance=50):
        """
        Initialize a critter.

        Args:
            x, y: World coordinates (pixels).
            cell_size: Size of a grid cell in pixels (used to set radius: 0.4 * cell_size).
            strength: Resource gathering effectiveness (1-100).
            speed_stat: Movement speed stat (1-100).
            endurance: Determines idle duration (1-100).
        """
        radius = cell_size * 0.4
        super().__init__(x, y, radius)
        self.strength = strength
        self.speed_stat = speed_stat
        self.endurance = endurance
        self.state = CritterState.IDLE
        self.assigned_hut = None
        self.target_resource = None
        self.held_resource = None
        self.is_well_fed = False

    def _effective_stat(self, stat):
        """Return the stat value after applying well-fed multiplier, capped at 100."""
        if self.is_well_fed:
            return min(stat * 1.1, 100)
        return stat

    def get_movement_speed(self):
        """
        Return movement speed in pixels per second.
        Base: 50 + speed_stat * 2. Well-fed multiplies speed_stat by 1.1 (capped at 100).
        """
        effective_speed = self._effective_stat(self.speed_stat)
        return 50 + effective_speed * 2

    def get_gather_speed(self):
        """
        Return gather speed in resources per second.
        Formula: strength * 0.1. Well-fed multiplies strength by 1.1 (capped at 100).
        """
        effective_strength = self._effective_stat(self.strength)
        return effective_strength * 0.1

    def get_idle_duration(self):
        """
        Return idle duration in seconds before transitioning to GATHER.
        Based on endurance: endurance * 0.5 seconds.
        """
        return self.endurance * 0.5
