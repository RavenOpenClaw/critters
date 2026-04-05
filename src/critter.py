"""
Critter entity with stats and behavior helpers.
"""
import random
from enum import Enum, auto
from entity import Entity
from buff import Buff  # for apply_buff and buff handling

class CritterState(Enum):
    """State machine states for critter AI."""
    IDLE = auto()
    GATHER = auto()
    RETURN = auto()
    FOLLOW = auto()

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
            endurance: Determines carry capacity and idle duration (1-100).
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
        self.held_resource = None  # resource type (str) or None
        self.held_quantity = 0
        self.carry_capacity = max(1, (endurance + 19) // 20)  # ceil(endurance/20)
        self.is_well_fed = False
        self.active_buffs = []  # Active buff effects list
        # Interaction radius: allow interaction from a nearby cell (1.5 × cell_size)
        self.interaction_radius = cell_size * 1.5
        # Debug: flag for pathfinding activity (set during calls to find_path)
        self.is_calculating = False
        # Loiter movement timer (for idle wandering)
        self.loiter_timer = 0.0
        # Follow state
        self.following_player = None
        self.follow_timer = 0.0
        self.follow_recalc_interval = 1.0  # seconds before picking new nearby target
        self.follow_goal = None  # (gx, gy) cell target
        # Animation: 2-frame sprite animation
        self.animation_timer = 0.0
        self.animation_interval = 0.2  # seconds per frame (5 FPS)
        self.animation_frame = 0  # 0 or 1
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

    def _update_buffs(self, dt):
        """Update active buffs, removing expired ones."""
        still_active = []
        for buff in self.active_buffs:
            if buff.update(dt):
                still_active.append(buff)
        self.active_buffs = still_active

    def _get_speed_multiplier(self):
        """Calculate total speed multiplier from active buffs (multiplicative)."""
        mult = 1.0
        for buff in self.active_buffs:
            if 'speed' in buff.multipliers:
                mult *= buff.multipliers['speed']
        return mult

    def _get_gather_multiplier(self):
        """Calculate total gather multiplier from active buffs."""
        mult = 1.0
        for buff in self.active_buffs:
            if 'gather' in buff.multipliers:
                mult *= buff.multipliers['gather']
        return mult

    def apply_buff(self, buff):
        """Apply a buff to the critter. If a buff with the same name exists, reset its timer."""
        for existing in self.active_buffs:
            if existing.name == buff.name:
                existing.remaining = buff.duration
                return
        self.active_buffs.append(buff)

    def get_movement_speed(self):
        """
        Return movement speed in pixels per second.
        Base: 50 + speed_stat * 2. Well-fed multiplies speed_stat by 1.1 (capped at 100).
        Buff multipliers are applied multiplicatively.
        """
        effective_speed = self._effective_stat(self.speed_stat)
        base = 50 + effective_speed * 2
        speed_mult = self._get_speed_multiplier()
        return base * speed_mult

    def get_gather_speed(self):
        """
        Return gather speed in resources per second.
        Formula: strength * 0.1. Well-fed multiplies strength by 1.1 (capped at 100).
        Buff multipliers are applied multiplicatively.
        """
        effective_strength = self._effective_stat(self.strength)
        base = effective_strength * 0.1
        gather_mult = self._get_gather_multiplier()
        return base * gather_mult

    def get_idle_duration(self):
        """
        Return base idle duration in seconds before transitioning to GATHER.
        Scales linearly with endurance from 8 (endurance 1) to 12 (endurance 100).
        """
        # Map endurance [1,100] to [8,12]
        return 8.0 + (self.endurance - 1) * (4.0 / 99.0)

    # State machine methods
    def start_idle(self):
        """Enter IDLE state: reset idle timer, loiter movement, and clear path/gathering."""
        self.state = CritterState.IDLE
        base_duration = self.get_idle_duration()
        # Add ±1 second random jitter to desynchronize critters
        self.idle_timer = base_duration + random.uniform(-1.0, 1.0)
        if self.idle_timer < 0.1:
            self.idle_timer = 0.1
        self.path = None
        self.path_index = 0
        self.target_resource = None
        self.goal_cell = None
        self.gathering = False
        self.gather_timer = 0.0
        self.loiter_timer = random.uniform(3.0, 5.0)
        self.loiter_target = None  # (wx, wy) if currently moving during loiter

    def start_gather(self, resource_obj):
        """Enter GATHER state: set target resource and reset path/gathering state."""
        self.state = CritterState.GATHER
        self.target_resource = resource_obj
        self.held_resource = None
        self.held_quantity = 0
        self.path = None
        self.path_index = 0
        self.goal_cell = None
        self.gathering = False
        self.gather_timer = 0.0

    def start_return(self):
        """Enter RETURN state: clear target and path, then compute new path to hut."""
        self.state = CritterState.RETURN
        self.target_resource = None
        self.path = None
        self.path_index = 0
        self.goal_cell = None
        self.gathering = False
        self.gather_timer = 0.0
        # Path to hut will be computed in update

    def start_follow(self, player):
        """Begin following the player."""
        # If already following this player, ignore
        if self.state == CritterState.FOLLOW and self.following_player is player:
            return
        # Stop any existing following critter first
        if player.following_critter is not None and player.following_critter is not self:
            player.following_critter.stop_follow()
        self.state = CritterState.FOLLOW
        self.following_player = player
        player.following_critter = self
        self.follow_timer = 0.0
        self.follow_goal = None
        self.path = None
        self.path_index = 0
        self.goal_cell = None
        self.loiter_target = None

    def stop_follow(self):
        """Cease following and return to IDLE."""
        if self.state == CritterState.FOLLOW:
            # Clear player's reference if it points to us
            if self.following_player and self.following_player.following_critter is self:
                self.following_player.following_critter = None
            self.state = CritterState.IDLE
            self.following_player = None
            self.follow_timer = 0.0
            self.follow_goal = None
            self.path = None
            self.path_index = 0
            self.goal_cell = None
            self.loiter_target = None

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
        # Update active buffs and remove expired ones
        self._update_buffs(dt)
        if self.state == CritterState.IDLE:
            self._update_idle(dt, world)
        elif self.state == CritterState.GATHER:
            self._update_gather(dt, world, pathfinding_system)
        elif self.state == CritterState.RETURN:
            self._update_return(dt, world, pathfinding_system)
        elif self.state == CritterState.FOLLOW:
            self._update_follow(dt, world, pathfinding_system)

        # Animation update: toggle frame based on interval
        self.animation_timer += dt
        if self.animation_timer >= self.animation_interval:
            self.animation_timer -= self.animation_interval
            self.animation_frame = 1 - self.animation_frame

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

    def _circle_intersects_rect(self, cx, cy, r, rect_x, rect_y, rect_w, rect_h):
        """Check if a circle (center cx,cy, radius r) intersects an axis-aligned rectangle."""
        closest_x = max(rect_x, min(cx, rect_x + rect_w))
        closest_y = max(rect_y, min(cy, rect_y + rect_h))
        dx = cx - closest_x
        dy = cy - closest_y
        return dx*dx + dy*dy <= r*r

    def _is_cell_within_radius(self, gx, gy, resource):
        """Check if standing at the center of cell (gx, gy) would allow interaction with resource."""
        cx = gx * self.cell_size + self.cell_size / 2.0
        cy = gy * self.cell_size + self.cell_size / 2.0
        if hasattr(resource, 'width') and hasattr(resource, 'height') and hasattr(resource, 'cell_size'):
            rect_x = resource.x
            rect_y = resource.y
            rect_w = resource.width * resource.cell_size
            rect_h = resource.height * resource.cell_size
            return self._circle_intersects_rect(cx, cy, self.interaction_radius, rect_x, rect_y, rect_w, rect_h)
        else:
            if hasattr(resource, 'get_center'):
                tx, ty = resource.get_center()
                dx = cx - tx
                dy = cy - ty
                return dx*dx + dy*dy <= self.interaction_radius * self.interaction_radius
            return False

    def _find_free_cell_within_radius(self, grid, center_gx, center_gy, resource, max_radius=5):
        """Search for a free grid cell within max_radius that is also within interaction radius of the resource."""
        candidates = []
        for r in range(0, max_radius+1):
            # Top and bottom rows
            for x in range(center_gx - r, center_gx + r + 1):
                for y in (center_gy - r, center_gy + r):
                    if grid.is_within_bounds(x, y) and not grid.is_occupied(x, y):
                        if self._is_cell_within_radius(x, y, resource):
                            candidates.append((x, y))
            # Left and right columns (excluding corners already added)
            for y in range(center_gy - r + 1, center_gy + r):
                for x in (center_gx - r, center_gx + r):
                    if grid.is_within_bounds(x, y) and not grid.is_occupied(x, y):
                        if self._is_cell_within_radius(x, y, resource):
                            candidates.append((x, y))
        if candidates:
            return random.choice(candidates)
        return None

    def _update_gather(self, dt, world, pathfinding_system):
        """GATHER behavior: find resource, pathfind to destination, gather over time, then RETURN."""
        # Acquire target if not set
        if self.target_resource is None and self.assigned_hut is not None:
            self.target_resource = self.assigned_hut.find_resource_in_radius(world, self)
        if self.target_resource is None:
            self.start_idle()
            return

        # If not currently gathering, ensure we have a path to the goal cell
        if not self.gathering:
            if self.path is None:
                grid = world.grid
                target_gx, target_gy = grid.world_to_grid(self.target_resource.x, self.target_resource.y)
                # Find a free cell within interaction radius to stand in
                candidates = []
                for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                    cx, cy = target_gx + dx, target_gy + dy
                    if grid.is_within_bounds(cx, cy) and not grid.is_occupied(cx, cy):
                        if self._is_cell_within_radius(cx, cy, self.target_resource):
                            candidates.append((cx, cy))
                if not candidates:
                    goal_cell = self._find_free_cell_within_radius(grid, target_gx, target_gy, self.target_resource, max_radius=5)
                    if goal_cell is None:
                        self.start_idle()
                        return
                else:
                    goal_cell = random.choice(candidates)

                start_gx, start_gy = grid.world_to_grid(self.x, self.y)
                self.is_calculating = True
                self.path = pathfinding_system.find_path((start_gx, start_gy), goal_cell, grid)
                if self.path is not None:
                    print(f"[DEBUG] Critter {id(self)} GATHER path to {goal_cell} len={len(self.path)} path={self.path}")
                else:
                    print(f"[DEBUG] Critter {id(self)} GATHER no path to {goal_cell}")
                self.path_index = 0
                self.goal_cell = goal_cell
                if self.path is None:
                    self.start_idle()
                    return

            # Follow the path if we have one and not yet gathering
            if self.path is not None:
                self._follow_path(dt, world)
                # Check if we've arrived at the goal cell
                if self.path is None:
                    # Arrived: start gathering timer
                    self.gathering = True
                    self.gather_timer = 0.0
                    gather_rate = self.get_gather_speed()
                    self.gathering_time_required = 1.0 / gather_rate if gather_rate > 0 else float('inf')
                    # Snap to exact cell center of goal_cell
                    if self.goal_cell is not None:
                        gx, gy = self.goal_cell
                        self.x = gx * self.cell_size + self.cell_size / 2
                        self.y = gy * self.cell_size + self.cell_size / 2

        # If we are in the gathering phase, accumulate time and harvest when ready
        if self.gathering:
            self.gather_timer += dt
            while self.gather_timer >= self.gathering_time_required and self.target_resource is not None:
                self.gather_timer -= self.gathering_time_required
                self._harvest_target()  # may set start_return and break loop
            # Note: _harvest_target will call start_return when capacity full or target empty

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
            # Target: a free cell adjacent to the hut (including diagonals) to allow immediate deposit
            hut_cells = self.assigned_hut.get_occupied_cells()
            adjacent_cells = set()
            for hx, hy in hut_cells:
                for dx, dy in [(1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]:
                    cx, cy = hx + dx, hy + dy
                    if grid.is_within_bounds(cx, cy) and not grid.is_occupied(cx, cy):
                        adjacent_cells.add((cx, cy))
            if not adjacent_cells:
                self.start_idle()
                return
            goal_cell = random.choice(list(adjacent_cells))
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

    def _update_follow(self, dt, world, pathfinding_system):
        """FOLLOW behavior: stay near the player."""
        if self.following_player is None:
            self.start_idle()
            return
        player = self.following_player
        # Recalculate goal periodically
        self.follow_timer -= dt
        if self.follow_timer <= 0.0:
            self.follow_timer = self.follow_recalc_interval
            # Choose a free cell near player (2-3 cells away)
            grid = world.grid
            player_gx, player_gy = grid.world_to_grid(player.x, player.y)
            radius = random.choice([2, 3])
            candidates = []
            for dx in range(-radius, radius+1):
                for dy in range(-radius, radius+1):
                    if dx == 0 and dy == 0:
                        continue
                    gx = player_gx + dx
                    gy = player_gy + dy
                    if grid.is_within_bounds(gx, gy) and not grid.is_occupied(gx, gy):
                        if dx*dx + dy*dy <= radius*radius:
                            candidates.append((gx, gy))
            if candidates:
                self.follow_goal = random.choice(candidates)
            else:
                self.follow_goal = None
        # Move towards follow_goal if set
        if self.follow_goal is not None:
            goal_gx, goal_gy = self.follow_goal
            goal_x = goal_gx * self.cell_size + self.cell_size / 2
            goal_y = goal_gy * self.cell_size + self.cell_size / 2
            dx = goal_x - self.x
            dy = goal_y - self.y
            dist_sq = dx*dx + dy*dy
            if dist_sq < 1.0:
                self.x, self.y = goal_x, goal_y
                self.follow_goal = None
                self.path = None
            else:
                speed = self.get_movement_speed()
                move_dist = speed * dt
                if move_dist * move_dist >= dist_sq:
                    self.x = goal_x
                    self.y = goal_y
                else:
                    self.x += (dx / dist_sq**0.5) * move_dist
                    self.y += (dy / dist_sq**0.5) * move_dist

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
        """Deposit held resources at the assigned hut and transition to IDLE."""
        if self.held_resource and self.held_quantity > 0:
            self.assigned_hut.storage.add(self.held_resource, self.held_quantity)
            self.held_resource = None
            self.held_quantity = 0
        self.start_idle()

    def _is_adjacent_to_hut(self, critter_gx, critter_gy):
        """Check if the critter is adjacent (including diagonally) to any cell occupied by the assigned hut."""
        hut_cells = self.assigned_hut.get_occupied_cells()
        for hx, hy in hut_cells:
            # Chebyshev distance <= 1 and not the same cell
            if max(abs(critter_gx - hx), abs(critter_gy - hy)) <= 1:
                if critter_gx != hx or critter_gy != hy:
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
        Check if critter's interaction circle intersects the target object's bounding box.
        Uses the same logic as _is_cell_within_radius but based on current position.
        """
        if target_obj is None:
            return False
        # Compute target AABB
        if hasattr(target_obj, 'width') and hasattr(target_obj, 'height') and hasattr(target_obj, 'cell_size'):
            rect_x = target_obj.x
            rect_y = target_obj.y
            rect_w = target_obj.width * target_obj.cell_size
            rect_h = target_obj.height * target_obj.cell_size
            return self._circle_intersects_rect(self.x, self.y, self.interaction_radius, rect_x, rect_y, rect_w, rect_h)
        else:
            # For point-like targets, fall back to center distance check
            if hasattr(target_obj, 'get_center'):
                tx, ty = target_obj.get_center()
            else:
                tx, ty = target_obj.x, target_obj.y
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
        """Harvest one resource from current target during gathering. Transition to RETURN when capacity full or target empty."""
        target = self.target_resource
        if not (hasattr(target, 'inventory') and target.inventory.items):
            self.target_resource = None
            self.path = None
            return

        resource_type = next(iter(target.inventory.items))
        # If we haven't started a resource type yet, set it
        if self.held_resource is None:
            self.held_resource = resource_type

        # Only harvest if we haven't reached capacity and target has at least one
        if self.held_quantity < self.carry_capacity and target.inventory.has(resource_type, 1):
            target.inventory.remove(resource_type, 1)
            self.held_quantity += 1

        # Check exit conditions: capacity reached OR target depleted
        if self.held_quantity >= self.carry_capacity or not target.inventory.has(resource_type, 1):
            self.start_return()
            return

        # Otherwise, continue gathering (stay in GATHER, will harvest again next frame)

    def get_render_offset(self):
        """Return (dx, dy) offset for animation based on state and current frame."""
        if self.state in (CritterState.GATHER, CritterState.RETURN):
            # Action: left/right wobble (1-pixel shift)
            return (-1, 0) if self.animation_frame == 0 else (1, 0)
        else:  # IDLE (and any others)
            return (0, -2) if self.animation_frame == 1 else (0, 0)



