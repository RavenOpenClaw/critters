"""
CraftingMenu: UI for selecting and crafting recipes.
"""
import pygame
from constants import CRAFTING_MENU_TITLE, CRAFT_MSG_NOT_ENOUGH, CRAFT_MSG_UNLOCKED, CRAFT_MSG_CRAFTED

class CraftingMenu:
    """Crafting menu overlay.

    Displays a list of recipes with required resources and handles crafting.
    """
    def __init__(self, recipes):
        self.recipes = recipes
        self.visible = False
        self.selected_index = 0  # For arrow-key navigation; optional
        self.last_message = ""  # Message to display after craft attempt
        self.message_timer = 0.0  # Time remaining to show message

    def toggle(self):
        """Toggle menu visibility and reset state when closing."""
        self.visible = not self.visible
        if not self.visible:
            self.selected_index = 0

    def handle_keypress(self, key):
        """Handle numeric keypresses (1-9) to craft the corresponding recipe.

        Args:
            key: pygame key constant (e.g., pygame.K_1). Should be called from main loop.

        Returns:
            A message string to display, or None.
        """
        if not self.visible:
            return None
        # Map K_1 through K_9 to indices 0-8
        number_keys = [
            pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
            pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9
        ]
        if key in number_keys:
            idx = number_keys.index(key)
            if idx < len(self.recipes):
                return idx  # Indicate that recipe at idx is selected for crafting
        return None

    def craft_selected(self, player, recipe):
        """Attempt to craft the given recipe.

        Checks resource costs, deducts resources if available, and unlocks equipment
        if the recipe requires it. Updates last_message with result.
        """
        # Verify costs
        for resource, required in recipe.cost.items():
            if not player.inventory.has(resource, required):
                self.last_message = CRAFT_MSG_NOT_ENOUGH.format(resource=resource)
                self.message_timer = 2.0  # Show for 2 seconds
                return False
        # Deduct resources
        for resource, required in recipe.cost.items():
            player.inventory.remove(resource, required)
        # Process result
        if recipe.unlocks_equipment:
            player.unlock_equipment(recipe.result)
            self.last_message = CRAFT_MSG_UNLOCKED.format(item=recipe.name)
        else:
            # For future: add item to inventory
            self.last_message = CRAFT_MSG_CRAFTED.format(item=recipe.name)
        self.message_timer = 2.0
        return True

    def update(self, dt):
        """Update message timer."""
        if self.message_timer > 0:
            self.message_timer -= dt
        else:
            self.last_message = ""

    def render(self, screen, font):
        """Render the crafting menu overlay."""
        if not self.visible:
            return
        x, y = 320, 70  # Position to the right of build menu
        overlay = pygame.Surface((300, 200))
        overlay.set_alpha(200)
        overlay.fill((255, 255, 255))
        screen.blit(overlay, (x, y))
        # Title
        title = font.render(CRAFTING_MENU_TITLE, True, (0, 0, 0))
        screen.blit(title, (x + 10, y + 10))
        # List recipes
        for idx, recipe in enumerate(self.recipes):
            prefix = " " if idx != self.selected_index else ">"
            line = f"{prefix}{idx+1}. {recipe.name} - {self._format_cost(recipe.cost)}"
            text = font.render(line, True, (0, 0, 0))
            screen.blit(text, (x + 20, y + 40 + idx * 20))
        # Message line if any
        if self.last_message:
            msg_surface = font.render(self.last_message, True, (0, 128, 0))
            screen.blit(msg_surface, (x + 10, y + 180))

    def _format_cost(self, cost):
        """Format cost dict as comma-separated resource:amount."""
        parts = [f"{res}:{amt}" for res, amt in cost.items()]
        return ", ".join(parts)
