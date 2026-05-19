"""
Critter entity with stats and behavior helpers.
"""
import random
from enum import Enum, auto
from entity import Entity
from buff import Buff  # for apply_buff and buff handling

class CritterState(Enum):
    """State machine states for critter AI."""
    REST = auto()
    GATHER = auto()
    PLANT = auto() # Planting saplings
    RETURN = auto()
    FOLLOW = auto()
    BREED = auto() # Loitering near Mating Hut

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
            endurance: Determines carry capacity and rest duration (1-100).
        """
        radius = cell_size * 0.4
        super().__init__(x, y, radius)
        self.strength = strength
        self.speed_stat = speed_stat
        self.endurance = endurance
        self.cell_size = cell_size
        self.state = CritterState.REST
        self.assigned_hut = None
        self.target_resource = None
        from inventory import Inventory
        self.inventory = Inventory()
        self.carry_capacity = max(1, (endurance + 19) // 20)  # ceil(endurance/20)
        self.is_well_fed = False
        self.active_buffs = []  # Active buff effects list
        # Interaction radius: allow interaction from a nearby cell (1.5 × cell_size)
        self.interaction_radius = cell_size * 1.5
        # Debug: flag for pathfinding activity (set during calls to find_path)
        self.is_calculating = False
        # Loiter movement timer (for rest wandering)
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
        self.path = None
        self.path_index = 0
        self.goal_cell = None
        # Trample tracking: last cell where damage was applied
        self.last_trampled_cell = None
        self.start_rest()

    def interact(self, player):
        """Toggle follow state when player interacts (E key). Provides feedback via player.world if available."""
        from constants import MESSAGE_FOLLOW_STOP, MESSAGE_FOLLOW_START
        if self.state == CritterState.FOLLOW:
            self.stop_follow()
            if hasattr(player, 'world') and player.world is not None:
                player.world.set_message(MESSAGE_FOLLOW_STOP, 2.0)
        else:
            self.start_follow(player)
            if hasattr(player, 'world') and player.world is not None:
                player.world.set_message(MESSAGE_FOLLOW_START, 2.0)

    def get_occupied_cells(self):
        """Critters do not occupy fixed grid cells; return empty list."""
        return []

    def _effective_stat(self, stat):
        """Return the stat value after applying well-fed multiplier, capped at 100."""
        if self.is_well_fed:
            return min(stat * 1.1, 100)
        return stat

    def get_color(self):
        """
        Calculate body color based on stats (RGB).
        R: Strength, G: Speed, B: Endurance.
        Stats are 1-100, mapped to 0-255.
        Uses integer math to avoid rounding errors.
        """
        r = (self.strength * 255) // 100
        g = (self.speed_stat * 255) // 100
        b = (self.endurance * 255) // 100
        return (max(0, min(r, 255)), max(0, min(g, 255)), max(0, min(b, 255)))

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
        Overburdened (inv > capacity) reduces final speed by 50%.
        """
        effective_speed = self._effective_stat(self.speed_stat)
        base = 50 + effective_speed * 2
        speed_mult = self._get_speed_multiplier()
        final_speed = base * speed_mult
        
        # Overburdened penalty
        if self.inventory.get_total_quantity() > self.carry_capacity:
            final_speed *= 0.5
            
        return final_speed

    def get_gather_multiplier(self):
        """
        Calculate total gather multiplier based on strength and buffs.
        Defined in CRITTER_STATS_BIBLE.md:
        1-40 strength: 1 item (1.0x)
        41-80 strength: 2 items (2.0x)
        81-100 strength: 3 items (3.0x)
        """
        effective_strength = self._effective_stat(self.strength)
        if effective_strength <= 40:
            base_mult = 1.0
        elif effective_strength <= 80:
            base_mult = 2.0
        else:
            base_mult = 3.0
            
        buff_mult = self._get_gather_multiplier()
        return base_mult * buff_mult

    def get_rest_duration(self):
        """
        Return base rest duration in seconds before transitioning to GATHER.
        Scales linearly with endurance from 8 (endurance 1) to 12 (endurance 100).
        """
        # Map endurance [1,100] to [8,12]
        return 8.0 + (self.endurance - 1) * (4.0 / 99.0)

    # State machine methods
    def start_rest(self):
        """Enter REST state: reset rest timer, loiter movement, and clear path/gathering."""
        self.state = CritterState.REST
        base_duration = self.get_rest_duration()
        # Add ±1 second random jitter to desynchronize critters
        self.rest_timer = base_duration + random.uniform(-1.0, 1.0)
        if self.rest_timer < 0.1:
            self.rest_timer = 0.1
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
        # If the provided resource is depleted, clear it
        if resource_obj is not None and hasattr(resource_obj, 'depleted') and resource_obj.depleted:
            self.target_resource = None
        else:
            self.target_resource = resource_obj
        self.path = None
        self.path_index = 0
        self.goal_cell = None
        self.gathering = False
        self.gather_timer = 0.0

    def start_breed(self):
        """Enter BREED state: loiter specifically around the Mating Hut."""
        self.state = CritterState.BREED
        self.rest_timer = 0.0
        self.path = None
        self.path_index = 0
        self.target_resource = None
        self.goal_cell = None
        self.gathering = False
        self.gather_timer = 0.0
        self.loiter_timer = random.uniform(1.0, 3.0)
        self.loiter_target = None

    def start_plant(self):
        """Enter PLANT state: reset path and prepare to seek a planting spot."""
        self.state = CritterState.PLANT
        self.path = None
        self.path_index = 0
        self.goal_cell = None
        self.gathering = False
        self.gather_timer = 0.0
        self.loiter_target = None

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
        # Ensure we are not already in player's list (remove if present)
        if self in player.following_critters:
            player.following_critters.remove(self)
        
        # Add this critter to following list (No hard limit)
        player.following_critters.append(self)
        self.state = CritterState.FOLLOW
        self.following_player = player
        self.follow_timer = 0.0
        self.follow_goal = None
        self.path = None
        self.path_index = 0
        self.goal_cell = None
        self.loiter_target = None

    def stop_follow(self):
        """Cease following and return to REST."""
        if self.state == CritterState.FOLLOW:
            if self.following_player:
                if self in self.following_player.following_critters:
                    self.following_player.following_critters.remove(self)
            self.state = CritterState.REST
            self.following_player = None
            self.follow_timer = 0.0
            self.follow_goal = None
            self.path = None
            self.path_index = 0
            self.goal_cell = None
            self.loiter_target = None
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
        if self.state == CritterState.REST:
            self.interaction_progress = 0.0
            self.active_target = None
            self._update_rest(dt, world)
        elif self.state == CritterState.GATHER:
            self._update_gather(dt, world, pathfinding_system)
        elif self.state == CritterState.RETURN:
            self._update_return(dt, world, pathfinding_system)
        elif self.state == CritterState.PLANT:
            self.active_target = None
            self._update_plant(dt, world, pathfinding_system)
        elif self.state == CritterState.FOLLOW:
            self.interaction_progress = 0.0
            self.active_target = None
            self._update_follow(dt, world, pathfinding_system)
        elif self.state == CritterState.BREED:
            self.active_target = None
            self._update_breed(dt, world)

        # Animation update: toggle frame based on interval
        self.animation_timer += dt
        if self.animation_timer >= self.animation_interval:
            self.animation_timer -= self.animation_interval
            self.animation_frame = 1 - self.animation_frame

    def _update_plant(self, dt, world, pathfinding_system):
        """PLANT behavior: seek valid planting spot, move there, and plant."""
        from constants import ITEM_SAPLING, PLANT_RADIUS
        from forester_hut import ForesterHut
        from sapling import Sapling

        if self.inventory.get_item_count(ITEM_SAPLING) <= 0:
            self.start_return()
            return

        grid = world.grid
        
        # 1. Seek spot if we don't have one
        if self.goal_cell is None:
            if not isinstance(self.assigned_hut, ForesterHut):
                self.start_rest()
                return
                
            hut_cx, hut_cy = self.assigned_hut.get_center()
            center_gx, center_gy = grid.world_to_grid(hut_cx, hut_cy)
            
            # [PLANT_RADIUS] Ring-based search to favor closer cells
            for r in range(1, PLANT_RADIUS + 1):
                ring_candidates = []
                for dy in range(-r, r + 1):
                    for dx in [-r, r]:
                        gx, gy = center_gx + dx, center_gy + dy
                        if grid.is_within_bounds(gx, gy) and not grid.is_occupied(gx, gy):
                            if Sapling.can_place_at(world, gx, gy):
                                ring_candidates.append((gx, gy))
                for dx in range(-(r-1), r):
                    for dy in [-r, r]:
                        gx, gy = center_gx + dx, center_gy + dy
                        if grid.is_within_bounds(gx, gy) and not grid.is_occupied(gx, gy):
                            if Sapling.can_place_at(world, gx, gy):
                                ring_candidates.append((gx, gy))
                
                if ring_candidates:
                    self.goal_cell = random.choice(ring_candidates)
                    break
            
            if self.goal_cell:
                start_gx, start_gy = grid.world_to_grid(self.x, self.y)
                self.is_calculating = True
                self.path = pathfinding_system.find_path((start_gx, start_gy), self.goal_cell, grid)
                self.path_index = 0
                
                if self.path is None:
                    self.goal_cell = None
                    return
            else:
                self.start_rest()
                return

        # 2. Follow path to planting spot
        if self.path is not None:
            self._follow_path(dt, world)

        # 3. Check for arrival (path finished or already there)
        if self.path is None and not self.gathering and self.goal_cell is not None:
            gx, gy = self.goal_cell
            # [PLANT_REVALIDATE] Arrived: re-verify spot is still valid (includes Player proximity check)
            if grid.is_occupied(gx, gy) or not Sapling.can_place_at(world, gx, gy):
                world.set_message("Critter spot invalidated (Player too close)", 1.5)
                self.goal_cell = None
                return

            self.gathering = True # Use gathering flag for interaction phase
            self.interaction_progress = 0.0

        # 4. Planting Interaction
        if self.gathering:
            mult = self.get_interaction_speed_multiplier()
            duration = 1.0 / mult
            self.interaction_progress += dt / duration

            if self.interaction_progress >= 1.0:
                # [PLANT_REVALIDATE] Final check before adding to world
                gx, gy = self.goal_cell
                if not grid.is_occupied(gx, gy) and Sapling.can_place_at(world, gx, gy):
                    # [PLANT_WORLD_ADD] Place object and ensure grid registration
                    new_sapling = Sapling(gx, gy, self.cell_size)
                    if world.add_object(new_sapling):
                        self.inventory.remove(ITEM_SAPLING, 1)
                        world.set_message("Critter planted a sapling!", 2.0)
                    else:
                        world.set_message("Critter failed to plant (blocked)", 2.0)
                else:
                    world.set_message("Critter spot invalidated", 2.0)

                
                self.gathering = False
                self.interaction_progress = 0.0
                self.goal_cell = None
                # Transition back to RETURN to check for more saplings in hut
                self.start_return()
    def _update_rest(self, dt, world):
        """REST behavior: loiter near hut with smooth movement, wait for rest duration, then transition to GATHER or PLANT."""
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

        # Rest timer counts down to transition
        self.rest_timer -= dt
        if self.rest_timer <= 0:
            from forester_hut import ForesterHut
            from obstacle import Obstacle
            from constants import ITEM_SAPLING

            # Forester Priority
            if isinstance(self.assigned_hut, ForesterHut):
                if self.inventory.get_item_count(ITEM_SAPLING) > 0:
                    self.start_plant()
                else:
                    # Fetch from hut storage
                    if self.assigned_hut.storage.get_item_count(ITEM_SAPLING) > 0:
                        gx, gy = world.grid.world_to_grid(self.x, self.y)
                        if self._is_adjacent_to_hut(gx, gy):
                            self.assigned_hut.storage.remove(ITEM_SAPLING, 1)
                            self.inventory.add(ITEM_SAPLING, 1)
                            self.start_plant()
                        else:
                            self.start_return() 
                    else:
                        self.rest_timer = random.uniform(5.0, 10.0)
            
            # Gathering Priority
            elif self.assigned_hut and isinstance(self.assigned_hut, Obstacle):
                self.start_gather(self.assigned_hut)
            elif self.assigned_hut and self.assigned_hut.can_gather():
                self.start_gather(None)
            else:
                # No valid gathering; remain in REST with extended timer to avoid constant re-evaluation
                self.rest_timer = random.uniform(10.0, 20.0)

    def _update_breed(self, dt, world):
        """BREED behavior: loiter specifically near the assigned Mating Hut."""
        from mating_hut import MatingHut
        if not self.assigned_hut or not isinstance(self.assigned_hut, MatingHut):
            self.start_rest()
            return

        # Smooth loiter movement (same logic as REST but tighter radius)
        if self.loiter_target is not None:
            tx, ty = self.loiter_target
            dx = tx - self.x
            dy = ty - self.y
            dist_sq = dx*dx + dy*dy
            if dist_sq < 1.0:
                self.x, self.y = self.loiter_target
                self.loiter_target = None
                self.loiter_timer = random.uniform(2.0, 4.0)
            else:
                speed = self.get_movement_speed() * 0.6 # Move slower near hut
                move_dist = speed * dt
                dist = dist_sq ** 0.5
                if move_dist >= dist:
                    self.x, self.y = self.loiter_target
                    self.loiter_target = None
                    self.loiter_timer = random.uniform(2.0, 4.0)
                else:
                    self.x += (dx / dist) * move_dist
                    self.y += (dy / dist) * move_dist
        else:
            self.loiter_timer -= dt
            if self.loiter_timer <= 0:
                # Pick a spot adjacent to the hut
                grid = world.grid
                hut_cells = self.assigned_hut.get_occupied_cells()
                adj_candidates = []
                for hx, hy in hut_cells:
                    for dx, dy in [(1,0), (-1,0), (0,1), (0,-1), (1,1), (-1,-1), (1,-1), (-1,1)]:
                        cx, cy = hx + dx, hy + dy
                        if grid.is_within_bounds(cx, cy) and not grid.is_occupied(cx, cy):
                            adj_candidates.append((cx, cy))
                
                if adj_candidates:
                    gx, gy = random.choice(adj_candidates)
                    self.loiter_target = (gx * self.cell_size + self.cell_size / 2,
                                         gy * self.cell_size + self.cell_size / 2)
                self.loiter_timer = random.uniform(2.0, 4.0)

    def render(self, screen, camera=None):
        """Draw the critter with procedural animation and stat-based coloring."""
        import pygame
        # Calculate screen position
        draw_x, draw_y = self.x, self.y
        if camera:
            draw_x, draw_y = camera.apply(self.x, self.y)

        # Apply state-based procedural offsets (jiggle/wobble)
        ox, oy = self.get_render_offset()
        final_x = int(draw_x + ox)
        final_y = int(draw_y + oy)

        # Draw Body (Stat-based color)
        color = self.get_color()
        pygame.draw.circle(screen, color, (final_x, final_y), int(self.radius))
        # Add outline for definition
        pygame.draw.circle(screen, (0, 0, 0), (final_x, final_y), int(self.radius), 1)

        # Draw eyes (simple dots)
        eye_offset = self.radius * 0.4
        pygame.draw.circle(screen, (255, 255, 255), (int(final_x - eye_offset), int(final_y - eye_offset)), 2)
        pygame.draw.circle(screen, (255, 255, 255), (int(final_x + eye_offset), int(final_y - eye_offset)), 2)

        # Draw State Text above critter
        font = pygame.font.SysFont(None, 16)
        state_text = self.state.name
        text_surf = font.render(state_text, True, (50, 50, 50))
        text_rect = text_surf.get_rect(center=(final_x, final_y - self.radius - 12))
        screen.blit(text_surf, text_rect)

        # Interaction Progress Circle
        if self.gathering and self.interaction_progress > 0:
            import math
            prog_radius = self.radius + 5
            rect = pygame.Rect(int(final_x - prog_radius), int(final_y - prog_radius), 
                               int(prog_radius * 2), int(prog_radius * 2))
            # Draw clockwise from top (12 o'clock)
            # Pygame draws arcs CCW. To make it LOOK clockwise filling from top (pi/2):
            # We start at (pi/2 - sweep) and end at pi/2.
            sweep = 2 * math.pi * self.interaction_progress
            start_angle = math.pi / 2 - sweep
            stop_angle = math.pi / 2
            pygame.draw.arc(screen, (0, 255, 0), rect, start_angle, stop_angle, 3)

    def get_render_offset(self):
        """Return (dx, dy) pixel offset for animation based on current state and frame."""
        # Simple procedural animation: wobble or jump
        if self.state in (CritterState.GATHER, CritterState.RETURN):
            # Action: left/right wobble (1-pixel shift)
            return (-1, 0) if self.animation_frame == 0 else (1, 0)
        else:  # REST, BREED, FOLLOW
            # Subtle hop
            return (0, -2) if self.animation_frame == 1 else (0, 0)

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

    def get_interaction_speed_multiplier(self):
        """
        Return multiplier for how fast the interaction circle fills.
        High SPD critters are faster. Base SPD (50) is 1.0x.
        Formula: 0.5 + speed_stat / 100.0 (ranges 0.51 to 1.5).
        """
        effective_speed = self._effective_stat(self.speed_stat)
        base_mult = 0.5 + effective_speed / 100.0
        gather_mult = self._get_gather_multiplier() # Buffs
        mult = base_mult * gather_mult
        return max(0.01, mult) # Ensure non-zero positive
    def _update_gather(self, dt, world, pathfinding_system):
        """GATHER behavior: find resource, pathfind to destination, gather over time, then RETURN."""
        # Acquire target if not set
        if self.target_resource is None and self.assigned_hut is not None:
            self.target_resource = self.assigned_hut.find_resource_in_radius(world, self)
        if self.target_resource is None:
            self.start_rest()
            return

        # If not currently gathering, ensure we have a path to the goal cell
        if not self.gathering:
            # Fallback/guardrail: if path is None or empty, plan a new route
            if self.path is None or not self.path:
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
                        self.start_rest()
                        return
                else:
                    goal_cell = random.choice(candidates)

                start_gx, start_gy = grid.world_to_grid(self.x, self.y)
                self.is_calculating = True
                self.path = pathfinding_system.find_path((start_gx, start_gy), goal_cell, grid)
                self.path_index = 0
                self.goal_cell = goal_cell
                if self.path is None or not self.path:
                    self.start_rest()
                    return

            # Follow the path if we have one and not yet gathering
            if self.path is not None:
                self._follow_path(dt, world)
                
            # Check for arrival (path finished or already there)
            if self.path is None and not self.gathering and self.goal_cell is not None:
                # Arrived: start gathering phase
                self.gathering = True
                self.interaction_progress = 0.0
                self.active_target = self.target_resource
                # Snap to exact cell center of goal_cell
                gx, gy = self.goal_cell
                self.x = gx * self.cell_size + self.cell_size / 2
                self.y = gy * self.cell_size + self.cell_size / 2

        # If we are in the gathering phase, accumulate time and harvest when ready
        if self.gathering:
            # Check if target is still valid/not depleted by others
            from obstacle import Obstacle
            target_valid = True
            if isinstance(self.target_resource, Obstacle):
                if self.target_resource.work_units <= 0:
                    target_valid = False
            elif not (hasattr(self.target_resource, 'inventory') and self.target_resource.inventory.items):
                target_valid = False

            if not self._has_reached_target(self.target_resource) or not target_valid:
                # Target lost or empty: reset and seek new
                self.gathering = False
                self.interaction_progress = 0.0
                self.active_target = None
                self.target_resource = None
                self._continue_gathering_or_return(world)
                return

            base_duration = 1.0
            if hasattr(self.target_resource, 'get_interaction_duration'):
                base_duration = self.target_resource.get_interaction_duration()
            
            duration = base_duration / self.get_interaction_speed_multiplier()
            self.interaction_progress += dt / duration
            
            if self.interaction_progress >= 1.0:
                self._harvest_target(world)
                # _harvest_target sets state to RETURN if full, or clears target_resource if empty
                if self.state == CritterState.GATHER and self.target_resource:
                    self.interaction_progress = 0.0 # Repeat
                else:
                    self.gathering = False
                    self.interaction_progress = 0.0
                    self.active_target = None

    def _update_return(self, dt, world, pathfinding_system):
        """RETURN behavior: pathfind back to hut and deposit when adjacent."""
        if self.assigned_hut is None:
            self.start_rest()
            return

        grid = world.grid
        critter_gx, critter_gy = grid.world_to_grid(self.x, self.y)

        # Handle depositing interaction phase
        if self.gathering: # Borrowing 'gathering' flag for 'in-interaction-phase'
            # Must stay adjacent
            if not self._is_adjacent_to_hut(critter_gx, critter_gy):
                self.gathering = False
                self.interaction_progress = 0.0
                self.active_target = None
                return

            base_duration = 1.5 # Deposit duration
            duration = base_duration / self.get_interaction_speed_multiplier()
            self.interaction_progress += dt / duration
            
            if self.interaction_progress >= 1.0:
                self._deposit_at_hut()
                self.gathering = False
                self.interaction_progress = 0.0
                self.active_target = None
            return

        # Check for arrival
        if self._is_adjacent_to_hut(critter_gx, critter_gy):
            self.gathering = True
            self.interaction_progress = 0.0
            self.active_target = self.assigned_hut
            return

        # If we don't have a path yet and we have a pathfinding system, compute it
        if not hasattr(self, 'path') or not self.path:
            if pathfinding_system is None:
                self.start_rest()
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
                self.start_rest()
                return
            goal_cell = random.choice(list(adjacent_cells))
            start_gx, start_gy = critter_gx, critter_gy
            self.is_calculating = True
            self.path = pathfinding_system.find_path((start_gx, start_gy), goal_cell, world.grid)
            self.path_index = 0
            if self.path is None:
                self.start_rest()
                return

        # Follow the path
        if self.path is not None:
            self._follow_path(dt, world)
            
        # Check for arrival
        if self.path is None and not self.gathering:
             if self._is_adjacent_to_hut(critter_gx, critter_gy):
                self.gathering = True
                self.interaction_progress = 0.0
                self.active_target = self.assigned_hut
                return
             else:
                # If path finished but not adjacent, we might have been pushed
                # Clear path to trigger recalculation next tick
                self.path = None
                return

    def _update_follow(self, dt, world, pathfinding_system):
        """FOLLOW behavior: stay near the player using pathfinding."""
        if self.following_player is None:
            self.start_rest()
            return
        player = self.following_player
        self.follow_timer -= dt
        if self.follow_timer <= 0.0:
            self.follow_timer = self.follow_recalc_interval
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
                    if grid.is_within_bounds(gx, gy) and not grid.is_occupied(gx, gy) and dx*dx+dy*dy <= radius*radius:
                        candidates.append((gx, gy))
            self.follow_goal = random.choice(candidates) if candidates else None
            self.path = None
        if self.follow_goal is not None:
            if self.path is None:
                grid = world.grid
                start_gx, start_gy = grid.world_to_grid(self.x, self.y)
                self.path = pathfinding_system.find_path((start_gx, start_gy), self.follow_goal, grid)
                self.path_index = 0
                if self.path is None:
                    self.follow_goal = None
                    return
            self._follow_path(dt, world)
            if self.path is None:
                self.follow_goal = None


    def _perform_loiter_move(self, world):
        """Pick a nearby free cell (1-2 steps) and set loiter_target to its center; movement happens in _update_rest."""
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
        """Deposit held resources at the assigned hut and transition to REST, BREED, or FETCH."""
        from constants import ITEM_SAPLING
        from forester_hut import ForesterHut
        
        if self.inventory.items:
            # Check if building supports storage (e.g. GatheringHut has storage, MatingHut does not)
            is_forester = isinstance(self.assigned_hut, ForesterHut)
            
            if hasattr(self.assigned_hut, 'storage'):
                for resource_type, quantity in list(self.inventory.items.items()):
                    # Forester check: don't deposit saplings back into your own hut if you are a forester
                    if is_forester and resource_type == ITEM_SAPLING:
                        continue
                    self.assigned_hut.storage.add(resource_type, quantity)
                    self.inventory.remove(resource_type, quantity)
        
        # Determine next state based on hut type
        from mating_hut import MatingHut
        if isinstance(self.assigned_hut, ForesterHut):
            if self.inventory.get_item_count(ITEM_SAPLING) > 0:
                self.start_plant()
            elif self.assigned_hut.storage.get_item_count(ITEM_SAPLING) > 0:
                # Fetch 1 instantly since we are adjacent for deposit
                self.assigned_hut.storage.remove(ITEM_SAPLING, 1)
                self.inventory.add(ITEM_SAPLING, 1)
                self.start_plant()
            else:
                self.start_rest()
        elif isinstance(self.assigned_hut, MatingHut):
            self.start_breed()
        else:
            self.start_rest()

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
        if self.path is None:
            return
            
        if not self.path or self.path_index >= len(self.path):
            self.path = None
            self.path_index = 0
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
        
        # Consistent arrival threshold
        if dist < 1.0:
            # Reached this waypoint; advance to next
            self.path_index += 1
            if self.path_index >= len(self.path):
                self.path = None
                self.path_index = 0
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
                self.path_index = 0
        else:
            # Partial move
            self.x += (dx / dist) * move_dist
            self.y += (dy / dist) * move_dist

    def _has_reached_target(self, target_obj):
        """
        Check if critter is close enough to interact with the target object.
        Uses boundary-to-boundary distance for accuracy.
        """
        if target_obj is None:
            return False
        
        from utils import get_distance_to_boundary
        
        # If target has rectangular bounds
        if hasattr(target_obj, 'width') and hasattr(target_obj, 'height') and hasattr(target_obj, 'cell_size'):
            dist = get_distance_to_boundary(self, target_obj)
        else:
            # For point-like targets, fall back to center distance check
            if hasattr(target_obj, 'get_center'):
                tx, ty = target_obj.get_center()
            else:
                tx, ty = target_obj.x, target_obj.y
            dx = tx - self.x
            dy = ty - self.y
            import math
            dist = math.sqrt(dx*dx + dy*dy)
            
        return dist <= self.interaction_radius

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

    def _harvest_target(self, world):
        """Harvest resources from current target or apply work to obstacle."""
        target = self.target_resource
        from obstacle import Obstacle

        # Prefer using the target's interact method (handles Trees, Bushes, Rocks, Obstacles)
        if hasattr(target, 'interact'):
            target.interact(self)

            # 1. Check if target was removed (e.g., Tree chopped down)
            if target not in world.objects:
                self.target_resource = None
                self._continue_gathering_or_return(world)
                return

            # 2. Obstacle specific post-interaction logic
            if isinstance(target, Obstacle):
                if target.work_units <= 0:
                    self.target_resource = None
                self.start_rest()
                return

        # Fallback for objects without interact or for direct inventory check
        if not (hasattr(target, 'inventory') and target.inventory.items):
            self.target_resource = None
            self._continue_gathering_or_return(world)
            return

        # Check exit conditions: total capacity reached
        if self.inventory.get_total_quantity() >= self.carry_capacity:
            self.start_return()
            return

        # Otherwise, continue gathering (stay in GATHER, will harvest again next frame)
    def _continue_gathering_or_return(self, world):
        """After a resource is depleted, either find a new target if not full, or return to hut."""
        if self.inventory.get_total_quantity() < self.carry_capacity and self.assigned_hut is not None:
            new_target = self.assigned_hut.find_resource_in_radius(world, self)
            if new_target is not None:
                # Found a new target! Stay in GATHER, but reset gathering phase and path
                self.target_resource = new_target
                self.gathering = False
                self.path = None
                self.path_index = 0
                return

        # No new target found or already at capacity
        self.start_return()

    def get_render_offset(self):
        """Return (dx, dy) offset for animation based on state and current frame."""
        if self.state in (CritterState.GATHER, CritterState.RETURN):
            # Action: left/right wobble (1-pixel shift)
            return (-1, 0) if self.animation_frame == 0 else (1, 0)
        else:  # REST (and any others)
            return (0, -2) if self.animation_frame == 1 else (0, 0)



