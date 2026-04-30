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
        # Timed interaction state
        self.active_target = None
        self.interaction_progress = 0.0 # 0.0 to 1.0

class Player(Entity):
    """Player entity with movement speed, world bounds, interaction, buffs, and equipment."""
    def __init__(self, x, y, radius=20, speed=200):
        super().__init__(x, y, radius)
        self.base_speed = speed
        self.speed = speed
        self.world_rect = None
        self.inventory = Inventory()
        self.active_buffs = []
        self.unlocked_equipment = set()
        self.equipped = set()
        self.following_critters = []  # List of critters following the player (max 2)
        self.last_trampled_cell = None  # Track last trampled grid cell to avoid repeated damage

    @property
    def following_critter(self):
        """Backward compatibility: return first following critter or None."""
        return self.following_critters[0] if self.following_critters else None

    @following_critter.setter
    def following_critter(self, value):
        if value is None:
            self.following_critters = []
        else:
            self.following_critters = [value]

    @property
    def interaction_radius(self):
        """Distance within which the player can interact with objects (fixed 45 pixels)."""
        return 45.0

    def get_interaction_speed_multiplier(self):
        """Calculate total interaction speed multiplier from active buffs and equipment."""
        mult = 1.0
        # Placeholder for future upgrades/buffs
        for buff in self.active_buffs:
            if 'interact_speed' in buff.multipliers:
                mult *= buff.multipliers['interact_speed']
        return mult

    def update_interaction(self, dt, world, is_key_held):
        """Update timed interaction progress."""
        if not is_key_held:
            self.active_target = None
            self.interaction_progress = 0.0
            return

        # If no target or target out of range/empty, find new target
        target = self.get_interactable_target(world)
        
        # If target changed or became None, reset progress
        if target is None or target != self.active_target:
            self.active_target = target
            self.interaction_progress = 0.0
            if target is None:
                return

        # Advance progress
        base_duration = 1.0
        if hasattr(target, 'get_interaction_duration'):
            base_duration = target.get_interaction_duration()
        
        # Total duration affected by player upgrades/buffs
        duration = base_duration / self.get_interaction_speed_multiplier()
        
        if duration > 0:
            self.interaction_progress += dt / duration
        else:
            self.interaction_progress = 1.0

        # Complete interaction
        if self.interaction_progress >= 1.0:
            target.interact(self)
            # Reset for repetition if target still has resources
            if self.get_interactable_target(world) == target:
                self.interaction_progress = 0.0
            else:
                self.active_target = None
                self.interaction_progress = 0.0

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
        """Interact with the nearest world object within the player's interaction radius."""
        nearest = self.get_interactable_target(world)
        if nearest is not None:
            nearest.interact(self)

    def get_interactable_target(self, world):
        """Find the nearest interactable world object within the interaction radius."""
        from utils import get_distance_to_boundary
        try:
            from grass import Grass
        except ImportError:
            Grass = None

        nearest = None
        min_dist = float('inf')
        
        # Check current map objects
        objects = []
        if hasattr(world, 'current_map'):
            objects = world.current_map.objects
        elif hasattr(world, 'objects'): # Fallback for tests
            objects = world.objects

        for obj in objects:
            # Skip known non-interactable types (e.g., Grass)
            if Grass is not None and isinstance(obj, Grass):
                continue
            
            # Check for width/height/cell_size which are needed for boundary distance
            if hasattr(obj, 'width') and hasattr(obj, 'height') and hasattr(obj, 'cell_size'):
                dist = get_distance_to_boundary(self, obj)
            else:
                # Fallback for point entities (like other Critters)
                if hasattr(obj, 'get_center'):
                    cx, cy = obj.get_center()
                else:
                    cx, cy = obj.x, obj.y
                dx = cx - self.x
                dy = cy - self.y
                dist = math.sqrt(dx*dx + dy*dy)
            
            if dist <= self.interaction_radius and dist < min_dist:
                min_dist = dist
                nearest = obj
        return nearest

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
