"""
MapData: Data container for a single map region.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class Portal:
    """A portal that transitions the player to another map.

    Attributes:
        gx: Grid X coordinate (cell index) where the portal is located.
        gy: Grid Y coordinate.
        target_map: Name of the destination map.
        target_portal: Portal ID on the destination map to arrive at.
    """
    gx: int
    gy: int
    target_map: str
    target_portal: str

@dataclass
class MapData:
    """Container for all data belonging to a single map region.

    Attributes:
        name: Unique identifier for the map.
        width: Width in grid cells.
        height: Height in grid cells.
        cell_size: Size of a grid cell in world units (pixels).
        objects: List of world objects (buildings, resources, etc.)
        critters: List of critters.
        trampled: Dict mapping (gx, gy) to remaining time (seconds).
        portals: Dict mapping portal ID to Portal objects.
        neighbors: Optional dict mapping direction ('north','south','east','west') to neighboring map name.
                    Used for edge-based transitions if desired.
    """
    name: str
    width: int
    height: int
    cell_size: float
    objects: list = field(default_factory=list)
    critters: list = field(default_factory=list)
    trampled: dict = field(default_factory=dict)
    portals: Dict[str, Portal] = field(default_factory=dict)
    neighbors: Optional[Dict[str, str]] = field(default_factory=dict)
