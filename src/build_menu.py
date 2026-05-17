"""
Build Menu system for selecting and placing buildings.
"""
import pygame
from gathering_hut import GatheringHut
from chair import Chair
from campfire import Campfire
from mating_hut import MatingHut
from release_building import ReleaseBuilding
from lumber_mill import LumberMill
from forester_hut import ForesterHut
from sapling import Sapling
from constants import (
    HUD_BUILD_BUTTON,
    BUILD_MENU_TITLE,
    BUILD_PLACEMENT_INSTR,
    BUILDING_GATHERING_HUT,
    BUILDING_MATING_HUT,
    BUILDING_CHAIR,
    BUILDING_CAMPFIRE,
    BUILDING_LUMBER_MILL,
    BUILDING_FORESTER_HUT,
)

class BuildMenu:
    """Simple build menu for selecting and placing buildings with mouse/keyboard."""
    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.selected_building_class = None
        self.visible = False
        # Building options: tuple of (class, label)
        self.buildings = [
            (GatheringHut, BUILDING_GATHERING_HUT),
            (MatingHut, BUILDING_MATING_HUT),
            (LumberMill, BUILDING_LUMBER_MILL),
            (ForesterHut, BUILDING_FORESTER_HUT),
            (ReleaseBuilding, "Release Altar"),
            (Chair, BUILDING_CHAIR),
            (Campfire, BUILDING_CAMPFIRE),
            (Sapling, "Plant Sapling"),
        ]
        # Button rectangles for mouse interaction (computed in render)
        self.button_rects = {}  # maps building class to rect

        # Menu appearance
        self.menu_width = 320
        self.button_height = 45  # slightly taller for better spacing
        self.button_margin = 10
        self.header_height = 40
        self.footer_height = 40
        # Calculate height based on number of buildings
        self.menu_height = self.header_height + len(self.buildings) * (self.button_height + self.button_margin) + self.footer_height
        
        # Position (can be updated by UIManager)
        self.x, self.y = 10, 70

        self.bg_color = (255, 255, 255, 200)  # semi-transparent white
        self.button_color = (100, 100, 200)
        self.button_hover_color = (120, 120, 220)
        self.selected_color = (0, 128, 0)
        self.text_color = (0, 0, 0)
        self.cost_color = (80, 80, 80)  # darker gray for cost text

    def reposition(self, screen_width, screen_height):
        """Update position to stay anchored relative to the top-left area."""
        self.x, self.y = 10, 70

    def toggle(self):
        """Toggle the build menu visibility."""
        self.visible = not self.visible
        if not self.visible:
            self.selected_building_class = None

    def select_building(self, building_class):
        """Select a building type."""
        self.selected_building_class = building_class
        self.visible = True  # ensure menu stays visible when selecting

    def handle_mouse_click(self, pos):
        """
        Handle mouse click on the build menu.

        Args:
            pos: (x, y) mouse position.

        Returns:
            True if a building button was clicked, False otherwise.
        """
        if not self.visible:
            return False
        for building_class, rect in self.button_rects.items():
            if rect.collidepoint(pos):
                self.select_building(building_class)
                return True
        return False

    def handle_keypress(self, key):
        """Handle keypresses for building selection when menu is open."""
        if not self.visible:
            return False
        if key == 'g':
            self.select_building(GatheringHut)
            return True
        if key == 'c':
            self.select_building(Chair)
            return True
        if key == 'f':
            self.select_building(Campfire)
            return True
        if key == 'b':
            self.toggle()
            return True
        return False

    def attempt_placement(self, player, world, grid, mouse_grid_x, mouse_grid_y):
        """
        Attempt to place the selected building at the given grid coordinates.
        """
        if self.selected_building_class is None:
            return False

        # Custom Placement Constraint (Sapling)
        if hasattr(self.selected_building_class, 'can_place_at'):
            if not self.selected_building_class.can_place_at(world, mouse_grid_x, mouse_grid_y):
                world.set_message("Need empty surrounding space!", 2.0)
                return False

        # Create building instance at the grid position
        building = self.selected_building_class(
            mouse_grid_x,
            mouse_grid_y,
            cell_size=self.cell_size
        )

        # Check if player has resources
        from constants import BUILDING_RELEASE_ALTAR_COST
        # Standard cost check from class attr, but we also have centralized ones
        # For prototype, we'll favor the class 'cost' attr if present
        cost = getattr(self.selected_building_class, 'cost', {})
        
        # Override for Altar specifically as requested
        if self.selected_building_class == ReleaseBuilding:
            cost = BUILDING_RELEASE_ALTAR_COST

        if not building.can_place(player.inventory, cost_override=cost):
            return False

        # Pre-check occupancy
        for cell in building.get_occupied_cells():
            if grid.is_occupied(*cell):
                return False

        # Add building to world
        if not world.add_object(building):
            return False

        # Deduct resources
        for resource, amount in cost.items():
            player.inventory.remove(resource, amount)

        return True

    def render_ghost(self, screen, camera, grid, mouse_pos, player_inventory):
        """
        Render a semi-transparent ghost preview of the selected building at the
        current mouse position, snapped to the grid.

        Green = valid placement. Red = blocked or can't afford.
        """
        if not self.visible or self.selected_building_class is None:
            return

        # Convert mouse screen position → world → grid (snapped)
        mx, my = mouse_pos
        wx, wy = camera.undo(mx, my)
        gx, gy = grid.world_to_grid(wx, wy)

        # Instantiate a temporary building to get its dimensions and cost
        try:
            temp = self.selected_building_class(gx, gy, cell_size=self.cell_size)
        except Exception:
            return

        w_cells = temp.width
        h_cells = temp.height
        cs = self.cell_size

        # Determine validity — mirrors attempt_placement logic exactly
        valid = True

        # 1. Custom placement constraint (e.g. Sapling needs 8 empty neighbours)
        if hasattr(self.selected_building_class, 'can_place_at'):
            # We need a world reference; skip this check if unavailable
            pass  # checked below when we have world access

        # 2. Bounds check
        for i in range(w_cells):
            for j in range(h_cells):
                if not grid.is_within_bounds(gx + i, gy + j):
                    valid = False
                    break

        # 3. Occupancy check
        if valid:
            for i in range(w_cells):
                for j in range(h_cells):
                    if grid.is_occupied(gx + i, gy + j):
                        valid = False
                        break

        # 4. Affordability check
        if valid:
            from release_building import ReleaseBuilding
            from constants import BUILDING_RELEASE_ALTAR_COST
            cost = getattr(self.selected_building_class, 'cost', {})
            if self.selected_building_class == ReleaseBuilding:
                cost = BUILDING_RELEASE_ALTAR_COST
            if not temp.can_place(player_inventory, cost_override=cost):
                valid = False

        # Draw ghost rect in screen space
        sx, sy = camera.apply(gx * cs, gy * cs)
        ghost_rect = pygame.Rect(int(sx), int(sy), w_cells * cs, h_cells * cs)

        ghost = pygame.Surface((ghost_rect.width, ghost_rect.height), pygame.SRCALPHA)
        if valid:
            ghost.fill((0, 220, 0, 90))       # translucent green fill
            outline_color = (0, 180, 0)
        else:
            ghost.fill((220, 0, 0, 90))        # translucent red fill
            outline_color = (180, 0, 0)

        screen.blit(ghost, (ghost_rect.x, ghost_rect.y))
        pygame.draw.rect(screen, outline_color, ghost_rect, 2)

    def render(self, screen, font, hud_button_rect=None):
        """
        Render the build menu overlay when visible.
        """
        if not self.visible:
            return

        # Draw menu background
        x, y = self.x, self.y
        menu_rect = pygame.Rect(x, y, self.menu_width, self.menu_height)
        bg = pygame.Surface((self.menu_width, self.menu_height), pygame.SRCALPHA)
        bg.fill(self.bg_color)
        screen.blit(bg, (x, y))
        pygame.draw.rect(screen, (0, 0, 0), menu_rect, 2)

        # Title
        title = font.render(BUILD_MENU_TITLE, True, self.text_color)
        screen.blit(title, (x + 10, y + (self.header_height - title.get_height()) // 2))

        # Compute button rects for each building
        self.button_rects = {}
        btn_x = x + 20
        from release_building import ReleaseBuilding
        from constants import BUILDING_RELEASE_ALTAR_COST
        
        for idx, (building_class, label) in enumerate(self.buildings):
            btn_y = y + self.header_height + idx * (self.button_height + self.button_margin)
            rect = pygame.Rect(btn_x, btn_y, self.menu_width - 40, self.button_height)
            self.button_rects[building_class] = rect
            
            is_selected = (self.selected_building_class is building_class)
            mouse_over = rect.collidepoint(pygame.mouse.get_pos())
            color = self.selected_color if is_selected else (self.button_hover_color if mouse_over else self.button_color)
            pygame.draw.rect(screen, color, rect)
            
            lbl_surface = font.render(label, True, (255, 255, 255))
            lbl_rect = lbl_surface.get_rect(center=(rect.centerx, rect.centery - 10))
            screen.blit(lbl_surface, lbl_rect)
            
            # Cost
            cost_dict = getattr(building_class, 'cost', {})
            if building_class == ReleaseBuilding:
                cost_dict = BUILDING_RELEASE_ALTAR_COST
                
            if cost_dict:
                cost_parts = [f"{qty} {res}" for res, qty in cost_dict.items()]
                cost_str = "Cost: " + ", ".join(cost_parts)
            else:
                cost_str = "Free"
            cost_surface = font.render(cost_str, True, (240, 240, 240))
            cost_rect = cost_surface.get_rect(center=(rect.centerx, rect.centery + 10))
            screen.blit(cost_surface, cost_rect)

        # Instructions
        click_instr = font.render(BUILD_PLACEMENT_INSTR, True, (80, 80, 80))
        instr_y = y + self.menu_height - self.footer_height + (self.footer_height - click_instr.get_height()) // 2
        screen.blit(click_instr, (x + 20, instr_y))
