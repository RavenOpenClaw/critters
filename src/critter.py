"""
Critter entity with stats and behavior helpers.
"""
import random
from enum import Enum, auto
from entity import Entity

class CritterState(Enum):
    """State machine states for critter AI."""
    IDLE = auto()
    GATHER = auto()
    RETURN = auto()

class Critter(Entity):
    """Critter entity with attributes and stat-based behavior."""
    blocks_movement = False

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
        self.cell_size = cell_size
        self.state = CritterState.IDLE
        self.assigned_hut = None
        self.target_resource = None
        self.held_resource = None
        self.is_well_fed = False
        # Interaction radius: allow interaction from a nearby cell (1.5 × cell_size)
        self.interaction_radius = cell_size * 1.5
        # Debug: flag for pathfinding activity (set during calls to find_path)
        self.is_calculating = False
        # Loiter movement timer (for idle wandering)
        self.loiter_timer = 0.0
        # Initialize state machine state
        self.start_idle()

    def interact(self, player):
        """Do nothing when player interacts. TODO: do something like purr or bark when pet"""

    def get_occupied_cells(self):
        """Critters do not occupy fixed grid cells; return empty list."""
        return []

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
        Return base idle duration in seconds before transitioning to GATHER.
        Scales linearly with endurance from 8 (endurance 1) to 12 (endurance 100).
        """
        # Map endurance [1,100] to [8,12]
        return 8.0 + (self.endurance - 1) * (4.0 / 99.0)

    # State machine methods
    def start_idle(self):
        """Enter IDLE state: reset idle timer to a random duration near the base, and loiter timer."""
        self.state = CritterState.IDLE
        base_duration = self.get_idle_duration()
        # Add ±1 second random jitter to desynchronize critters
        self.idle_timer = base_duration + random.uniform(-1.0, 1.0)
        if self.idle_timer < 0.1:
            self.idle_timer = 0.1
        self.path = None
        self.path_index = 0
        self.target_resource = None
        # Loiter movement: wait a random interval before making a small move
        self.loiter_timer = random.uniform(3.0, 5.0)
        self.loiter_target = None  # (wx, wy) if currently moving during loiter

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
        # Clear per-frame calculation flag
        self.is_calculating = False
        if self.state == CritterState.IDLE:
            self._update_idle(dt, world)
        elif self.state == CritterState.GATHER:
            self._update_gather(dt, world, pathfinding_system)
        elif self.state == CritterState.RETURN:
            self._update_return(dt, world, pathfinding_system)

    def _update_idle(self, dt, world):
        """IDLE behavior: loiter near hut with smooth movement, wait for idle duration, then transition to GATHER."""
        # If we have a loiter_target, move towards it smoothly
        if self.loiter_target is not None:
            tx, ty = self.loiter_target
            dx = tx - self.x
            dy = ty - self.y
            dist_sq = dx*dx + dy*dy
            if dist_sq < 1.0:
                # Reached target
                self.x, self.y = self.loiter_target
                self.loiter_target = None
                self.loiter_timer = random.uniform(3.0, 5.0)
            else:
                speed = self.get_movement_speed()
                move_dist = speed * dt
                dist = dist_sq ** 0.5
                if move_dist >= dist:
                    self.x, self.y = self.loiter_target
                    self.loiter_target = None
                    self.loiter_timer = random.uniform(3.0, 5.0)
                else:
                    self.x += (dx / dist) * move_dist
                    self.y += (dy / dist) * move_dist
        else:
            # Loiter timer counts down to trigger a new loiter move
            self.loiter_timer -= dt
            if self.loiter_timer <= 0:
                self._perform_loiter_move(world)
                # _perform_loiter_move sets loiter_target if a valid target exists
                # Reset timer regardless to stagger attempts; if no target, we'll try again later
                self.loiter_timer = random.uniform(3.0, 5.0)

        # Idle timer counts down to transition to GATHER
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

        # If we don't have a path yet, compute it to a free cell adjacent to the resource
        if not hasattr(self, 'path') or not self.path:
            grid = world.grid
            target_gx, target_gy = grid.world_to_grid(self.target_resource.x, self.target_resource.y)
            # Collect adjacent cells (Manhattan distance 1)
            candidates = []
            for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                cx, cy = target_gx + dx, target_gy + dy
                if grid.is_within_bounds(cx, cy) and not grid.is_occupied(cx, cy):
                    candidates.append((cx, cy))
            if not candidates:
                # Fallback: broader search up to radius 3
                goal_cell = self._find_free_cell_near(grid, target_gx, target_gy, max_radius=3)
                if goal_cell is None:
                    self.start_idle()
                    return
            else:
                goal_cell = random.choice(candidates)
            start_gx, start_gy = grid.world_to_grid(self.x, self.y)
            self.is_calculating = True
            self.path = pathfinding_system.find_path((start_gx, start_gy), goal_cell, grid)
            # Debug: log computed path
            if self.path is not None:
                print(f"[DEBUG] Critter {id(self)} GATHER path to {goal_cell} len={len(self.path)} path={self.path}")
            else:
                print(f"[DEBUG] Critter {id(self)} GATHER no path to {goal_cell}")
            self.path_index = 0
            if self.path is None:
                self.start_idle()
                return

        # Follow the path
        self._follow_path(dt, world)
        # Check if we've reached the target (or close enough)
        if self._has_reached_target(self.target_resource):
            # Harvest resource directly from target inventory
            self._harvest_target()

    def _update_return(self, dt, world, pathfinding_system):
        """RETURN behavior: pathfind back to hut and deposit when adjacent."""
        if self.assigned_hut is None:
            self.start_idle()
            return

        grid = world.grid
        critter_gx, critter_gy = grid.world_to_grid(self.x, self.y)

        # Deposit if adjacent to the hut (Manhattan distance of 1 to any hut cell)
        if self._is_adjacent_to_hut(critter_gx, critter_gy):
            self._deposit_at_hut()
            return

        # If we don't have a path yet and we have a pathfinding system, compute it
        if not hasattr(self, 'path') or not self.path:
            if pathfinding_system is None:
                self.start_idle()
                return
            # Target: a free cell near the hut (with random offset to spread critters)
            hut_gx, hut_gy = self.assigned_hut.gx, self.assigned_hut.gy
            offset_gx = hut_gx + random.randint(-2, 2)
            offset_gy = hut_gy + random.randint(-2, 2)
            goal_cell = self._find_free_cell_near(world.grid, offset_gx, offset_gy, max_radius=5)
            if goal_cell is None:
                self.start_idle()
                return
            start_gx, start_gy = critter_gx, critter_gy
            self.is_calculating = True
            self.path = pathfinding_system.find_path((start_gx, start_gy), goal_cell, world.grid)
            # Debug: log computed path
            if self.path is not None:
                print(f"[DEBUG] Critter {id(self)} RETURN path to {goal_cell} len={len(self.path)} path={self.path}")
            else:
                print(f"[DEBUG] Critter {id(self)} RETURN no path to {goal_cell}")
            self.path_index = 0
            if self.path is None:
                self.start_idle()
                return

        # Follow the path
        self._follow_path(dt, world)
        # After moving, check again for adjacency
        critter_gx, critter_gy = grid.world_to_grid(self.x, self.y)
        if self._is_adjacent_to_hut(critter_gx, critter_gy):
            self._deposit_at_hut()

    def _is_adjacent_to_hut(self, critter_gx, critter_gy):
        """Check if the critter is orthogonally adjacent to any cell occupied by the assigned hut."""
        hut_cells = self.assigned_hut.get_occupied_cells()
        for hx, hy in hut_cells:
            if abs(critter_gx - hx) + abs(critter_gy - hy) == 1:
                return True
        return False

    def _perform_loiter_move(self, world):
        """Pick a nearby free cell (1-2 steps) and set loiter_target to its center; movement happens in _update_idle."""
        if self.assigned_hut is None:
            return
        grid = world.grid
        # Choose direction: one of four cardinal directions
        directions = [(1,0), (-1,0), (0,1), (0,-1)]
        dx, dy = random.choice(directions)
        # Choose step count: 1 or 2
        steps = random.choice([1, 2])
        tx = self.x + dx * steps * self.cell_size
        ty = self.y + dy * steps * self.cell_size
        gx, gy = grid.world_to_grid(tx, ty)
        if grid.is_within_bounds(gx, gy) and not grid.is_occupied(gx, gy):
            # Target cell center
            target_wx = gx * self.cell_size + self.cell_size / 2
            target_wy = gy * self.cell_size + self.cell_size / 2
            self.loiter_target = (target_wx, target_wy)
        # else: no valid target; loiter_target stays None; timer will retry later

    def _deposit_at_hut(self):
        """Deposit held resource at the assigned hut and transition to IDLE."""
        if self.held_resource:
            self.assigned_hut.storage.add(self.held_resource, 1)
            self.held_resource = None
        self.start_idle()

    def _is_adjacent_to_hut(self, critter_gx, critter_gy):
        """Check if the critter is orthogonally adjacent to any cell occupied by the assigned hut."""
        hut_cells = self.assigned_hut.get_occupied_cells()
        for hx, hy in hut_cells:
            if abs(critter_gx - hx) + abs(critter_gy - hy) == 1:
                return True
        return False

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
        """
        Find a free grid cell near (gx, gy), searching outward.
        Returns a randomly selected free cell from the search area to prevent clustering.
        """
        candidates = []
        # Quick check: if the cell itself is free and within bounds, add it
        if grid.is_within_bounds(gx, gy) and not grid.is_occupied(gx, gy):
            candidates.append((gx, gy))
        # Spiral outward search
        for r in range(1, max_radius+1):
            # Top and bottom rows
            for x in range(gx - r, gx + r + 1):
                for y in (gy - r, gy + r):
                    if grid.is_within_bounds(x, y) and not grid.is_occupied(x, y):
                        candidates.append((x, y))
            # Left and right columns (excluding corners to avoid duplicates)
            for y in range(gy - r + 1, gy + r):
                for x in (gx - r, gx + r):
                    if grid.is_within_bounds(x, y) and not grid.is_occupied(x, y):
                        candidates.append((x, y))
        if not candidates:
            return None
        return random.choice(candidates)

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



