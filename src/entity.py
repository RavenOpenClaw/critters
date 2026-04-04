"""
Entity base class and Player class.
"""
import math
from inventory import Inventory

class Entity:
    """Base entity with position and radius."""
    def __init__(self, x, y, radius=20):
        self.x = x
        self.y = y
        self.radius = radius

class Player(Entity):
    """Player entity with movement speed, world bounds, interaction, buffs, and equipment."""
    def __init__(self, x, y, radius=20, speed=200):
        super().__init__(x, y, radius)
        self.base_speed = speed  # Base speed in pixels per second (without buffs)
        self.speed = speed       # Current effective speed (updated by buffs)
        self.world_rect = None   # pygame.Rect for clamping; set externally
        self.inventory = Inventory()
        self.active_buffs = []   # List of active Buff instances
        self.unlocked_equipment = set()  # Set of equipment IDs that have been unlocked
        self.equipped = set()            # Set of equipped equipment IDs

    @property
    def interaction_radius(self):
        """Distance within which the player can interact with objects (fixed 45 pixels)."""
        return 45.0

    def move(self, dx, dy, dt, grid=None):
        """Move the player with collision detection and boundary clamping.

        If a GridSystem is provided, movement that would cause the player's circular
        boundary to overlap any occupied grid cell is blocked per-axis, allowing
        sliding along obstacles.
        """
        # X axis movement
        new_x = self.x + dx * self.speed * dt
        if grid is not None:
            if self._would_collide(new_x, self.y, grid):
                new_x = self.x  # Block X movement

        # Y axis movement
        new_y = self.y + dy * self.speed * dt
        if grid is not None:
            if self._would_collide(new_x, new_y, grid):
                new_y = self.y  # Block Y movement

        self.x = new_x
        self.y = new_y

        if self.world_rect:
            self.x = max(self.radius, min(self.x, self.world_rect.width - self.radius))
            self.y = max(self.radius, min(self.y, self.world_rect.height - self.radius))

    def _would_collide(self, x, y, grid):
        """Check if player at (x,y) would collide with any occupied grid cell."""
        left = x - self.radius
        right = x + self.radius
        top = y - self.radius
        bottom = y + self.radius
        gx_min, gy_min = grid.world_to_grid(left, top)
        gx_max, gy_max = grid.world_to_grid(right, bottom)
        for gx in range(gx_min, gx_max + 1):
            for gy in range(gy_min, gy_max + 1):
                if grid.is_occupied(gx, gy):
                    return True
        return False

    def _circle_intersects_rect(self, circle_x, circle_y, circle_r, rect_x, rect_y, rect_w, rect_h):
        """Check if a circle intersects an axis-aligned rectangle."""
        # Find the closest point on the rectangle to the circle center
        closest_x = max(rect_x, min(circle_x, rect_x + rect_w))
        closest_y = max(rect_y, min(circle_y, rect_y + rect_h))
        dx = circle_x - closest_x
        dy = circle_y - closest_y
        return dx*dx + dy*dy <= circle_r*circle_r

    def interact(self, world):
        """Interact with the nearest world object whose collision shape intersects
        the player's interaction circle (radius 45). The nearest is determined by
        Euclidean distance to the object's center (for deterministic selection).
        Non-interactable objects (like Grass) are ignored.
        """
        # Local import to avoid circular dependency; Grass is a common non-interactable
        try:
            from grass import Grass
        except ImportError:
            Grass = None

        nearest = None
        min_dist_sq = float('inf')
        for obj in getattr(world, 'objects', []):
            # Skip known non-interactable types (e.g., Grass)
            if Grass is not None and isinstance(obj, Grass):
                continue
            # Determine object's collision bounds (AABB) and center
            if hasattr(obj, 'width') and hasattr(obj, 'height') and hasattr(obj, 'cell_size'):
                rect_x = obj.x
                rect_y = obj.y
                rect_w = obj.width * obj.cell_size
                rect_h = obj.height * obj.cell_size
                # Check if player's interaction circle intersects this rectangle
                if not self._circle_intersects_rect(self.x, self.y, self.interaction_radius, rect_x, rect_y, rect_w, rect_h):
                    continue  # Skip objects outside interaction range
                # Use rectangle center for distance ordering
                center_x = rect_x + rect_w / 2.0
                center_y = rect_y + rect_h / 2.0
            else:
                # Fallback for objects without rectangular bounds (e.g., point-like)
                if hasattr(obj, 'get_center'):
                    center_x, center_y = obj.get_center()
                else:
                    center_x, center_y = obj.x, obj.y
                dx = center_x - self.x
                dy = center_y - self.y
                if dx*dx + dy*dy > self.interaction_radius**2:
                    continue
            # Compute distance to center for nearest selection
            dx = center_x - self.x
            dy = center_y - self.y
            dist_sq = dx*dx + dy*dy
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                nearest = obj
        if nearest is not None:
            nearest.interact(self)

    def update(self, dt):
        """Update player state: refresh buffs, recalc effective speed, remove expired buffs."""
        # Update all active buffs; remove expired ones
        still_active = []
        for buff in self.active_buffs:
            if buff.update(dt):
                still_active.append(buff)
        self.active_buffs = still_active

        # Recompute effective speed based on speed multipliers from active buffs
        speed_mult = self._get_speed_multiplier()
        self.speed = self.base_speed * speed_mult

    def _get_speed_multiplier(self):
        """Calculate total speed multiplier from all active buffs (multiplicative)."""
        mult = 1.0
        for buff in self.active_buffs:
            if 'speed' in buff.multipliers:
                mult *= buff.multipliers['speed']
        return mult

    def get_gather_multiplier(self):
        """Calculate total gather multiplier from active buffs and equipped gear."""
        mult = 1.0
        # Buff multipliers
        for buff in self.active_buffs:
            if 'gather' in buff.multipliers:
                mult *= buff.multipliers['gather']
        # Equipment multipliers (requires import of EQUIPMENT_REGISTRY)
        from equipment import EQUIPMENT_REGISTRY
        for eq_id in self.equipped:
            eq = EQUIPMENT_REGISTRY.get(eq_id)
            if eq and eq.gather_multiplier:
                mult *= eq.gather_multiplier
        return mult

    def apply_buff(self, buff):
        """Apply a buff to the player. If a buff with the same name already exists, reset its timer."""
        for existing in self.active_buffs:
            if existing.name == buff.name:
                existing.remaining = buff.duration
                return
        self.active_buffs.append(buff)

    def unlock_equipment(self, equipment):
        """Unlock an equipment item (by id string or Equipment object)."""
        equipment_id = getattr(equipment, 'id', equipment)
        self.unlocked_equipment.add(equipment_id)

    def equip(self, equipment_id):
        """Equip an item by its ID. Requires that it is unlocked."""
        if equipment_id in self.unlocked_equipment:
            self.equipped.add(equipment_id)
            return True
        return False

    def unequip(self, equipment_id):
        """Unequip an item if it is currently equipped."""
        if equipment_id in self.equipped:
            self.equipped.remove(equipment_id)
            return True
        return False
