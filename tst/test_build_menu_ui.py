"""
Tests for BuildMenu UI dimensions and layout.
Ensures buttons and menu background are large enough for their content.
"""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

import pygame
pygame.init()

import unittest
from build_menu import BuildMenu
from constants import (
    BUILD_MENU_TITLE,
    BUILD_PLACEMENT_INSTR,
)

class TestBuildMenuUI(unittest.TestCase):
    def setUp(self):
        self.cell_size = 32
        self.build_menu = BuildMenu(self.cell_size)
        pygame.font.init()
        # Use a default font. Size 24 is what is used in the game's main loop usually.
        self.font = pygame.font.SysFont("Arial", 24)

    def test_menu_background_contains_all_buttons(self):
        """The menu background should be tall enough to contain all buttons."""
        # Render to populate button_rects
        screen = pygame.Surface((800, 600))
        self.build_menu.visible = True
        self.build_menu.render(screen, self.font)

        menu_top_y = 70 # Hardcoded in build_menu.py
        menu_height = self.build_menu.menu_height
        menu_bottom_y = menu_top_y + menu_height

        for building_class, rect in self.build_menu.button_rects.items():
            self.assertLessEqual(rect.bottom, menu_bottom_y, 
                                 f"Button for {building_class} extends beyond menu bottom")

    def test_menu_background_contains_instructions(self):
        """The menu background should be tall enough to contain the instruction text."""
        screen = pygame.Surface((800, 600))
        self.build_menu.visible = True
        self.build_menu.render(screen, self.font)

        menu_top_y = 70
        menu_height = self.build_menu.menu_height
        menu_bottom_y = menu_top_y + menu_height

        # The instruction text is rendered at y + self.menu_height - 30
        # Wait, if it's rendered at that position, it might be outside if menu_height is small?
        # Let's check where it SHOULD be.
        instr_y = menu_top_y + self.build_menu.menu_height - 30
        instr_surface = self.font.render(BUILD_PLACEMENT_INSTR, True, (0,0,0))
        instr_bottom = instr_y + instr_surface.get_height()

        self.assertLessEqual(instr_bottom, menu_bottom_y, 
                             "Instructions text extends beyond menu bottom")

    def test_buttons_wide_enough_for_labels(self):
        """Each button should be wide enough to fit its building label and cost text."""
        screen = pygame.Surface((800, 600))
        self.build_menu.visible = True
        self.build_menu.render(screen, self.font)

        for building_class, label in self.build_menu.buildings:
            rect = self.build_menu.button_rects[building_class]
            
            # Check label width
            lbl_surface = self.font.render(label, True, (255, 255, 255))
            self.assertLessEqual(lbl_surface.get_width(), rect.width - 10, 
                                 f"Label '{label}' is too wide for its button")

            # Check cost width
            cost_dict = getattr(building_class, 'cost', {})
            if cost_dict:
                cost_parts = [f"{qty} {res}" for res, qty in cost_dict.items()]
                cost_str = "Cost: " + ", ".join(cost_parts)
            else:
                cost_str = "Free"
            cost_surface = self.font.render(cost_str, True, (255, 255, 255))
            self.assertLessEqual(cost_surface.get_width(), rect.width - 10, 
                                 f"Cost text '{cost_str}' is too wide for its button")

if __name__ == '__main__':
    unittest.main()
