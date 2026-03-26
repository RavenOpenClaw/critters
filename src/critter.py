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
        # Interaction radius: allow interaction from a nearby cell (1.5 × cell_size)
        self.interaction_radius = cell_size * 1.5
        # Initialize state machine state
        self.start_idle()

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

    # State machine methods
    def start_idle(self):
        """Enter IDLE state: reset idle timer to full duration."""
        self.state = CritterState.IDLE
        self.idle_timer = self.get_idle_duration()
        self.path = None
        self.path_index = 0
        self.target_resource = None

    def start_gather(self, resource_obj):
        """Enter GATHER state: set target resource and compute path to it."""
        self.state = CritterState.GATHER
        self.target_resource = resource_obj
        self.held_resource = None
        # Compute path to resource position (we'll use center of object)
        # Note: pathfinding will be set by update using pathfinding_system

    def start_return(self):
        """Enter RETURN state: clear target and set path back to hut."""
        self.state = CritterState.RETURN
        self.target_resource = None
        # Path to hut will be computed in update

    def update(self, dt, world, pathfinding_system):
        """
        Update critter state machine and movement.

        Args:
            dt: Delta time in seconds.
            world: World instance containing objects.
            pathfinding_system: PathfindingSystem instance for path queries.
        """
        if self.state == CritterState.IDLE:
            self._update_idle(dt)
        elif self.state == CritterState.GATHER:
            self._update_gather(dt, world, pathfinding_system)
        elif self.state == CritterState.RETURN:
            self._update_return(dt, world, pathfinding_system)

    def _update_idle(self, dt):
        """IDLE behavior: wait at hut location for idle duration."""
        self.idle_timer -= dt
        if self.idle_timer <= 0:
            # Transition to GATHER
            self.start_gather(None)  # target will be set by update_gather

    def _update_gather(self, dt, world, pathfinding_system):
        """GATHER behavior: find resource, pathfind, collect, then RETURN."""
        # If we don't have a target resource yet, ask the hut for one
        if self.target_resource is None and self.assigned_hut is not None:
            self.target_resource = self.assigned_hut.find_resource_in_radius(world, self)
        # If still no resource, go idle (nothing to gather)
        if self.target_resource is None:
            self.start_idle()
            return

        # If we don't have a path yet, compute it to a free cell near the resource
        if not hasattr(self, 'path') or not self.path:
            # Compute target grid coordinate of the resource's top-left
            target_gx, target_gy = world.grid.world_to_grid(self.target_resource.x, self.target_resource.y)
            # Find a free cell adjacent to the target
            goal_cell = self._find_free_cell_near(world.grid, target_gx, target_gy, max_radius=3)
            if goal_cell is None:
                # No reachable free cell near target; go idle
                self.start_idle()
                return
            start_gx, start_gy = world.grid.world_to_grid(self.x, self.y)
            self.path = pathfinding_system.find_path((start_gx, start_gy), goal_cell, world.grid)
            self.path_index = 0
            if self.path is None:
                # No path; go idle for now
                self.start_idle()
                return

        # Follow the path
        self._follow_path(dt, world)
        # Check if we've reached the target (or close enough)
        if self._has_reached_target(self.target_resource):
            # Harvest resource directly from target inventory
            self._harvest_target()

    def _update_return(self, dt, world, pathfinding_system):
        """RETURN behavior: pathfind back to hut and deposit."""
        if self.assigned_hut is None:
            self.start_idle()
            return

        # Hut center coordinates for arrival check
        hut_cx = self.assigned_hut.x + (self.assigned_hut.width * self.assigned_hut.cell_size) / 2
        hut_cy = self.assigned_hut.y + (self.assigned_hut.height * self.assigned_hut.cell_size) / 2

        # If already extremely close to hut center, deposit immediately without pathfinding
        dx = self.x - hut_cx
        dy = self.y - hut_cy
        if dx*dx + dy*dy <= (self.radius * 2) ** 2:
            self._deposit_at_hut()
            return

        # If we don't have a path yet and we have a pathfinding system, compute it
        if not hasattr(self, 'path') or not self.path:
            if pathfinding_system is None:
                # Can't pathfind; just go idle
                self.start_idle()
                return
            # Target: a free cell near the hut (start from hut's top-left)
            hut_gx, hut_gy = self.assigned_hut.gx, self.assigned_hut.gy
            # Expand search radius until we find a free cell
            goal_cell = self._find_free_cell_near(world.grid, hut_gx, hut_gy, max_radius=5)
            if goal_cell is None:
                self.start_idle()
                return
            start_gx, start_gy = world.grid.world_to_grid(self.x, self.y)
            self.path = pathfinding_system.find_path((start_gx, start_gy), goal_cell, world.grid)
            self.path_index = 0
            if self.path is None:
                # No path, go idle
                self.start_idle()
                return

        # Follow the path
        self._follow_path(dt, world)
        # After following, check if we've arrived (close to hut center)
        dx = self.x - hut_cx
        dy = self.y - hut_cy
        if dx*dx + dy*dy <= (self.radius * 2) ** 2:
            self._deposit_at_hut()

    def _deposit_at_hut(self):
        """Deposit held resource at the assigned hut and transition to IDLE."""
        if self.held_resource:
            self.assigned_hut.storage.add(self.held_resource, 1)
            self.held_resource = None
        self.start_idle()

    def _follow_path(self, dt, world):
        """
        Move along the current path using movement speed.
        Uses simple waypoint following: head to next grid cell center.
        """
        if not self.path or self.path_index >= len(self.path):
            return

        # Current target waypoint in grid coordinates
        gx, gy = self.path[self.path_index]
        # Convert to world coordinates (cell center)
        world_x, world_y = world.grid.grid_to_world(gx, gy)
        target_x = world_x + world.grid.cell_size / 2
        target_y = world_y + world.grid.cell_size / 2

        # Compute direction vector
        dx = target_x - self.x
        dy = target_y - self.y
        dist = (dx*dx + dy*dy) ** 0.5
        if dist < 1.0:
            # Reached this waypoint; advance to next
            self.path_index += 1
            if self.path_index >= len(self.path):
                self.path = None
            return

        # Move towards target at current speed
        speed = self.get_movement_speed()
        move_dist = speed * dt
        if move_dist >= dist:
            # Snap to waypoint
            self.x = target_x
            self.y = target_y
            self.path_index += 1
            if self.path_index >= len(self.path):
                self.path = None
        else:
            # Partial move
            self.x += (dx / dist) * move_dist
            self.y += (dy / dist) * move_dist

    def _has_reached_target(self, target_obj):
        """
        Check if critter is close enough to interact with target object.
        Uses interaction radius: cell_size * 1.5.
        """
        if target_obj is None:
            return False
        # Compute target center
        if hasattr(target_obj, 'get_center'):
            tx, ty = target_obj.get_center()
        else:
            tx = target_obj.x + (getattr(target_obj, 'width', 0) * getattr(target_obj, 'cell_size', 0)) / 2
            ty = target_obj.y + (getattr(target_obj, 'height', 0) * getattr(target_obj, 'cell_size', 0)) / 2
        dx = tx - self.x
        dy = ty - self.y
        dist_sq = dx*dx + dy*dy
        return dist_sq <= self.interaction_radius * self.interaction_radius

    def _find_free_cell_near(self, grid, gx, gy, max_radius=5):
        """Find a free grid cell near (gx, gy), searching outward."""
        # Quick check: if the cell itself is free and within bounds, use it
        if grid.is_within_bounds(gx, gy) and not grid.is_occupied(gx, gy):
            return (gx, gy)
        # Spiral outward search
        for r in range(1, max_radius+1):
            # Top and bottom rows
            for x in range(gx - r, gx + r + 1):
                for y in (gy - r, gy + r):
                    if grid.is_within_bounds(x, y) and not grid.is_occupied(x, y):
                        return (x, y)
            # Left and right columns (excluding corners to avoid duplicates)
            for y in range(gy - r + 1, gy + r):
                for x in (gx - r, gx + r):
                    if grid.is_within_bounds(x, y) and not grid.is_occupied(x, y):
                        return (x, y)
        return None

    def _harvest_target(self):
        """Harvest one resource from current target and transition to RETURN."""
        target = self.target_resource
        if hasattr(target, 'inventory') and target.inventory.items:
            resource_type = next(iter(target.inventory.items))
            if target.inventory.has(resource_type, 1):
                target.inventory.remove(resource_type, 1)
                self.held_resource = resource_type
                self.start_return()
                return
        # If harvesting failed (no resource), clear target and reset path
        self.target_resource = None
        self.path = None



