"""
Build Menu system for selecting and placing buildings.
"""
import pygame
from gathering_hut import GatheringHut
from chair import Chair
from campfire import Campfire

class BuildMenu:
    """Simple build menu for selecting and placing buildings."""
    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.selected_building_class = None
        self.visible = False

    def toggle(self):
        """Toggle the build menu visibility."""
        self.visible = not self.visible
        if not self.visible:
            self.selected_building_class = None

    def select_gathering_hut(self):
        """Select the Gathering Hut building type."""
        self.selected_building_class = GatheringHut

    def select_chair(self):
        """Select the Chair building type."""
        self.selected_building_class = Chair

    def select_campfire(self):
        """Select the Campfire building type."""
        self.selected_building_class = Campfire

    def handle_keypress(self, key):
        """Handle keypresses for building selection when menu is open."""
        if not self.visible:
            return False
        if key == 'g':
            self.select_gathering_hut()
            return True
        if key == 'c':
            self.select_chair()
            return True
        if key == 'f':
            self.select_campfire()
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

    def render(self, screen, font):
        """Render the build menu overlay when visible."""
        if not self.visible:
            return
        # Simple overlay: list available buildings and selection status
        x, y = 10, 70  # below debug display
        # Draw a semi-transparent background for readability
        overlay = pygame.Surface((200, 150))
        overlay.set_alpha(200)
        overlay.fill((255, 255, 255))
        screen.blit(overlay, (x, y))
        # Title
        title = font.render("Build Menu (B to close)", True, (0, 0, 0))
        screen.blit(title, (x + 10, y + 10))
        # Options
        g_key = font.render("G: Gathering Hut", True, (0, 0, 0))
        screen.blit(g_key, (x + 20, y + 40))
        c_key = font.render("C: Chair", True, (0, 0, 0))
        screen.blit(c_key, (x + 20, y + 65))
        f_key = font.render("F: Campfire", True, (0, 0, 0))
        screen.blit(f_key, (x + 20, y + 90))
        # Selected indicator
        if self.selected_building_class is GatheringHut:
            sel = font.render("> Selected", True, (0, 128, 0))
            screen.blit(sel, (x + 120, y + 40))
        elif self.selected_building_class is Chair:
            sel = font.render("> Selected", True, (0, 128, 0))
            screen.blit(sel, (x + 120, y + 65))
        elif self.selected_building_class is Campfire:
            sel = font.render("> Selected", True, (0, 128, 0))
            screen.blit(sel, (x + 120, y + 90))
        # Instructions
        click_instr = font.render("Click grid to place", True, (80, 80, 80))
        screen.blit(click_instr, (x + 20, y + 120))
