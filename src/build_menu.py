"""
Build Menu system for selecting and placing buildings.
"""
import pygame
from gathering_hut import GatheringHut
from chair import Chair
from campfire import Campfire
from mating_hut import MatingHut

class BuildMenu:
    """Simple build menu for selecting and placing buildings with mouse/keyboard."""
    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.selected_building_class = None
        self.visible = False
        # Building options: tuple of (class, label)
        self.buildings = [
            (GatheringHut, "Gathering Hut"),
            (MatingHut, "Mating Hut"),
            (Chair, "Chair"),
            (Campfire, "Campfire"),
        ]
        # Button rectangles for mouse interaction (computed in render)
        self.button_rects = {}  # maps building class to rect

        # Menu appearance
        self.menu_width = 200
        self.menu_height = 150
        self.button_height = 40  # taller to accommodate cost line
        self.button_margin = 10
        self.bg_color = (255, 255, 255, 200)  # semi-transparent white
        self.button_color = (100, 100, 200)
        self.button_hover_color = (120, 120, 220)
        self.selected_color = (0, 128, 0)
        self.text_color = (0, 0, 0)
        self.cost_color = (80, 80, 80)  # darker gray for cost text

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

        Args:
            player: Player instance with inventory
            world: World instance to add the building to
            grid: GridSystem for occupancy checks
            mouse_grid_x, mouse_grid_y: grid coordinates for placement

        Returns:
            True if placement succeeded, False otherwise.
        """
        if self.selected_building_class is None:
            return False

        # Create building instance at the grid position
        building = self.selected_building_class(
            mouse_grid_x,
            mouse_grid_y,
            cell_size=self.cell_size
        )

        # Check if player has resources
        if not building.can_place(player.inventory):
            return False

        # Pre-check occupancy: ensure all cells in the building footprint are unoccupied
        for cell in building.get_occupied_cells():
            if grid.is_occupied(*cell):
                return False

        # Add building to world (this registers it with the grid)
        try:
            world.add_object(building)
        except ValueError:
            # Overlap or invalid placement; do not deduct resources
            return False

        # Deduct resources only after successful placement
        for resource, amount in building.cost.items():
            player.inventory.remove(resource, amount)

        return True

    def render(self, screen, font, hud_button_rect=None):
        """
        Render the build menu overlay when visible, and optionally a HUD toggle button.

        Args:
            screen: Pygame surface to draw on.
            font: Pygame font for text.
            hud_button_rect: If provided, draw a small button in the HUD area to toggle menu.
        """
        # Draw HUD toggle button if requested
        if hud_button_rect:
            pygame.draw.rect(screen, self.button_color, hud_button_rect)
            btn_text = font.render("Build", True, (255, 255, 255))
            screen.blit(btn_text, btn_text.get_rect(center=hud_button_rect.center))

        if not self.visible:
            return

        # Draw menu background
        x, y = 10, 70  # below debug display
        menu_rect = pygame.Rect(x, y, self.menu_width, self.menu_height)
        # Create a transparent surface
        bg = pygame.Surface((self.menu_width, self.menu_height), pygame.SRCALPHA)
        bg.fill(self.bg_color)
        screen.blit(bg, (x, y))
        pygame.draw.rect(screen, (0, 0, 0), menu_rect, 2)

        # Title
        title = font.render("Build Menu (B to close)", True, self.text_color)
        screen.blit(title, (x + 10, y + 10))

        # Compute button rects for each building
        self.button_rects = {}
        btn_x = x + 20
        for idx, (building_class, label) in enumerate(self.buildings):
            btn_y = y + 40 + idx * (self.button_height + self.button_margin)
            rect = pygame.Rect(btn_x, btn_y, self.menu_width - 40, self.button_height)
            self.button_rects[building_class] = rect
            # Draw button with state
            is_selected = (self.selected_building_class is building_class)
            mouse_over = rect.collidepoint(pygame.mouse.get_pos())
            color = self.selected_color if is_selected else (self.button_hover_color if mouse_over else self.button_color)
            pygame.draw.rect(screen, color, rect)
            # Button label (top half)
            lbl_surface = font.render(label, True, (255, 255, 255))
            lbl_rect = lbl_surface.get_rect(center=(rect.centerx, rect.centery - 8))
            screen.blit(lbl_surface, lbl_rect)
            # Cost string (bottom half)
            cost_dict = getattr(building_class, 'cost', {})
            if cost_dict:
                cost_parts = [f"{qty} {res}" for res, qty in cost_dict.items()]
                cost_str = "Cost: " + ", ".join(cost_parts)
            else:
                cost_str = "Free"
            cost_surface = font.render(cost_str, True, self.cost_color)
            cost_rect = cost_surface.get_rect(center=(rect.centerx, rect.centery + 8))
            screen.blit(cost_surface, cost_rect)

        # Instructions
        click_instr = font.render("Click grid to place", True, (80, 80, 80))
        screen.blit(click_instr, (x + 20, y + self.menu_height - 30))
