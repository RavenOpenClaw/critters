"""
World: Container for all world entities, manages grid registration and rendering.
Supports multiple maps via MapData and portals for transitions.
"""
from grid_system import GridSystem
from map_data import MapData, Portal
from typing import Dict, List, Optional

class World:
    def __init__(self, grid_or_map):
        """
        Initialize World. Accepts either a GridSystem (legacy single-map) or a MapData.
        """
        if isinstance(grid_or_map, GridSystem):
            grid = grid_or_map
            self._legacy = True
            self.maps = {}  # no extra maps; use a single default map
            self.current_map = MapData(
                name="default",
                width=grid.width,
                height=grid.height,
                cell_size=grid.cell_size
            )
            self.grid = grid
        elif isinstance(grid_or_map, MapData):
            self._legacy = False
            self.maps = {grid_or_map.name: grid_or_map}
            self.current_map = grid_or_map
            self._rebuild_grid()
        else:
            raise TypeError("World constructor expects GridSystem or MapData")
        self.trample_duration = 5.0

    def _rebuild_grid(self):
        """Create a new GridSystem for the current map and register its objects."""
        self.grid = GridSystem(self.current_map.cell_size, self.current_map.width, self.current_map.height)
        for obj in self.current_map.objects:
            self.grid.register(obj)
            # Set world reference for all objects when building grid
            obj.world = self

    # Backward-compatible properties
    @property
    def objects(self):
        return self.current_map.objects

    @objects.setter
    def objects(self, value):
        self.current_map.objects = value

    @property
    def trampled(self):
        return self.current_map.trampled

    @trampled.setter
    def trampled(self, value):
        self.current_map.trampled = value

    @property
    def critters(self):
        return self.current_map.critters

    @property
    def critters(self):
        return self.current_map.critters

    # Map management
    def add_map(self, map_data: MapData):
        if map_data.name in self.maps:
            raise ValueError(f"Map {map_data.name} already exists")
        self.maps[map_data.name] = map_data

    def switch_map(self, map_name: str):
        if map_name not in self.maps:
            raise ValueError(f"Map {map_name} not found")
        self.current_map = self.maps[map_name]
        self._rebuild_grid()

    def get_portal_near(self, x: float, y: float, radius: float = 5.0) -> Optional[Portal]:
        """Return a portal within given radius (world units) of (x,y)."""
        cell_size = self.grid.cell_size
        for portal in self.current_map.portals.values():
            px = portal.gx * cell_size + cell_size/2
            py = portal.gy * cell_size + cell_size/2
            dx = px - x
            dy = py - y
            if dx*dx + dy*dy <= radius*radius:
                return portal
        return None

    def transition_via_portal(self, portal: Portal) -> Portal:
        """Switch to target map and return the target portal object."""
        if portal.target_map not in self.maps:
            raise ValueError(f"Target map {portal.target_map} not found")
        self.switch_map(portal.target_map)
        target = self.current_map.portals.get(portal.target_portal)
        if target is None:
            raise ValueError(f"Target portal {portal.target_portal} not found on map {portal.target_map}")
        return target

    def handle_map_transition(self, player):
        """
        Check if player should transition to another map via portal or edge boundary.
        Returns True if a transition occurred, False otherwise.
        """
        # Portal check has priority
        portal = self.get_portal_near(player.x, player.y, radius=player.radius)
        if portal:
            target = self.transition_via_portal(portal)
            cs = self.grid.cell_size
            # Place player at the center of the target portal's cell
            player.x = target.gx * cs + cs/2
            player.y = target.gy * cs + cs/2
            return True

        # Boundary-based edge transition using neighbors
        cs = self.grid.cell_size
        map_w_px = self.current_map.width * cs
        map_h_px = self.current_map.height * cs
        x, y = player.x, player.y
        neighbors = self.current_map.neighbors or {}

        direction = None
        if x < 0:
            direction = 'west'
        elif x >= map_w_px:
            direction = 'east'
        elif y < 0:
            direction = 'north'
        elif y >= map_h_px:
            direction = 'south'

        if direction and direction in neighbors:
            target_name = neighbors[direction]
            if target_name not in self.maps:
                return False
            self.switch_map(target_name)
            # After switching, place player just inside the opposite edge of the new map
            new_map = self.current_map
            new_w_px = new_map.width * cs
            new_h_px = new_map.height * cs
            if direction == 'west':
                # leaving west edge, so enter west neighbor at its east edge (right side)
                player.x = new_w_px - cs/2
                player.y = max(cs/2, min(y, new_h_px - cs/2))
            elif direction == 'east':
                # leaving east edge, enter east neighbor at its west edge (left side)
                player.x = cs/2
                player.y = max(cs/2, min(y, new_h_px - cs/2))
            elif direction == 'north':
                # leaving north edge, enter north neighbor at its south edge (bottom)
                player.y = new_h_px - cs/2
                player.x = max(cs/2, min(x, new_w_px - cs/2))
            elif direction == 'south':
                # leaving south edge, enter south neighbor at its north edge (top)
                player.y = cs/2
                player.x = max(cs/2, min(x, new_w_px - cs/2))
            return True

        return False

    # Standard API (mostly unchanged)
    def add_object(self, obj):
        if not hasattr(obj, 'cell_size') or obj.cell_size != self.grid.cell_size:
            obj.cell_size = self.grid.cell_size
        self.current_map.objects.append(obj)
        self.grid.register(obj)
        obj.world = self
        # If this object is a Critter, also add to current_map.critters list
        try:
            from critter import Critter
            if isinstance(obj, Critter):
                self.current_map.critters.append(obj)
        except ImportError:
            pass

    def remove_object(self, obj):
        if obj in self.current_map.objects:
            self.current_map.objects.remove(obj)
            self.grid.unregister(obj)

    def mark_trampled(self, gx, gy):
        self.current_map.trampled[(gx, gy)] = self.trample_duration

    def is_trampled(self, gx, gy):
        return (gx, gy) in self.current_map.trampled

    def update_trampled(self, dt):
        trampled = self.current_map.trampled
        expired = []
        for cell, remaining in trampled.items():
            remaining -= dt
            if remaining <= 0:
                expired.append(cell)
            else:
                trampled[cell] = remaining
        for cell in expired:
            trampled.pop(cell, None)

    def draw(self, screen):
        for obj in self.current_map.objects:
            if hasattr(obj, 'render'):
                obj.render(screen)
